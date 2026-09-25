#!/usr/bin/env python3
"""
Parses food-log.md's and spending-log.md's structured table rows (never
a hand-written summary, which can go stale) and makes the workbook's
Food Log and Spending Log tabs an exact mirror of them. Daily Summary,
Weekly Rollup, and Monthly Rollup are formula-driven off those tabs
already, so once they're synced everything downstream recomputes itself
- no hand-written total, no arithmetic done by a person or an LLM.
Grocery Purchases is not covered here (it has protein/calorie columns
Claude estimates by hand, not present in grocery-purchases.md, so a
blind wipe-and-rewrite would destroy them) - still synced manually, see
CLAUDE.md's PRIMARY DEVICE section.

Usage: python3 app/recompute.py [--dry-run] [--no-commit]
"""

import argparse
import copy
import re
import subprocess
import sys
from pathlib import Path

import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FOOD_LOG = PROJECT_ROOT / "food-log.md"
SHEET_NAME = "Food Log"
SPENDING_LOG = PROJECT_ROOT / "spending-log.md"
SPENDING_SHEET_NAME = "Spending Log"


def _find_workbook() -> Path:
    """The one .xlsx file at the project root, discovered by extension
    rather than a hardcoded name - same approach the bash hooks already
    use (see .claude/hooks/session-start.sh), so this keeps working
    after onboarding renames the workbook (CLAUDE.md's FIRST RUN /
    ONBOARDING step 1) instead of silently pointing at a file that no
    longer exists."""
    matches = sorted(PROJECT_ROOT.glob("*.xlsx"))
    if not matches:
        raise FileNotFoundError(f"No .xlsx workbook found in {PROJECT_ROOT}")
    return matches[0]


WORKBOOK = _find_workbook()

ROW_RE = re.compile(
    r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|(.*)\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|"
    r"\s*(-?\d+)[^|]*\|\s*(-?\d+)\s*\|\s*(Yes|No)[^|]*\|(.*)\|\s*$"
)


def parse_food_log(path: Path):
    """Return a list of dicts, one per structured table row, in file order.
    Anything that isn't a table row (headers, separators, prose Notes
    blocks) is ignored - this is the whole point: the app never trusts a
    hand-written summary, only the raw rows."""
    rows = []
    skipped = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.startswith("|"):
            continue
        if line.startswith("| Date ") or line.startswith("|---"):
            continue
        m = ROW_RE.match(line)
        if not m:
            skipped.append((lineno, line))
            continue
        date, item, cal, protein, carbs, fat, alcohol_word, confidence = m.groups()
        rows.append(
            {
                "date": date,
                "item": item.strip(),
                "calories": int(cal),
                "protein": int(protein),
                "carbs": int(carbs),
                "fat": int(fat),
                "alcohol": line.split("|")[7].strip(),  # keep full text e.g. "No (0.0% ABV)"
                "confidence": confidence.strip(),
                "line": lineno,
            }
        )
    return rows, skipped


def sync_workbook(rows, dry_run=False):
    wb = openpyxl.load_workbook(WORKBOOK, data_only=False)
    ws = wb[SHEET_NAME]

    # Template formatting from an existing data row (row 2), so new rows
    # match the workbook's existing convention (blue text, number formats).
    template_fonts = {c: copy.copy(ws.cell(row=2, column=c).font) for c in range(1, 9)}
    template_formats = {c: ws.cell(row=2, column=c).number_format for c in range(1, 9)}

    # Wipe everything from row 2 down to the current last used row - data
    # rows AND any interspersed "Notes, ..." text rows. The workbook's job
    # is numbers; narrative notes live in food-log.md only from now on, so
    # they don't need hand-copying into the sheet (that copying was manual
    # busywork with no formula benefit, and another way for drift to creep
    # in).
    last_row = ws.max_row
    for r in range(2, last_row + 1):
        for c in range(1, 9):
            ws.cell(row=r, column=c).value = None

    for i, row in enumerate(rows, start=2):
        values = [
            row["date"],
            row["item"],
            row["calories"],
            row["protein"],
            row["carbs"],
            row["fat"],
            row["alcohol"],
            row["confidence"],
        ]
        for c, v in enumerate(values, start=1):
            cell = ws.cell(row=i, column=c)
            if c == 1:
                import datetime as _dt

                y, mo, d = (int(x) for x in v.split("-"))
                cell.value = _dt.datetime(y, mo, d)
            else:
                cell.value = v
            cell.font = template_fonts[c]
            cell.number_format = template_formats[c]

    if dry_run:
        print(f"[dry-run] would write {len(rows)} rows to '{SHEET_NAME}' (rows 2-{len(rows)+1})")
        return False

    wb.save(WORKBOOK)
    print(f"Synced {len(rows)} rows into '{SHEET_NAME}' (rows 2-{len(rows)+1}).")
    return True


