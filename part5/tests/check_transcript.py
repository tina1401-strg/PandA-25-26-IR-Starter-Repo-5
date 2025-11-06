# Run without pytest: python -m part2.tests.check_transcript
import io, sys, builtins
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from part5 import app  # type: ignore

def run_with_inputs(inputs):
    it = iter(inputs)
    out = io.StringIO()
    def fake_input(prompt=""):
        print(prompt, end="", file=out)
        try:
            raw = next(it)
            print(raw, end="\n", file=out)
            return raw
        except StopIteration:
            raise EOFError
    old_stdout = sys.stdout
    old_input = builtins.input
    sys.stdout = out
    try:
        builtins.input = fake_input  # monkeypatch input
        app.main()
    finally:
        builtins.input = old_input
        sys.stdout = old_stdout
    return out.getvalue()

ESC = "\x1b"

def canonicalize_ansi(line: str) -> str:
    # Convert actual ESC to visible literal \x1b so snapshots can contain readable text
    return line.replace(ESC, "\\x1b")

def normalize_lines(s: str):
    """Normalize to a list of lines for robust, line-by-line comparison."""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return [canonicalize_ansi(line.rstrip()) for line in s.split("\n")]


def first_diff(exp_lines, got_lines):
    """Return the first differing index, or None if identical length & content.
    If only lengths differ, return the first index after the common prefix."""
    m = min(len(exp_lines), len(got_lines))
    for i in range(m):
        if exp_lines[i] != got_lines[i]:
            return i
    if len(exp_lines) != len(got_lines):
        return m
    return None


def print_context(exp_lines, got_lines, idx, context=2):
    start = max(0, idx - context)
    end = min(max(len(exp_lines), len(got_lines)), idx + context + 1)
    print("\nContext:")
    for i in range(start, end):
        mark = ">>" if i == idx else "  "
        exp = exp_lines[i] if i < len(exp_lines) else "<no line>"
        got = got_lines[i] if i < len(got_lines) else "<no line>"
        print(f"{mark} line {i+1}:")
        print(f"   EXPECTED: {exp!r}")
        print(f"   GOT     : {got!r}")


def main():
    inputs = ["love summer", "love war", ":search-mode OR", "love wire", ":search-mode NOT", ":quit"]

    got = run_with_inputs(inputs)
    got_lines = normalize_lines(got)

    snap_path = Path(__file__).with_name("snapshot_interaction.txt")
    expected = snap_path.read_text(encoding="utf-8")
    exp_lines = normalize_lines(expected)

    idx = first_diff(exp_lines, got_lines)

    if idx is None:
        print("OK: Transcript matches snapshot.")
        return

    # Mismatch details
    print("FAIL: Transcript does not match snapshot.")
    if idx < len(exp_lines) and idx < len(got_lines):
        print(f"\nFirst difference at line {idx+1}:")
        print(f"EXPECTED: {exp_lines[idx]!r}")
        print(f"GOT     : {got_lines[idx]!r}")
    elif idx >= len(exp_lines):
        print(f"\nOutput has EXTRA line at {idx+1}:")
        print(f"GOT     : {got_lines[idx]!r}")
    else:  # idx >= len(got_lines)
        print(f"\nOutput is MISSING line {idx+1}:")
        print(f"EXPECTED: {exp_lines[idx]!r}")

    print_context(exp_lines, got_lines, idx)


if __name__ == "__main__":
    main()