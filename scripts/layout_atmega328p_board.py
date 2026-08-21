import sys
from pathlib import Path

import pcbnew


BOARD_PATH = Path(
    r"C:\Users\georg\Documents\kicad_projects\atmega328p_tht_arduino_like_v2\atmega328p_tht_arduino_like_v2.kicad_pcb"
)


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def v(x: float, y: float):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def find_fp(board, ref: str):
    for candidate in board.GetFootprints():
        if candidate.GetReference() == ref:
            return candidate
    return None


def set_pos(board, ref: str, x: float, y: float, deg: float | None = None):
    if deg is not None and abs(deg % 360) > 0.001:
        print(f"Skipping {ref}; rotated footprints hang KiCad Python moves in this build", flush=True)
        return
    fp = find_fp(board, ref)
    if fp is None:
        raise RuntimeError(f"Missing footprint {ref}")
    target = v(x, y)
    current = fp.GetPosition()
    fp.Move(pcbnew.VECTOR2I(target.x - current.x, target.y - current.y))
    # Do not set orientation here. In this KiCad 10.0.5 Windows Python build,
    # both SetOrientationDegrees() and SetOrientation(EDA_ANGLE(...)) can hang
    # on some transferred footprints. Preserve the current rotations and only
    # perform deterministic placement.


def clear_edge_cuts(board):
    drawings = list(board.GetDrawings())
    for item in drawings:
        if item.GetLayer() == pcbnew.Edge_Cuts:
            board.Remove(item)


def add_edge_line(board, x1, y1, x2, y2):
    segment = pcbnew.PCB_SHAPE(board)
    segment.SetShape(pcbnew.SHAPE_T_SEGMENT)
    segment.SetLayer(pcbnew.Edge_Cuts)
    segment.SetStart(v(x1, y1))
    segment.SetEnd(v(x2, y2))
    segment.SetWidth(mm(0.1))
    board.Add(segment)


def add_board_rect(board, x, y, w, h):
    clear_edge_cuts(board)
    add_edge_line(board, x, y, x + w, y)
    add_edge_line(board, x + w, y, x + w, y + h)
    add_edge_line(board, x + w, y + h, x, y + h)
    add_edge_line(board, x, y + h, x, y)


def main():
    print(f"Loading {BOARD_PATH}", flush=True)
    board = pcbnew.LoadBoard(str(BOARD_PATH))

    # Elongated through-hole Arduino-like carrier.
    print("Updating board outline", flush=True)
    add_board_rect(board, 0, 0, 120, 80)

    # Main functional placement.
    placements = {
        # Left edge connectors / power entry
        # J1 barrel jack is already near the left edge. Moving it hangs this
        # KiCad Python build, so preserve its existing position.
        "J2": (12, 62, 90),
        # Power conversion block
        "D1": (26, 55, 0),
        "D2": (26, 35, 0),
        "U2": (34, 18, 90),
        "U3": (52, 18, 90),
        "JP1": (54, 34, 90),
        "C7": (22, 18, 90),
        "C5": (40, 34, 90),
        "C6": (58, 34, 90),
        # MCU core
        "U1": (62, 48, 90),
        "Y1": (62, 28, 0),
        "C2": (48, 39, 90),
        "C3": (76, 39, 90),
        "C4": (83, 49, 90),
        "R1": (43, 66, 0),
        "C1": (30, 70, 0),
        "SW1": (54, 72, 0),
        "J3": (82, 68, 0),
        # Indicators
        "R2": (36, 8, 0),
        "D3": (49, 8, 0),
        "R3": (68, 8, 0),
        "D4": (81, 8, 0),
        # Optional I2C pullups
        "R4": (84, 34, 90),
        "R5": (90, 34, 90),
        # User I/O headers at right edge
        "J4": (108, 25, 0),
        "J5": (86, 66, 0),
    }

    for ref, (x, y, deg) in placements.items():
        print(f"Placing {ref}", flush=True)
        set_pos(board, ref, x, y, deg)

    print("Saving board", flush=True)
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Placed {len(placements)} footprints on {BOARD_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