SPENDING_ROW_RE = re.compile(
    r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|(.*)\|\s*(Groceries|Alcohol/Beer|Eating Out|Other)\s*\|"
    r"\s*\$?(-?[\d,]+\.\d{2})\s*\|(.*)\|\s*$"
)


def parse_spending_log(path: Path):
    """Same idea as parse_food_log: only the structured table rows count,
    never the prose "Source:" notes above them. Anchored on the Category
    column (one of the four fixed values) and the Amount column's $X.XX
    shape, same way food-log.md's row regex anchors on Calories/Confidence,
    so a comma or parenthetical in the Vendor or Notes text doesn't throw
    off which column is which."""
    if not path.exists():
        return [], []
    rows = []
    skipped = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.startswith("|"):
            continue
        if line.startswith("| Date ") or line.startswith("|---"):
            continue
        m = SPENDING_ROW_RE.match(line)
        if not m:
            skipped.append((lineno, line))
            continue
        date, vendor, category, amount, notes = m.groups()
        rows.append(
            {
                "date": date,
                "vendor": vendor.strip(),
                "category": category.strip(),
                "amount": float(amount.replace(",", "")),
                "notes": notes.strip(),
                "line": lineno,
            }
        )
    return rows, skipped


def sync_spending_workbook(rows, dry_run=False):
    """Mirrors sync_workbook() for the Spending Log tab. Unlike Grocery
    Purchases, every column here (Date, Vendor, Category, Amount, Notes)
    comes straight from spending-log.md with nothing added by hand in
    the workbook, so a full wipe-and-rewrite is safe - there's no
    Claude-estimated column here to lose the way Grocery Purchases has
    with its protein/calorie estimates (still manual, see CLAUDE.md)."""
    if not SPENDING_LOG.exists():
        return False

    wb = openpyxl.load_workbook(WORKBOOK, data_only=False)
    ws = wb[SPENDING_SHEET_NAME]

    template_fonts = {c: copy.copy(ws.cell(row=2, column=c).font) for c in range(1, 6)}
    template_formats = {c: ws.cell(row=2, column=c).number_format for c in range(1, 6)}

    last_row = ws.max_row
    for r in range(2, last_row + 1):
        for c in range(1, 6):
            ws.cell(row=r, column=c).value = None

    for i, row in enumerate(rows, start=2):
        values = [row["date"], row["vendor"], row["category"], row["amount"], row["notes"]]
        for c, v in enumerate(values, start=1):
            cell = ws.cell(row=i, column=c)
            if c == 1:
                import datetime as _dt

                y, mo, d = (int(x) for x in v.split("-"))
                cell.value = _dt.datetime(y, mo, d)
            else:
                cell.value = v
            cell.font = template_fonts[c]
            cell.number_format = template_formats[c]

    if dry_run:
        print(f"[dry-run] would write {len(rows)} rows to '{SPENDING_SHEET_NAME}' (rows 2-{len(rows)+1})")
        return False

    wb.save(WORKBOOK)
    print(f"Synced {len(rows)} rows into '{SPENDING_SHEET_NAME}' (rows 2-{len(rows)+1}).")
    return True


