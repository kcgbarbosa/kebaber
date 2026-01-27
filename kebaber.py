import os
import re
import sys
from typing import List, Tuple, Dict

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"

NO_COLOR = not sys.stdout.isatty() or os.getenv("NO_COLOR")

def c(text: str, *styles: str) -> str:
    if NO_COLOR:
        return text
    return "".join(styles) + text + Colors.RESET

# Input

def get_key() -> str:
    try:
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except (ImportError, termios.error):
        return input().strip()[:1]

# Naming

def to_kebab(name: str, smart: bool) -> str:
    base, ext = os.path.splitext(name)
    if smart:
        base = re.sub(r"([a-zA-Z])([0-9])", r"\1 \2", base)
        base = re.sub(r"([0-9])([a-zA-Z])", r"\1 \2", base)
        base = re.sub(r"([a-z])([A-Z])", r"\1 \2", base)
    base = base.lower()
    base = re.sub(r"[:./\\]", "-", base)
    base = re.sub(r"[\s_-]+", "-", base)
    base = re.sub(r"[^a-z0-9-]", "", base)
    base = base.strip("-") or "unnamed"
    return base + ext.lower()

SKIP = {"Recycle Bin", "__MACOSX"}
def get_files(folder: str) -> List[str]:
    return sorted(
        f for f in os.listdir(folder)
        if not f.startswith((".", "~")) and f not in SKIP
    )

def find_collisions(rows: List[Tuple[str, str]]) -> set:
    targets: Dict[str, List[str]] = {}
    for orig, new in rows:
        targets.setdefault(new, []).append(orig)
    return {t for t, srcs in targets.items() if len(srcs) > 1}

def apply_renames(folder: str, rows: List[Tuple[str, str]], collisions: set) -> int:
    renamed = 0
    for orig, new in rows:
        if orig == new or new in collisions:
            continue
        old_path = os.path.join(folder, orig)
        new_path = os.path.join(folder, new)
        if os.path.exists(new_path) and orig.lower() != new.lower():
            continue
        temp = new_path + ".tmp"
        os.rename(old_path, temp)
        os.rename(temp, new_path)
        renamed += 1
    return renamed

def clear():
    if not NO_COLOR:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

def show_controls(smart: bool, has_changes: bool):
    other = "Conservative" if smart else "Smart"
    print("\n" + c("─" * 60, Colors.DIM))
    print(f"\n  {c('[m]', Colors.CYAN)} {other} mode", end="")
    if has_changes:
        print(f"   {c('[a]', Colors.CYAN)} Apply", end="")
    print(f"   {c('[q]', Colors.DIM)} Quit\n")

def show_preview(folder: str, files: List[str], smart: bool) -> Tuple[List[Tuple[str, str]], set]:
    clear()
    mode = "Smart" if smart else "Conservative"
    rows = [(f, to_kebab(f, smart)) for f in files]
    changes = [(o, n) for o, n in rows if o != n]
    collisions = find_collisions(rows)

    print(c(f"\n  Kebab-case Renamer — {mode} Mode\n", Colors.BOLD, Colors.CYAN))
    print(f"  {c('Folder:', Colors.DIM)} {folder}")
    print(f"  {c('Files:', Colors.DIM)}  {len(files)}\n")
    print(c("─" * 60, Colors.DIM))

    if not changes:
        print(c("\n  No changes needed.\n", Colors.DIM))
    else:
        MAX_SHOW = 40
        print()
        for orig, new in changes:
            collision = new in collisions
            new_fmt = c(new, Colors.RED) if collision else c(new, Colors.GREEN)
            warn = c(" ⚠", Colors.RED) if collision else ""
            show_orig = orig if len(orig) <= MAX_SHOW else orig[:MAX_SHOW-1] + "…"
            print(f"  {show_orig:<{MAX_SHOW}}  {c('→', Colors.DIM)}  {new_fmt}{warn}")
        print(f"\n  {c(str(len(changes)), Colors.GREEN, Colors.BOLD)} to rename", end="")
        if collisions:
            print(c(f"  |  ⚠ {len(collisions)} collision(s) skipped", Colors.YELLOW))
        else:
            print()
    return rows, collisions

# Main loop

def main() -> int:
    if len(sys.argv) < 2:
        print(f"\n  {c('Usage:', Colors.BOLD)} {sys.argv[0]} <folder>\n")
        return 1
    folder = os.path.abspath(sys.argv[1])
    if not os.path.isdir(folder):
        print(c(f"\n  Error: not a directory\n", Colors.RED))
        return 1

    files = get_files(folder)
    if not files:
        print(c("\n  No files found.\n", Colors.DIM))
        return 0

    smart = False
    while True:
        rows, collisions = show_preview(folder, files, smart)
        changes = [(o, n) for o, n in rows if o != n]
        show_controls(smart, bool(changes))

        sys.stdout.write(f"  {c('>', Colors.CYAN)} ")
        sys.stdout.flush()
        key = get_key().lower()

        if key in ("\x03", "\x04", "q"):
            print("Quit\n")
            return 0
        if key == "m":
            smart = not smart
        if key == "a" and changes:
            print("Apply\n")
            sys.stdout.write(f"  Confirm? {c('[y/n]', Colors.DIM)} ")
            sys.stdout.flush()
            if get_key().lower() == "y":
                renamed = apply_renames(folder, rows, collisions)
                print(c(f"\n\n  ✓ Renamed {renamed} file(s)\n", Colors.GREEN))
                return 0
            print()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(c("\n\n  Interrupted.\n", Colors.YELLOW))
        sys.exit(130)