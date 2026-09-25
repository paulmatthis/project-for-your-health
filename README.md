<!-- vale Google.Headings = NO -->
# Project For Your Health
<!-- vale Google.Headings = YES -->

![Project For Your Health mascot](images/project-for-your-health.jpg)

A calorie/macro/spending tracker where you're allowed to be kinda sloppy and casual about it. Use text or audio to log food in the Code project on any device, plus add photographs of receipts, meals, and nutrition labels.

DO NOT log real data into this repo. This is a template.

## Requirements

- **Python 3.9+**, with `pip install -r requirements.txt` run once after cloning. Installs `openpyxl` to read and write the workbook.
- **LibreOffice**. Needed for the workbook's formulas via `openpyxl`. Without this, `app/recompute.py` still updates the raw data but skips recalculation.
- **A Chromium-based browser**: Google Chrome, Brave, Microsoft Edge, or Chromium to open Dashboard. Launcher scripts try each in that order. 
- **GitHub CLI (`gh`)**

### Create private repo from this template

1. **Create a private repo via Command Line or Web UI** 
   - **Command line**
     ```
     gh repo create my-tracker --private --template paulmatthis/project-for-your-health --clone
     cd my-tracker
     ```
   - **GitHub Web UI**. On this repo's page, click the green **"Use this template"** button, then **"Create a new repository."** Choose an owner and a name, and confirm the visibility is set to **Private**, then click Create. Then clone it:
     ```
     git clone <the-URL-github-gives-you> my-tracker
     cd my-tracker
     ```

   See "Not using GitHub" below for non-github options, then come back to step 2.

2. **Verify it's private.**
   ```
   gh repo view --json isPrivate
   ```
   This should print `{"isPrivate":true}`. On github.com, the repo name should show a **Private** badge next to it. If either check says public, fix it immediately, before going any further:
   ```
   gh repo edit --visibility private --accept-visibility-change-consequences
   ```

3. **Turn on the pre-push safety check** before you log anything:
   ```
   git config core.hooksPath .githooks
   ```
   This makes every future `git push` from this clone refuse to go through if this repo is public. See `.githooks/pre-push` for details.

4. **Open this folder as a project in Claude Code to begin the onboarding process.** 

### Not using GitHub?

If your git host isn't GitHub, or you'd rather not use the template feature, do the same thing by hand:

1. Clone this template:
   ```
   git clone https://github.com/paulmatthis/project-for-your-health.git my-tracker
   cd my-tracker
   ```
2. Disconnect it from this template's history and remote entirely, so there's no path back to a public repo:
   ```
   rm -rf .git
   git init
   git add -A
   git commit -m "Initial commit from Project For Your Health template"
   git branch -M main
   ```
3. Create a **new, private** repo of your own on whatever host you're using, then:
   ```
   git remote add origin <your-new-private-repo-url>
   git push -u origin main
   ```

Then continue from step 2 (verify) above.

### Preventing leaks

No process is perfect, but the following layers exist to try and protect your private information:

- **`.claude/hooks/session-start.sh`** checks the repo's real GitHub visibility at the start of every Claude Code session on this project and warns loudly if it isn't private. Only fires inside a Claude Code session.
- **`.githooks/pre-push`** (step 3 above) checks the same thing before any `git push`. This one's most important, since a push is the step that can't be undone. Fails open if `gh` isn't installed or isn't logged in, and can be skipped with `git push --no-verify`. 
- **`statements/*.pdf`** (raw bank/card statement uploads) and the LibreOffice recalculation step's temp files are gitignored. See `.gitignore` for details.
- Never paste your data somewhere public by hand, share your private repo's access with someone you shouldn't, or deliberately override the checks above with `--no-verify`. This template cannot account for everything. Just be safe.

## Structure and onboarding

"Project For Your Health" is the name of this template. THIS IS NOT YOUR TRACKER, it's just a template. Onboarding renames your instance, in the style "Project 200" or "Project Lose 30," based on your actual goal, and renames CLAUDE.md's title and the workbook file to match. This template file's title stays "Project For Your Health" either way.

## It's yours now

Once you've made your own private repo from this template, everything in it is yours to change. Ask Claude Code to add more onboarding, change the tone, add a feature, redesign the dashboard, swap the calorie formula, rename things, delete what you don't want, whatever. This template's own conventions (the hooks, the file layout, the TONE section in CLAUDE.md) are just a reasonable starting point. The only genuinely load-bearing pieces are the git sync hooks, the .py calculator, and the privacy checks above, and even those can be changed if you want to tinker.

## Setup

1. **Open this folder in a Claude Code project** after your own private repo is set up per installation steps. On the first message, Claude notices `profile-and-targets.md` says "ONBOARDING NOT COMPLETE" and walks through setup: picks a project name with you based on your actual goal and renames itself to match, asks a handful of questions (stats, goal, history, preferences, activity, which optional features you want to enable), then calculates your targets and saves everything. Opt-out behaviors go in an archive folder, so you can resurrect them later if you change your mind.