def sync_daily_summary_dates(rows, dry_run=False):
    """Fill in the Date column (A) on Daily Summary for any day that has
    Food Log rows but no date entered yet. The B-N formulas are pre-built
    ~220 days ahead and key off column A (IF(A<row>="","",...)), so a day
    with entries but no date here silently shows as blank/"No data
    logged" even though sync_workbook() already wrote its rows into the
    Food Log tab. Handled here automatically instead of relying on a
    person to remember to add the date by hand."""
    import datetime as _dt

    wb = openpyxl.load_workbook(WORKBOOK, data_only=False)
    ws = wb["Daily Summary"]

    anchor_row = 5
    anchor_date = ws.cell(row=anchor_row, column=1).value
    if not isinstance(anchor_date, _dt.datetime):
        print(
            f"WARNING: Daily Summary row {anchor_row} has no anchor date; "
            "skipping date sync.",
            file=sys.stderr,
        )
        return False

    template_font = copy.copy(ws.cell(row=anchor_row, column=1).font)
    template_format = ws.cell(row=anchor_row, column=1).number_format

    log_dates = sorted({row["date"] for row in rows})
    added = []
    for date_str in log_dates:
        y, mo, d = (int(x) for x in date_str.split("-"))
        target_date = _dt.datetime(y, mo, d)
        target_row = anchor_row + (target_date - anchor_date).days
        if target_row < anchor_row or target_row > ws.max_row:
            continue  # before the anchor or past the pre-built range
        cell = ws.cell(row=target_row, column=1)
        if cell.value is None:
            cell.value = target_date
            cell.font = template_font
            cell.number_format = template_format
            added.append(date_str)

    if not added:
        return False
    if dry_run:
        print(f"[dry-run] would add {len(added)} missing date(s) to Daily Summary: {', '.join(added)}")
        return False

    wb.save(WORKBOOK)
    print(f"Added {len(added)} missing date(s) to Daily Summary: {', '.join(added)}")
    return True


EXCEL_ERROR_STRINGS = ("#VALUE!", "#DIV/0!", "#REF!", "#NAME?", "#NULL!", "#NUM!", "#N/A")


