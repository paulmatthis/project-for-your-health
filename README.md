<!-- vale Google.Headings = NO -->
# Project For Your Health
<!-- vale Google.Headings = YES -->

![Project For Your Health mascot](images/project-for-your-health.jpg)

A calorie/macro/spending tracker where you're allowed to be kinda sloppy and casual about it. Use text or audio to log food in the Code project on any device, plus add photographs of receipts, meals, and nutrition labels.

"Project For Your Health" is the name of this template, not your own tracker. Onboarding (step 2 below) gives your instance its own name instead, in the style "Project 200" or "Project Lose 30," based on your actual goal, and renames CLAUDE.md's title and the workbook file to match. That's the name Claude and the hooks use day to day. This file's own title stays "Project For Your Health" either way, it names the template, not your instance.

## Setup

1. **Make this its own private git repo.** The log ends up containing photos of nutrition labels, receipts, and possibly bank statements or other sensitive information, so it should never be public.
   ```
   cd <your-project-folder>
   git init
   git add -A
   git commit -m "Initial tracker setup"
   ```
   Then create a **private** repo on GitHub (or wherever) and push:
   ```
   git remote add origin <your-private-repo-url>
   git branch -M main
   git push -u origin main
   ```

2. **Open this folder in Claude Code** (desktop app, command-line tool, or a cloud session pointed at the repo). On the first message, Claude notices `profile-and-targets.md` says "ONBOARDING NOT COMPLETE" and walks through setup: picks a project name with you based on your actual goal and renames itself to match, asks a handful of questions (stats, goal, history, preferences, activity, which optional features you want), then calculates your targets and saves everything. Opt-out behaviors go in an archive folder, so you can resurrect them if you change your mind later.

3. **After that, just send stuff.** A photo of a nutrition label, a text like "had two eggs and toast," a receipt from the grocery store, a screenshot or copy/paste of what you spent on a given night. Make sure you're always in the same Claude Code project, otherwise you'll need to manually copy over what you logged. 

## Optional behaviors

These are initially determined at onboarding, but you can turn them on or off at any time. 

- **Spending log**: lump-sum spending by category, from receipts, statements, or plaintext copy/paste.
- **Grocery purchases**: itemized grocery items help determine meal-plan and cost-per-macro advice.
- **Exercise log**: rep/weight tracking for resistance machine workouts (sets, reps, weight or assistance weight, machine).

Turning a feature off moves its files to `archive/`. Turning it back on later just moves it back.

The companion spreadsheet (`tracker.xlsx`, see below) isn't on this list. It's included by default, same as the food log itself, not something you opt into.

## Updating from mobile or other machines

You never run git yourself. A hook pulls the latest logs at the start of every session, and another commits and pushes anything new at the end, retrying automatically if two devices sync at the same moment. Two devices logging around the same time get their entries combined automatically in the text logs, instead of a merge conflict. The one exception is the workbook, a binary file, so it can't merge the same way, see below for how that's handled instead.

## About the companion workbook

`tracker.xlsx` is a live spreadsheet mirror of the logs used by Claude, with tabs that auto-calculate daily and weekly summaries against your targets. It only ever gets edited from your primary device (whichever one you run Claude Code from most, for example a home computer). A phone/cloud session logs to the markdown files only. 

Your primary device backfills the matching rows next time you run a session on it. This is because it's a binary file, and two devices editing it around the same time can't be merged the way the text logs can. See the workbook's own README tab for its tab structure and color key.

## Project map

- `CLAUDE.md` contains the instructions Claude follows for this project.
- `profile-and-targets.md` logs your stats, goal, and calculated targets. It's filled in by the onboarding Q&A, then updated with changes like reweigh, new activity level, etc.
- `welcome-message.md` is the message sent at the end of onboarding. Not otherwise used.
- `food-log.md` and `tracker.xlsx` are updated with ongoing data.
- `.claude/` settings and hook scripts for git sync, plus a few quality checks: an onboarding gate that blocks logging before setup finishes, a repo-privacy check, and Vale style/content linting (see `.vale.ini`).
- `images/` archived copies of every photo you send, plus this template's own mascot image, shown at the top of this file.
- `statements/` bank/card statement source material. The extracted text gets committed. A raw original file, if you send one, stays local only, never committed (see `.gitignore`).
- `reference/` standing reference material you provide for consistency, like a recurring product's label or a standard workout routine, not a dated log entry.
- `spending-log.md`, `grocery-purchases.md`, `exercise-log.md` are opt-in features.
- `archive/` contains files for any feature you've turned off.