2. **After that, just send stuff.** A photo of a nutrition label, a text like "had two eggs and toast," a receipt from the grocery store, a screenshot or copy/paste of what you spent on a given night. Make sure you're always in the same Claude Code project, otherwise you'll need to manually copy over what you logged. When you send data from other devices besides your primary one (a mobile session, say) the spreadsheet will not update until you log back in on your primary device. Open the dashboard and any updates will then be synced against the local files and repo. 

## Optional behaviors

These are initially determined at onboarding, but you can turn them on or off at any time. 

- **Spending log**: lump-sum spending by category, from receipts, statements, or plaintext copy/paste.
- **Grocery purchases**: itemized grocery items help determine meal-plan and cost-per-macro advice.
- **Exercise log**: rep/weight tracking for resistance machine workouts (sets, reps, weight or assistance weight, machine).

Turning a feature off moves its files to `archive/`. Turning it back on later just moves it back.

## Updating from mobile or other machines

A hook pulls the latest logs at the start of every session, and another commits and pushes anything new after every response, not just when you end the conversation, retrying automatically if two devices sync at the same moment. Two devices logging around the same time get their entries combined automatically in the text logs to avoid a merge conflict. The workbook is a binary `.xlsx` file, so it can't merge the same way, see below for how that's handled instead. See "A Typical Day" below for exactly what syncs, when.

## A Typical Day

What actually syncs, when, without you having to think about it:

1. You send something (text, photo, whatever) to a Claude Code session, on any device. That session pulls the latest data before reading anything, logs your entry to the right .md file or files, then commits and pushes automatically once it finishes responding. Not when you "end" the session or close the app - after every single response. You never need to explicitly close a conversation for this to happen.
2. If that session is running on your primary device (see PRIMARY DEVICE in CLAUDE.md, the one your workbook lives on), the same after-every-response step also resyncs the workbook: if food-log.md or spending-log.md changed, it rewrites the matching tab and recalculates, automatically, before that response's commit goes out. Nothing has to remember to ask for it.
3. If that session is running anywhere else (phone, cloud, a laptop that isn't your primary device), it only ever touches the .md files, never the workbook. Your primary device catches those entries up the next time it's used (step 1 pulls them, then step 2 resyncs the workbook from them).
4. Opening the on-demand dashboard does its own pull-and-resync first, every time, before showing you anything - so what you see is never more than a few seconds stale, even if you haven't had a Claude Code session open in a while.
5. The one thing that stays manual: the Grocery Purchases tab. Its protein/calorie columns don't exist anywhere in grocery-purchases.md - only Claude's own judgment produces them - so no script can safely fill them in without risking overwriting a real estimate with a guess. A primary-device session backfills this tab by hand, same as before.

None of this depends on a session "remembering" to follow the rules, and it doesn't matter how long a session runs or how many turns it takes. The commit-and-push, and on the primary device the workbook resync, are enforced by a hook after every response - not by anyone (human or Claude) keeping track.

## The on-demand dashboard

Double-click the launcher for your platform in the project root: `Open Dashboard (Mac).command`, `Open Dashboard (Windows).bat`, or `Open Dashboard (Linux).desktop` (the Linux one needs a one-time path edit after cloning, see the comments inside it). It syncs the workbook, starts a local server, and opens the dashboard in its own isolated browser window so it never touches your regular browser profile). 

NOTE: Only the Mac path has actually been tested; the Windows and Linux ones were written and reviewed but not run on those platforms, see CLAUDE.md's app/ section for details.

### Launching it by hand

If the launcher for your platform doesn't work, you can probably ask Claude Code to troubleshoot and fix it for you in the same project. You can also do the same steps yourself from a CLI:

1. From the project root, sync the workbook first: `python3 app/recompute.py` (Windows: `python app/recompute.py`, or `py app/recompute.py` if `python` isn't found).
2. Start the server: `python3 app/server.py` (same `python`/`py` swap on Windows). Leave this terminal window open, it runs in the foreground until you stop it.
3. Open `http://localhost:8420/` in any browser. It doesn't need to be Chromium-based for this manual path, that requirement is only for the isolated app-mode window the launcher scripts try to open automatically - a normal browser tab works fine too, it just looks like a regular web page instead of its own little app window.

If port 8420 is already in use (usually a leftover server from a launcher that didn't clean up), find and stop it before starting a new one:
- Mac/Linux: `lsof -ti:8420` to get the process ID, then `kill <that number>`.
- Windows (PowerShell): `Get-NetTCPConnection -LocalPort 8420 | Select-Object OwningProcess`, then `Stop-Process -Id <that number>`.

## About the companion workbook

`tracker.xlsx` is the generic name for a live spreadsheet mirror of the logs used by Claude, with tabs that auto-calculate daily, weekly, and monthly summaries against your targets. It only ever gets edited from your primary device (whichever one you run Claude Code from most, for example a home computer). A phone/cloud session logs to the markdown files only. You have the option to set up an always-on remote instance if you want, just ask Claude Code how to do that. I didn't do it here because it felt like major overkill. 

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