def _find_soffice() -> str | None:
    """Cross-platform search for the LibreOffice binary: PATH first
    (covers a Linux package install, or anyone who put it on PATH
    themselves), then each OS's default install location. Deliberately
    self-contained - no dependency on any Claude-specific bundled
    tooling, so this works the same whether or not Claude Desktop
    happens to be installed on this machine."""
    import platform
    import shutil

    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found

    system = platform.system()
    if system == "Darwin":
        candidates = ["/Applications/LibreOffice.app/Contents/MacOS/soffice"]
    elif system == "Windows":
        candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
    else:
        candidates = ["/usr/bin/soffice", "/usr/local/bin/soffice", "/opt/libreoffice/program/soffice"]

    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def recalc():
    """openpyxl has no formula engine - it only reads and writes each
    cell's last-cached value, so without this step nothing here would
    ever actually recalculate. Forces LibreOffice to open the workbook
    headless, recalculate it (the default behavior of --convert-to,
    since AutoCalculate is on by default), and hand back a fresh copy,
    which replaces the original in place."""
    import shutil
    import tempfile

    soffice = _find_soffice()
    if not soffice:
        print(
            "Could not find a LibreOffice (soffice) binary on PATH or in the "
            "usual per-OS install locations. Install LibreOffice to get "
            "automatic formula recalculation - see README.md. Skipping "
            "recalculation for now; the workbook's formulas will show stale "
            "cached values until it's opened and recalculated by hand.",
            file=sys.stderr,
        )
        return None

    with tempfile.TemporaryDirectory() as outdir:
        result = subprocess.run(
            [soffice, "--headless", "--norestore", "--convert-to", "xlsx", "--outdir", outdir, str(WORKBOOK)],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if result.returncode != 0:
            print(f"LibreOffice failed to recalculate: {result.stderr.strip()}", file=sys.stderr)
            return result

        converted = Path(outdir) / WORKBOOK.name
        if not converted.exists():
            print(
                "LibreOffice exited cleanly but produced no output file, so nothing "
                "was recalculated. Check that no other LibreOffice instance is "
                "running, then retry.",
                file=sys.stderr,
            )
            return result

        shutil.copyfile(converted, WORKBOOK)

    errors = []
    wb = openpyxl.load_workbook(WORKBOOK, data_only=True)
    for sheet_name in wb.sheetnames:
        for row in wb[sheet_name].iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value in EXCEL_ERROR_STRINGS:
                    errors.append(f"{sheet_name}!{cell.coordinate}: {cell.value}")
    wb.close()

    if errors:
        print(f"Recalculated with {len(errors)} formula error(s):", file=sys.stderr)
        for e in errors[:20]:
            print(f"  {e}", file=sys.stderr)
    else:
        print("Recalculated, no formula errors found.")
    return {"status": "errors_found" if errors else "success", "total_errors": len(errors)}


def git_commit_and_push(message: str):
    # Scoped to WORKBOOK specifically (both the diff check and the commit
    # itself) so this never sweeps up an unrelated change that happens to
    # be staged elsewhere in the tree at the same time this script runs.
    subprocess.run(["git", "add", str(WORKBOOK)], cwd=PROJECT_ROOT, check=True)
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", str(WORKBOOK)], cwd=PROJECT_ROOT
    )
    if diff.returncode == 0:
        print("No changes to commit.")
        return
    subprocess.run(["git", "commit", "-m", message, "--", str(WORKBOOK)], cwd=PROJECT_ROOT, check=True)

    push = subprocess.run(["git", "push"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    if push.returncode != 0:
        print("Push rejected, pulling and retrying once...", file=sys.stderr)
        pull = subprocess.run(
            ["git", "pull", "--rebase"], cwd=PROJECT_ROOT, capture_output=True, text=True
        )
        if pull.returncode != 0:
            print(f"git pull --rebase failed:\n{pull.stderr}", file=sys.stderr)
            print(
                "Could not auto-resolve. Stopping here rather than guessing - "
                "check the working tree by hand.",
                file=sys.stderr,
            )
            sys.exit(1)
        retry = subprocess.run(["git", "push"], cwd=PROJECT_ROOT, capture_output=True, text=True)
        if retry.returncode != 0:
            print(f"Push still failing after retry:\n{retry.stderr}", file=sys.stderr)
            sys.exit(1)
    print("Committed and pushed.")


def print_summary(rows):
    from collections import defaultdict

    by_date = defaultdict(lambda: {"calories": 0, "protein": 0, "carbs": 0, "fat": 0})
    for row in rows:
        d = by_date[row["date"]]
        d["calories"] += row["calories"]
        d["protein"] += row["protein"]
        d["carbs"] += row["carbs"]
        d["fat"] += row["fat"]
    if not rows:
        return
    last_date = rows[-1]["date"]
    t = by_date[last_date]
    print(
        f"Latest day in food-log.md ({last_date}): "
        f"{t['calories']} kcal, {t['protein']}g protein, {t['carbs']}g carb, {t['fat']}g fat."
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-commit", action="store_true")
    args = parser.parse_args()

    rows, skipped = parse_food_log(FOOD_LOG)
    if skipped:
        print(f"WARNING: {len(skipped)} table-looking line(s) failed to parse:", file=sys.stderr)
        for lineno, line in skipped:
            print(f"  line {lineno}: {line}", file=sys.stderr)

    print_summary(rows)
    changed = sync_workbook(rows, dry_run=args.dry_run)
    dates_changed = sync_daily_summary_dates(rows, dry_run=args.dry_run)

    spending_rows, spending_skipped = parse_spending_log(SPENDING_LOG)
    if spending_skipped:
        print(f"WARNING: {len(spending_skipped)} spending-log.md table-looking line(s) failed to parse:", file=sys.stderr)
        for lineno, line in spending_skipped:
            print(f"  line {lineno}: {line}", file=sys.stderr)
    spending_changed = sync_spending_workbook(spending_rows, dry_run=args.dry_run)

    if args.dry_run:
        return
    if changed or dates_changed or spending_changed:
        recalc()
        if not args.no_commit:
            parts = []
            if changed:
                parts.append(f"Food Log ({len(rows)} rows)")
            if spending_changed:
                parts.append(f"Spending Log ({len(spending_rows)} rows)")
            summary = ", ".join(parts) if parts else "Daily Summary dates"
            git_commit_and_push(f"auto: sync {summary} from .md source")


if __name__ == "__main__":
    main()
