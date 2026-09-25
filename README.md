<!-- vale Google.Headings = NO -->
# Project For Your Health
<!-- vale Google.Headings = YES -->

![Project For Your Health mascot](images/project-for-your-health.jpg)

A calorie/macro/spending tracker where you're allowed to be kinda sloppy and casual about it. Use text or audio to log food in the Code project on any device, plus add photographs of receipts, meals, and nutrition labels.

## Before you start: create YOUR OWN private repo from this template

DO NOT log real data into this repo. Treat this template as read-only source material.

**DO NOT click GitHub's "Fork" button.** A fork of a public repo is public by default, and GitHub doesn't offer a free way to make a private fork - confirmed directly against GitHub's own API, which refuses to change that setting on anything but an org-owned private repo. Use the green **"Use this template"** button instead (a different button, further along the same row) or the equivalent steps below. Unlike a fork, it creates a completely separate repo with no shared git history and no relation to this one, and lets you choose Private right when you create it.

## Structure and onboarding

"Project For Your Health" is the name of this template. THIS IS NOT YOUR TRACKER, it's just a template. Onboarding (see Setup below) gives your instance its own name instead, in the style "Project 200" or "Project Lose 30," based on your actual goal, and renames CLAUDE.md's title and the workbook file to match. This template file's title stays "Project For Your Health" either way.

## Requirements

- **Git**, and a GitHub account (or any git host that offers private repos).
- **Python 3.9+**, with `pip install -r requirements.txt` run once after cloning (installs `openpyxl`, used to read and write the workbook).
- **A Chromium-based browser**: Google Chrome, Brave, Microsoft Edge, or Chromium. The on-demand dashboard opens in an isolated app-mode window (`--app` / `--user-data-dir`), a feature all four share; the launcher scripts try each in that order. Firefox and Safari don't support this mode and aren't detected.
- **LibreOffice**, free, any recent version. Needed for the workbook's formulas to actually recalculate. `openpyxl` (the Python library this project uses to read and write the .xlsx file) has no formula engine of its own, it only stores whatever value was last calculated. Without LibreOffice installed, `app/recompute.py` still updates the raw data, it just skips recalculating and says so.
- Recommended: **GitHub CLI (`gh`)**, installed and logged in (`gh auth login`). Without this, the privacy checks below still run, but they can only warn instead of actually confirming or blocking anything.


### Exact steps to get your own private copy

**Recommended: the GitHub CLI, one command.** This is GitHub's own "generate from template" feature, not a fork - it gives you a fresh repo with a single initial commit, no shared history, and no relation to this one:
```
gh repo create my-tracker --private --template paulmatthis/project-for-your-health --clone
cd my-tracker
```
Skip to step 4 (verify) below.

**Or, the same thing from the GitHub web UI:** on this repo's page, click the green **"Use this template"** button (not "Fork," a separate button further along the same row), then **"Create a new repository."** Choose an owner, a name, and confirm the visibility is set to **Private** right there on that page, before clicking Create. Then clone it:
```
git clone <the-URL-github-gives-you> my-tracker
cd my-tracker
```
Skip to step 4.

**Or, without GitHub's template feature** (any git host, not just GitHub):

1. Clone this template:
   ```
   git clone https://github.com/paulmatthis/project-for-your-health.git my-tracker
   cd my-tracker
   ```
2. Disconnect it from this template's history and remote entirely, so there's no path back to a public repo, ever:
   ```
   rm -rf .git
   git init
   git add -A
   git commit -m "Initial commit from Project For Your Health template"
   git branch -M main
   ```
3. Create a **new, private** repo of your own. Either:
   - With the GitHub CLI (`gh`), which won't let you skip the privacy flag by accident:
     ```
     gh repo create my-tracker --private --source=. --remote=origin --push
     ```
   - Or on github.com: click **New repository**, name it, and *before clicking Create*, confirm the visibility toggle says **Private**, not Public. Then:
     ```
     git remote add origin <the-URL-github-gives-you>
     git push -u origin main
     ```

4. **Verify it's actually private. Don't just trust the toggle you clicked.**
   ```
   gh repo view --json isPrivate
   ```
   This should print `{"isPrivate":true}`. On github.com, the repo name should show a **Private** badge next to it. If either check says public, fix it immediately, before going any further:
   ```
   gh repo edit --visibility private --accept-visibility-change-consequences
   ```
