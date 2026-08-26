# KiCad/JLCPCB Database Discovery Research

Research date: 2026-08-13

## Executive conclusion

KiCad does **not** expose an IPC/API call that locates the Bouni `kicad-jlcpcb-tools` parts database or discovers that project's current download URL. KiCad knows its own configured package roots and provides an API-created persistent settings directory for a plugin, but a third-party plugin's private database path and remote feed are outside KiCad's public IPC model.

Konnect should therefore treat local database discovery and upstream catalog discovery as two separate concerns:

1. Prefer an explicitly configured database path.
2. When launched by the in-process KiCad Python plugin, discover Bouni's installed plugin and its configured data directory, then pass the resolved database path to the Rust server.
3. For Konnect-managed downloads, replace the dead monolithic URL with a versioned provider manifest and a transactional downloader for Bouni's current chunk protocol.
4. Add an importer/query adapter: Bouni's current database schema is **not** a drop-in match for the schema Konnect currently queries.

## What issue #97 identifies

[Konnect issue #97](https://github.com/mixelpixx/Konnect/issues/97) correctly identifies that Konnect's hardcoded `https://bouni.github.io/kicad-jlcpcb-tools/jlcpcb_parts.db` endpoint returns HTTP 404. The corresponding Konnect implementation hardcodes that URL and writes its response directly to `jlcpcb.db`; path selection is `output_path`, then `jlcpcb_db_path`, then a Konnect-owned user cache path. [Konnect path resolution](https://github.com/mixelpixx/Konnect/blob/5cd6454969d2d060ff8c65b480651a4341051eed/crates/konnect-core/src/tools/integration.rs#L150-L173), [hardcoded downloader](https://github.com/mixelpixx/Konnect/blob/5cd6454969d2d060ff8c65b480651a4341051eed/crates/konnect-core/src/tools/integration.rs#L245-L281)

The immediate problem is larger than a renamed file. Bouni's current distributor publishes several databases as split ZIP chunks, while Konnect expects a monolithic SQLite response.

## What KiCad can and cannot locate

### KiCad-owned paths

KiCad defines `KICAD10_3RD_PARTY` as the location for packages installed by the Plugin and Content Manager (PCM). KiCad also warns that values set in **Configure Paths** are internal settings, stored in KiCad's user configuration, and are not necessarily visible as operating-system environment variables. [KiCad paths documentation](https://docs.kicad.org/master/en/kicad/kicad.html#paths-and-libraries-configuration)

Internally, PCM installs package content below its effective third-party root. It changes dots in a package identifier to underscores and maps archive content from `<PackageRoot>/$folder/$contents` to `$KICAD*_3RD_PARTY/$folder/$package_id/$contents`. [KiCad PCM extraction source](https://docs.kicad.org/doxygen/pcm__task__manager_8cpp_source.html#l00254) The valid top-level package folders include `plugins`, `footprints`, `3dmodels`, `symbols`, `resources`, `colors`, `templates`, and `scripts`. [KiCad PCM directory source](https://docs.kicad.org/doxygen/pcm_8h_source.html#l00041)

PCM tracks installed packages in `<user_settings>/installed_packages.json`, and keeps repository caches below `$KICAD*_3RD_PARTY/cache`. [KiCad PCM class documentation](https://docs.kicad.org/doxygen/classPLUGIN__CONTENT__MANAGER.html#details)

These are KiCad package-management locations. They do not describe where an arbitrary plugin stores a runtime-generated database, nor do they advertise that plugin's upstream data feed.

### Public IPC API

The official `kicad-python` API offers `get_plugin_settings_path(identifier)`, but its documented purpose is a writable persistent configuration directory that survives plugin uninstall or upgrade. [Official `KiCad` API](https://docs.kicad.org/kicad-python-main/kicad.html#kipy.kicad.KiCad.get_plugin_settings_path)

KiCad's implementation constructs that result as:

```text
<KiCad user settings>/plugins/<identifier>
```

It does not return the PCM installation/resources directory. [KiCad IPC handler source](https://docs.kicad.org/doxygen/api__handler__common_8cpp_source.html#l00303)

The IPC plugin-launch environment documents `KICAD_API_SOCKET` and `KICAD_API_TOKEN`; it does not define a third-party package-root or catalog-discovery variable. [Official add-on developer documentation](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/#connecting-to-kicad)

`Project.expand_text_variables()` is not an indirect solution for `${KICAD10_3RD_PARTY}`. Its handler calls the project text-variable resolver, whose implementation resolves project variables and built-ins such as `PROJECTNAME` and dates, rather than KiCad path/environment variables. [IPC expansion handler](https://docs.kicad.org/doxygen/api__handler__common_8cpp_source.html#l00279), [project resolver source](https://docs.kicad.org/doxygen/project_8cpp_source.html#l00081)

**Finding:** no reviewed public KiCad IPC method lists PCM packages, returns the effective `KICAD<n>_3RD_PARTY` value, locates another plugin's private data, or discovers its remote database URL.

### In-process legacy Python option

Konnect's action plugin already runs inside `pcbnew` and starts the Rust server as a child process. [Konnect action plugin](https://github.com/mixelpixx/Konnect/blob/5cd6454969d2d060ff8c65b480651a4341051eed/plugin/__init__.py) That makes the in-process Python layer the most practical place to inspect KiCad's Python plugin search roots and pass a resolved path to Rust. KiCad's legacy SWIG bindings also expose `SETTINGS_MANAGER.GetUserSettingsPath()`. [KiCad 10 SWIG reference](https://docs.kicad.org/doxygen-python-10.0/classpcbnew_1_1SETTINGS__MANAGER.html#a28c955de581223bbd6153822b10f5464)

This is a pragmatic bridge, not a portable IPC contract. Konnect must retain explicit configuration and standalone fallback behavior.

## How Bouni's plugin currently resolves and downloads its database

Bouni's current plugin first reads its own `library.data_path` setting. If unset, it uses a `jlcpcb` directory below the installed plugin directory. It then combines that directory with the selected library's configured filename. [Bouni local-path implementation](https://github.com/Bouni/kicad-jlcpcb-tools/blob/fa758809e0438ec316e474deb8506257a9fee310/library.py#L71-L91)

The available variants are:

| Selection | SQLite filename | Chunk-count sentinel |
|---|---|---|
| Basic + preferred | `basic-parts-fts5.db` | `chunk_num_basic_parts_fts5.txt` |
| All parts | `parts-fts5.db` | `chunk_num_fts5.txt` |
| Current parts (default) | `current-parts-fts5.db` | `chunk_num_current_parts_fts5.txt` |

These names and the `current-parts` default are defined in [Bouni's database configuration](https://github.com/Bouni/kicad-jlcpcb-tools/blob/fa758809e0438ec316e474deb8506257a9fee310/dblib/__init__.py#L21-L81).

The plugin's downloader uses `https://bouni.github.io/kicad-jlcpcb-tools/`, fetches the selected variant's chunk-count sentinel, then downloads numbered files such as `current-parts-fts5.db.zip.001`. It checks the size of resumable chunks before reuse. [Bouni downloader implementation](https://github.com/Bouni/kicad-jlcpcb-tools/blob/fa758809e0438ec316e474deb8506257a9fee310/library.py#L538-L675)

Bouni's scheduled GitHub Actions workflow updates the data daily, creates an archive, and deploys that archive to GitHub Pages. [Bouni database workflow](https://github.com/Bouni/kicad-jlcpcb-tools/blob/fa758809e0438ec316e474deb8506257a9fee310/.github/workflows/update_parts_database.yml)

KiCad's PCM metadata cannot discover this feed. Bouni's PCM package manifest identifies `com.github.bouni.kicad-jlcpcb-tools` and its install archive, but does not declare the runtime database source. [Bouni PCM packages manifest](https://raw.githubusercontent.com/Bouni/bouni-kicad-repository/main/packages.json)

## Schema incompatibility that must be addressed

Konnect currently queries a `components` table with identifier-style columns including `LCSC`, `MFR_Part`, `Library_Type`, and `Category`. [Konnect query implementation](https://github.com/mixelpixx/Konnect/blob/5cd6454969d2d060ff8c65b480651a4341051eed/crates/konnect-core/src/tools/integration.rs#L334-L352)

Bouni's current generated database instead defines an FTS5 virtual table named `parts`, with columns including `LCSC Part`, `First Category`, `Second Category`, `MFR.Part`, `Library Type`, `Description`, `Price`, and `Stock`; it also creates `meta`, `mapping`, and `categories` tables. [Bouni schema source](https://github.com/Bouni/kicad-jlcpcb-tools/blob/fa758809e0438ec316e474deb8506257a9fee310/common/partsdb.py#L33-L72)

Therefore simply changing the download URL will still leave `search_jlcpcb_parts` broken. The fix needs either:

- a query adapter for the Bouni `parts` schema; or
- an import step that converts Bouni's schema into a stable Konnect-owned schema.

The second option gives Konnect a cleaner compatibility boundary. In either case, open the source database read-only and validate required tables/columns before accepting it.

## Recommended dynamic design

### 1. Local database resolver

Use this precedence:

1. Tool argument / explicit `jlcpcb_db_path`.
2. Bouni database discovered by the in-process KiCad launcher.
3. Last known-good Konnect-owned cache.
4. Download/update only when requested or no usable local database exists.

The KiCad launcher can inspect plugin search roots, identify Bouni's directory by package marker files rather than a single absolute pathname, read its `settings.json`, honor `library.data_path` and `selected_library`, and then pass the candidate path to the Rust child through an explicit argument or narrowly named environment variable. Validate the SQLite schema rather than trusting a folder name. This accommodates PCM root changes, manual plugin installs, user overrides, and Bouni's selectable database variants.

### 2. Versioned upstream provider manifest

Do not embed another guessed artifact URL in Rust. Define a small, versioned Konnect provider manifest containing:

- provider and manifest-schema versions;
- ordered base URLs/mirrors;
- database variants;
- chunk-count sentinel and chunk filename pattern;
- supported source schema and required tables/columns;
- optional expected SHA-256 hashes and publication timestamp.

Ship a bundled manifest as an offline fallback and allow a configured manifest/source override. A remotely refreshable Konnect-controlled copy can repair an upstream move without requiring a new binary release. No discovery mechanism can survive every host/repository relocation, so explicit override plus a last-known-good database remain necessary.

### 3. Transactional download/import

For the current Bouni provider:

1. Fetch and strictly parse the chunk-count sentinel.
2. Download all numbered chunks to a temporary directory with bounded size/count limits.
3. Verify HTTP status, sizes, and hashes when available.
4. Reassemble and extract without writing outside the temporary directory.
5. Open SQLite read-only; verify `PRAGMA integrity_check`, expected schema, and basic metadata.
6. Import/adapt into Konnect's stable schema.
7. Atomically replace the active database only after all checks succeed.
8. Preserve and continue using the previous database on 404, timeout, corrupt archive, or schema mismatch.

Return diagnostics including provider, resolved local path, selected variant, source URL, database age, detected schema, and whether fallback data was used.

### 4. Do not make JLC's web endpoint the client fallback

Bouni's builder currently obtains component data through JLCPCB's shopping-cart web endpoint and an XSRF-token flow. [Bouni JLC API client](https://github.com/Bouni/kicad-jlcpcb-tools/blob/fa758809e0438ec316e474deb8506257a9fee310/common/jlcapi.py#L30-L77) That source demonstrates how Bouni builds its catalog, but it is not evidence of a documented, stable public JLCPCB API contract. Rebuilding the entire catalog in each Konnect client would also be expensive. Keep that activity in an upstream/build pipeline rather than using it as the normal runtime recovery path.

## Suggested implementation order

1. Add schema detection and a Bouni `parts` query/import adapter.
2. Add local Bouni database discovery to the KiCad Python launcher and pass the result to Rust.
3. Implement the current chunked Bouni provider with temporary files, validation, and atomic activation.
4. Add the versioned provider manifest, overrides, mirrors, and last-known-good diagnostics.
5. Add fixtures/tests for missing plugins, custom `data_path`, each database variant, partial chunks, bad ZIP/SQLite input, schema drift, and upstream 404.

## Direct answer

There is no KiCad API call that asks, “where is the JLCPCB database?” KiCad's public API can return a plugin-specific persistent settings path, but that is not Bouni's installed plugin directory or database feed. The resilient solution is to let Konnect's in-process KiCad launcher discover an installed local Bouni database when available, while making remote acquisition an independently configured, manifest-driven provider with schema adaptation and a last-known-good fallback.