5. Turn on the pre-push safety check (one time, right now, before you log anything real):
   ```
   git config core.hooksPath .githooks
   ```
   This makes every future `git push` from this clone refuse to go through if this repo is ever public, checked fresh against GitHub each time rather than just trusted from setup. See `.githooks/pre-push` for exactly what it checks and its honest limits, it's a backstop, not a substitute for step 4.

Only after all five steps: open this folder in Claude Code and start onboarding (see Setup below).

### Preventing leaks

No process is perfect, but the following layers exist to try and protect your private information:

- **`.claude/hooks/session-start.sh`** checks the repo's real GitHub visibility at the start of every Claude Code session on this project and warns loudly if it isn't private. Only fires inside a Claude Code session.
- **`.githooks/pre-push`** (step 5 above) checks the same thing before any `git push`, from any terminal, Claude Code or not - this is the one that actually matters, since a push is the step that can't be undone. Fails open (warns, doesn't block) if `gh` isn't installed or isn't logged in, and can be skipped with `git push --no-verify` - no git hook is truly unbypassable. This raises the bar against an honest mistake, it doesn't remove the possibility of a deliberate override.
- **`statements/*.pdf`** (raw bank/card statement uploads) and the LibreOffice recalculation step's temp files are gitignored, never committed even to a private repo - see `.gitignore`.
- **None of this catches**: pasting your data somewhere unrelated and public by hand, sharing your private repo's access with someone you shouldn't, or deliberately overriding the checks above with `--no-verify`. Those are on you, the same as with any private notebook you could still choose to leave open on a table.

## It's yours now

Once you've made your own private repo from this template, everything in it is yours to change. Ask Claude Code to rewrite the onboarding questions, change the tone, add a feature, redesign the dashboard, swap the calorie formula, rename things, delete what you don't want, whatever you want. This template's own conventions (the hooks, the file layout, the TONE section in CLAUDE.md) are a reasonable starting point, not rules you're bound to. The only genuinely load-bearing pieces are the git sync hooks and the privacy checks above, and even those can be changed if you understand what you'd be giving up.

## Setup

1. **Open this folder in Claude Code** (desktop app, command-line tool, or a cloud session pointed at the repo) - only after your own private repo is set up per the steps above. On the first message, Claude notices `profile-and-targets.md` says "ONBOARDING NOT COMPLETE" and walks through setup: picks a project name with you based on your actual goal and renames itself to match, asks a handful of questions (stats, goal, history, preferences, activity, which optional features you want), then calculates your targets and saves everything. Opt-out behaviors go in an archive folder, so you can resurrect them if you change your mind later.

2. **After that, just send stuff.** A photo of a nutrition label, a text like "had two eggs and toast," a receipt from the grocery store, a screenshot or copy/paste of what you spent on a given night. Make sure you're always in the same Claude Code project, otherwise you'll need to manually copy over what you logged.

## Optional behaviors

These are initially determined at onboarding, but you can turn them on or off at any time. 

- **Spending log**: lump-sum spending by category, from receipts, statements, or plaintext copy/paste.
- **Grocery purchases**: itemized grocery items help determine meal-plan and cost-per-macro advice.
- **Exercise log**: rep/weight tracking for resistance machine workouts (sets, reps, weight or assistance weight, machine).

Turning a feature off moves its files to `archive/`. Turning it back on later just moves it back.

The companion spreadsheet (`tracker.xlsx`, see below) isn't on this list. It's included by default, same as the food log itself, not something you opt into.

## Updating from mobile or other machines

You never run git yourself. A hook pulls the latest logs at the start of every session, and another commits and pushes anything new at the end, retrying automatically if two devices sync at the same moment. Two devices logging around the same time get their entries combined automatically in the text logs, instead of a merge conflict. The one exception is the workbook, a binary file, so it can't merge the same way, see below for how that's handled instead.

## The on-demand dashboard

Double-click the launcher for your platform in the project root: `Open Dashboard (Mac).command`, `Open Dashboard (Windows).bat`, or `Open Dashboard (Linux).desktop` (the Linux one needs a one-time path edit after cloning, see the comments inside it). It syncs the workbook, starts a local server for just this session, opens the dashboard in its own isolated browser window (so it never touches your regular browser profile), and shuts everything back down the moment you close that window. Nothing runs in the background before or after. Only the Mac path has actually been tested; the Windows and Linux ones were written and reviewed but not run on those platforms, see CLAUDE.md's app/ section for specifics.

### Launching it by hand

If the launcher for your platform doesn't work, especially likely on Windows or Linux since only the Mac path has actually been run, do the same steps yourself from a terminal:

1. From the project root, sync the workbook first: `python3 app/recompute.py` (Windows: `python app/recompute.py`, or `py app/recompute.py` if `python` isn't found).
2. Start the server: `python3 app/server.py` (same `python`/`py` swap on Windows). Leave this terminal window open, it runs in the foreground until you stop it.
3. Open `http://localhost:8420/` in any browser. It doesn't need to be Chromium-based for this manual path, that requirement is only for the isolated app-mode window the launcher scripts try to open automatically - a normal browser tab works fine too, it just looks like a regular web page instead of its own little app window.
4. When you're done, go back to that terminal window and press Ctrl+C to stop the server.

If port 8420 is already in use (usually a leftover server from a launcher that didn't clean up), find and stop it before starting a new one:
- Mac/Linux: `lsof -ti:8420` to get the process ID, then `kill <that number>`.
- Windows (PowerShell): `Get-NetTCPConnection -LocalPort 8420 | Select-Object OwningProcess`, then `Stop-Process -Id <that number>`.

If Claude Code is running in the same project, you can also just ask it to launch or troubleshoot the dashboard for you instead of doing any of this by hand.

## About the companion workbook

`tracker.xlsx` is a live spreadsheet mirror of the logs used by Claude, with tabs that auto-calculate daily and weekly summaries against your targets. It only ever gets edited from your primary device (whichever one you run Claude Code from most, for example a home computer). A phone/cloud session logs to the markdown files only. 

Your primary device backfills the matching rows next time you run a session on it. This is because it's a binary file, and two devices editing it around the same time can't be merged the way the text logs can. See the workbook's own README tab for its tab structure and color key.

## Project map

- `CLAUDE.md` contains the instructions Claude follows for this project.
- `README.md` this file.
- `LICENSE` MIT license for the template code and scaffolding itself. Doesn't apply to whatever personal data you log once this is your own private repo, that's yours.
- `profile-and-targets.md` logs your stats, goal, and calculated targets. It's filled in by the onboarding Q&A, then updated with changes like reweigh, new activity level, etc.
- `welcome-message.md` is the message sent at the end of onboarding. Not otherwise used.
- `food-log.md`, `spending-log.md`, `grocery-purchases.md`, `exercise-log.md` the four logs. The last three are opt-in features, see Optional behaviors above.
- `<your-project-name>-tracker.xlsx` the companion workbook, see About the companion workbook below.
- `requirements.txt` lists the Python dependencies (`pip install -r requirements.txt`).
- `app/` the code behind automatic date handling, workbook syncing, and the on-demand dashboard - see CLAUDE.md's app/ entry for what each script does, and The on-demand dashboard above.
- `Open Dashboard (Mac).command`, `Open Dashboard (Windows).bat`, `Open Dashboard (Linux).desktop` double-click dashboard launchers, one per platform - see The on-demand dashboard above.
- `.claude/` settings and hook scripts for git sync, plus a few quality checks: an onboarding gate that blocks logging before setup finishes, a repo-privacy check, and Vale style/content linting (see `.vale.ini` and `.vale/`).
- `.githooks/pre-push` is the pre-push privacy check described above. Not active until you run `git config core.hooksPath .githooks` in your own clone.
- `images/` archived copies of every photo you send, plus this template's own mascot image, shown at the top of this file.
- `statements/` bank/card statement source material. The extracted text gets committed. A raw original file, if you send one, stays local only, never committed (see `.gitignore`).
- `reference/` standing reference material you provide for consistency, like a recurring product's label or a standard workout routine, not a dated log entry.
- `reports/` a saved copy of every dashboard or report Claude generates for you, as a standalone HTML file - a permanent home for it even after a published link expires. Doesn't exist until the first one gets saved.
- `archive/` contains files for any feature you've turned off. Doesn't exist until you turn one off.
