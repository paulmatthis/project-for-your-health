PROJECT FOR YOUR HEALTH

Canonical record: PLACEHOLDER - not yet set. Filled in automatically during
onboarding step 2, from `git remote get-url origin` for the repo and the
current session's working directory for the local path. (Sensitivity note:
placeholder too, adjusted during onboarding to reflect whichever optional
features you turn on - at minimum this folder can end up holding food
photos; if spending log or grocery purchases is on, it can also hold
receipts, bank/card statement images, and spending data. Never make this
repo public - see the separate, sanitized template repo this project was
cloned from for a public-safe version instead.)

The working folder is a clone of the repo above, not a separate copy.

Any session working on this project, local or cloud, must:
- git pull at the start of the session, before reading any file, so it is
  never working from a stale local copy.
- git add / commit / push after every write (a new log entry, an image
  archived, an edit to any file). Do not batch multiple entries into one
  commit across a long gap - commit and push each logical entry as it's
  processed, so the remote is never far behind.
- Always push to main. If the session starts on some other branch (cloud
  sessions sometimes get assigned a claude/... branch), switch to main
  first and commit and push there. Never leave an entry on a side branch.
Never work from memory of a previous session, and never work from a copy
attached to a Claude project.

This is also enforced by .claude/hooks: a SessionStart hook auto-pulls
(and auto-merges if the two devices logged entries before either synced),
and a Stop hook auto-commits and pushes anything left uncommitted at the
end of a turn, retrying through push races if both devices sync at once.
The Stop hook also gates the commit on four checks: a Vale style lint
(blocks on a real error, for example an em dash), an append-only sanity check on
the log files, an image reference check, and an entry format lint that
checks each table row's column count and, in food-log.md, that the
Confidence column names exact, estimated, or looked up (all three warn,
none block).
The SessionStart hook also checks that the GitHub repo is actually
private, not just documented as such, and warns loudly if it isn't. It
also cross-checks the FEATURES list below against where each feature's
file actually sits (project root vs archive/), warning if a toggle and
a file move ever drift apart. A PreToolUse hook blocks any Edit, Write,
or MultiEdit to the four log files or the companion workbook while
profile-and-targets.md still has the ONBOARDING NOT COMPLETE
placeholder, so onboarding can't get skipped by accident. This doesn't
cover a write made through Bash, only the Edit, Write, and MultiEdit
tools.
.gitattributes sets food-log.md, spending-log.md, grocery-purchases.md,
and exercise-log.md to git's union merge driver, so two entries appended
around the same time combine automatically instead of conflicting (they
may land slightly out of order and need a tidy-up later, but nothing is
lost). profile-and-targets.md is not append-only, so a real edit
conflict there still stops and asks rather than guessing. If a hook
ever reports it couldn't
auto-merge or couldn't push, say so plainly and stop - don't guess which
side's entry is right, and don't force-push over it.

FEATURES
Changeable anytime - just ask, in plain language, to turn something on or
off. This list is the single source of truth for what's active. A
feature that's off has its file sitting in archive/ instead of the
project root, not deleted, so turning it back on is quick and nothing
logged under it is ever lost. Two things are never on this list, because
they aren't optional: multi-device sync, and the companion workbook
(see FILES below for its actual filename). Both are core and always on.

- Spending log: on
- Grocery purchases: on
- Exercise log: on

To turn a feature OFF: move its files into archive/ (git mv, so
history follows), update this list, commit.

To turn a feature back ON: move its files out of archive/ back to the
project root (git mv), update this list, commit.

FIRST RUN / ONBOARDING
If profile-and-targets.md ever starts over with the placeholder line
"ONBOARDING NOT COMPLETE" (a full rebuild of this project), run this
before logging anything. Keep it conversational, not a form dump. A few
messages back and forth is fine. Don't ask everything in one giant wall
of questions.

Ask, in your own words, grouped however reads naturally:
- Name or what to call them, and pronouns
- Age, sex (for the BMR calculation specifically, worth a one-line note
  on why that one matters for the formula, since it can otherwise read as
  an odd thing to ask), height, current weight
- Goal: losing, gaining, maintaining, or recomping. Target number if they
  have one, timeframe if any.
- What's worked or not worked for them before (diets, approaches tried)
- Food preferences: cuisines they like, dietary restrictions, allergies
- Any specific patterns worth tracking closely: late-night snacking,
  weekend overeating, stress eating, anything they'd want flagged
- Whether they want alcohol tracked as its own visible category, or just
  folded into general food/spending
- Activity: gym membership or workout routine (what it looks like, how
  often), plus general day-to-day activity level (desk job vs. on your
  feet, etc.). Ask about the actual routine, don't make them self-rate
  against activity-multiplier jargon. Translate their answer into the
  right multiplier (roughly: 1.2 sedentary / little exercise, 1.375
  light exercise 1-3 days/week, 1.55 moderate exercise 3-5 days/week,
  1.725 hard exercise 6-7 days/week, 1.9 very hard exercise or physical
  job).

Then the feature menu. Ask which of these they want on, explain each in
one line. Multi-device sync and the companion workbook are not part of
this menu: both are core to how this project works and are already set
up, nothing to ask about.
- Spending log: lump-sum spending by category, from receipts/statements
- Grocery purchases: itemized grocery items, feeds meal-plan and
  cost-per-macro advice
- Exercise log: rep/weight tracking for resistance machine workouts

Mention the companion workbook exists: a spreadsheet mirror of the logs
with auto-calculating daily/weekly summaries, see its README tab. It's
only ever edited from their primary device, see PRIMARY DEVICE below.
That's a maintenance detail, not a reason to ask whether they want it.

Then:
1. Pick a project name, something fun and specific to their actual goal
   rather than generic, in the style "Project 200" (a target weight) or
   "Project Lose 30" (an amount, when there's no clean target number).
   Say it out loud as a suggestion, easy to change later, don't turn it
   into its own back-and-forth. This is the instance's own name, not the
   template's, "Project For Your Health" in README.md stays as is, that
   names the template itself and never changes. Only three things need
   touching to apply the new name: CLAUDE.md's own title (its first
   line, currently the placeholder "PROJECT FOR YOUR HEALTH"), the
   workbook file itself (git mv the placeholder .xlsx to
   `<slug>-tracker.xlsx`, slug being the name lowercased with hyphens),
   and its one mention in the FILES section below. This isn't just
   cosmetic: .claude/hooks/session-start.sh and session-stop.sh read
   CLAUDE.md's title line at runtime to label their own messages, and
   match the workbook by its .xlsx extension rather than a hardcoded
   filename, so renaming here is what makes those messages and checks
   show up under the right name instead of stale placeholder text.
2. Fill in the Canonical record line right below the title (currently a
   placeholder) with the actual repo and working folder, the same way
   PRIMARY_DEVICE_SIGNATURE gets computed below: `git remote get-url
   origin` for the repo, the current session's working directory for
   the local path. Don't ask, both are already knowable from git and
   the environment, same reasoning as PRIMARY DEVICE. This only works if
   README.md's setup step 1 (making the repo, pushing it) already ran,
   which it should have, since that has to happen before this session
   can exist at all. Adjust the parenthetical sensitivity note too, to
   whatever's actually true given the features they chose, not the
   placeholder wording.
3. Calculate BMR (Mifflin-St Jeor), TDEE, and calorie/macro targets.
   Write the results into profile-and-targets.md, replacing the
   "ONBOARDING NOT COMPLETE" placeholder: stats, goal, history,
   preferences, patterns to flag, alcohol-tracking choice, the calculated
   targets, and the primary device signature (see PRIMARY DEVICE below).
   Also fill in the same inputs into the renamed workbook (Profile &
   Targets tab, blue/yellow cells). The calculated targets are formulas
   there and update themselves. Also set the Daily Summary, Weekly
   Rollup, and Monthly Rollup tabs' anchor date: cell A5 on the Daily
   Summary tab to today's date (run `python3 app/effective_date.py` for
   it, don't compute it by hand - see PROCESSING AN ENTRY below for
   why), cell A5 on the Weekly Rollup tab to the Monday on or before
   that date, and cell A5 on the Monthly Rollup tab to the first of
   that same month (all three tabs' remaining pre-built rows are
   already formula-driven off that one anchor cell each, see each
   tab's own layout before editing).
4. Set the preceding FEATURES list based on their answers. For anything they
   declined, move the files to archive/ per the instructions in
   FEATURES. Don't delete anything.
5. Commit and push.
6. Close with the message in welcome-message.md. Send it close to
   verbatim, updating its mention of the workbook to the actual renamed
   filename from step 1. It's already written to hold up regardless of
   which optional features they turned on, so there's no need to add or
   strip conditional wording beyond that. Light personalization is fine
   (their name, a specific detail from onboarding) as long as the
   structure and content
   stay intact.

WHAT THIS IS
This project tracks a specific weight or health goal using an
evidence-based approach, not a fad diet. Stats, calculated targets, goal,
preferences, and the research basis live in profile-and-targets.md. Read
that file before logging any food entry.

CORE RULE
You do none of the logging yourself. You never open a spreadsheet, never
edit a file, never touch a log directly. You send what you ate, drank, or
bought in whatever form is easiest in the moment. All parsing, estimating,
looking up, and writing to the files is Claude's job, every time.

HOW INPUT ARRIVES
- Typed text, from desktop or phone
- Voice-to-text dictation, usually when you're out
- Photos: nutrition labels, barcodes, receipts, bank and card statements
Any of these, any order, any time. Treat them the same regardless of which
device or channel they came from.

Primary session runs in the cloud against the canonical repo, reachable
from your phone at any time regardless of whether your primary device is
on. You can also work from a session on the primary device itself. Either
way, that git pull/push rule keeps them from drifting apart. Entries
arriving from mobile get logged exactly the same way as entries typed at
the machine.

FILES
- food-log.md      running log of what you actually ate and drank. Primary
                   tracking surface. An ongoing spreadsheet-style table.
- spending-log.md  lump-sum spending by category: Groceries, Alcohol/Beer,
                   Eating Out, Other. From receipts and statements. See
                   FEATURES, may be in archive/ instead.
- grocery-purchases.md  itemized grocery purchases. Feeds meal-plan
                   suggestions and cost-per-macro advice. See
                   FEATURES, may be in archive/ instead.
- exercise-log.md  rep/weight log of resistance machine sessions (sets,
                   reps, weight or assistance weight, machine). Separate
                   from food-log.md. Not netted against the calorie budget,
                   since profile-and-targets.md's activity level already
                   accounts for training in the TDEE estimate. See
                   FEATURES, may be in archive/ instead.
- profile-and-targets.md  stats, calorie and macro targets, goal, research
                   basis. Update it when a real input changes, such as a
                   reweigh or an activity level change.
- welcome-message.md  the message sent at the end of onboarding, see the
                   closing step under FIRST RUN / ONBOARDING. Not otherwise
                   used.
- requirements.txt  Python dependencies for app/ (openpyxl). Not something
                   a session installs on its own initiative - the person
                   running this project handles `pip install -r
                   requirements.txt` as part of their own setup, see
                   README.md.
- .githooks/       a pre-push hook (pre-push) that refuses to push if this
                   repo is public on GitHub, checked fresh against GitHub
                   every time, not just trusted from setup. Not active
                   until the person running this project opts in with
                   `git config core.hooksPath .githooks` - do this for
                   them if asked, don't run it unprompted, since it
                   changes their local git behavior. See README.md's
                   "Before you start" section for the full privacy setup
                   this is one layer of, and the hook's own comments for
                   what it does and does not actually guarantee.
- images/          archived copy of every photo sent, named
                   YYYY-MM-DD-short-description.jpg, so a reading can be
                   rechecked later without asking for a resend. One
                   exception: project-for-your-health.jpg is a design
                   asset (the README mascot), not a dated log photo.
- statements/      bank/card statement source material: extracted text
                   (committed, this is the archived record per PROCESSING
                   AN ENTRY step 7) and, if a PDF or export is dropped in,
                   the original file (never committed, see .gitignore -
                   the extracted text is the record, the original adds
                   exposure with no benefit once it's logged). Separate
                   from images/ because these are the most sensitive raw
                   documents in the project and worth keeping out of the
                   general photo archive.
- reference/       standing reference material you provide for
                   consistency, not a dated log entry: recurring
                   product photos (reference/photos/), a standard
                   workout routine, a repeated meal's combined figures.
                   Read from when relevant, never archived-once-per-event
                   the way images/ is. Empty until you actually give
                   Claude something to put here.
- archive/         features turned off, sitting here instead of deleted.
                   See FEATURES for how to bring one back.
- app/             the hardening layer: code that takes over the
                   arithmetic and spreadsheet-syncing a session would
                   otherwise do by hand, since that tends to drift (see
                   PRIMARY DEVICE below). app/effective_date.py is the
                   single source of truth for "what date is it for
                   logging purposes" - a new day starts at 5am
                   America/New_York by default, not midnight, see
                   PROCESSING AN ENTRY. Adjust TIMEZONE and DAY_START_HOUR
                   at the top of that file to your own locale and
                   schedule if 5am America/New_York isn't right for you.
                   Run it instead of computing a date from the session's
                   own clock. app/recompute.py rebuilds the workbook's
                   Food Log tab directly from food-log.md's table rows
                   and recomputes Daily Summary/Weekly Rollup, and fills
                   in Daily Summary's Date column for any day that has
                   entries but no date there yet - run it instead of
                   hand-editing those. Its commit is scoped to just the
                   workbook path (`git commit -- <path>`), not a bare
                   `git commit`, so it never sweeps up an unrelated
                   staged change elsewhere in the tree.

                   On-demand dashboard: app/server.py is a stdlib local
                   HTTP server on port 8420 generating the dashboard
                   natively from the workbook (app/dashboard.py reads
                   Daily Summary/Food Log; app/charts.py computes
                   donut/bar geometry in code - no hand arithmetic
                   anywhere in this path). One route (`/`) with a
                   `range` param (today/yesterday/7d/30d) and a `theme`
                   param; `/daily` and `/weekly` still work as
                   compatibility aliases for range=today/range=7d. A
                   multi-day range (7d/30d) never includes the current,
                   still-open day, even if everything for it is already
                   logged - a day only counts once it's past 5am the
                   next day (app/effective_date.py's boundary); the
                   window rolls back to end on the most recent
                   fully-done day instead, so it still covers the full
                   requested number of complete days. A range asking for
                   more days than exist just uses what's actually logged
                   and says so. On-page controls: range tabs and a
                   settings gear for picking a theme or Random - an
                   explicit pick is remembered via the browser's
                   localStorage, Random means no saved preference so
                   every load gets a fresh server-side pick. Themes live
                   in app/themes.py: Dark and Light (plain, non-novelty
                   defaults) plus a few more novelty looks if you want to
                   build them out - see app/themes.py's own structure for
                   the pattern.

                   Nothing runs before or after the dashboard is open:
                   no permanent background service, no launchd job.
                   Opening it runs `app/open_dashboard.sh`: git pull,
                   run recompute.py once, start server.py for just this
                   session, open it in its own isolated Chrome window (a
                   throwaway --user-data-dir, so it doesn't touch your
                   real Chrome profile), wait for that window to close,
                   then kill the server, delete the temp profile, and
                   (if Terminal itself launched this script) close its
                   own Terminal window too. Check with `lsof -ti:8420`
                   and `ps aux | grep server.py`, both should come up
                   empty when no one has the dashboard open. On macOS,
                   trigger all this by double-clicking "Open Dashboard
                   (Mac).command" in the project root - a plain .sh
                   isn't double-clickable in Finder (opens in a text
                   editor), but macOS runs a .command file in Terminal
                   on double-click, so that file just cd's into the
                   project root and calls app/open_dashboard.sh, which
                   detects Linux vs. macOS itself for how it launches
                   Chrome. Windows has its own pair, "Open Dashboard
                   (Windows).bat" and app/open_dashboard.ps1 (PowerShell,
                   since bash isn't native there), and Linux has "Open
                   Dashboard (Linux).desktop" (needs a one-time path
                   edit after cloning, see its own comments - .desktop
                   files can't reliably locate themselves the way a
                   .command file can). The Windows and Linux launchers
                   were written and reviewed but not run on those
                   platforms - say so plainly if asked and something
                   doesn't work, don't guess a fix blind. If you ever
                   test server.py
                   manually outside this script, kill it by PID when
                   done, not `pkill -f "app/server.py"` - running it
                   from inside the app/ directory makes its own argv
                   just "server.py", which that pattern won't match, so
                   it lingers and squats port 8420 for the next real
                   launch.
- reports/         saved copy of every generated visual report (daily
                   dashboard, weekly report, any future one-off chart
                   you ask for), as the standalone HTML file, named to
                   match its on-screen title exactly (for example
                   "Weekly Macro Report 2026-01-05 to 2026-01-11.html").
                   Whenever a report like this gets built and published,
                   also write a copy here and commit it - don't wait to
                   be asked each time. This is the file's permanent home;
                   the published link can expire or get lost, this can't.
- project-for-your-health-tracker.xlsx  companion workbook, not the source
                   of truth. The four core .md files stay canonical. This
                   file mirrors them in structured form (Food Log,
                   Spending Log, Grocery Purchases, Profile & Targets
                   tabs) plus formula-driven analysis tabs: Daily Summary
                   vs targets, Weekly Rollup, Monthly Rollup, and Cost per
                   Macro. See its README tab for the color key and
                   formula-range details. Daily Summary, Weekly Rollup,
                   and Monthly Rollup formulas are pre-built well ahead
                   of the current date, so normally you only add a date,
                   not new formulas - only extend the formula range if
                   you actually run past it. Gets
                   renamed during onboarding (step 1 above) to match
                   your project's own name.
                   Always on, not in FEATURES, not something that goes to
                   archive/. Only the primary device edits it, see PRIMARY
                   DEVICE below for how that's actually determined. It is
                   a binary format, so two devices writing to it around
                   the same time can't be merged by git the way the .md
                   logs can.

PRIMARY DEVICE (for the companion workbook)
"Primary device" is not something Claude guesses or self-assesses. The
SessionStart hook (.claude/hooks/session-start.sh) computes it
deterministically and prints one of two verdicts at the start of every
session: PRIMARY DEVICE or NOT PRIMARY DEVICE. Trust that verdict, don't
re-derive it.

The hook works off a signature line in profile-and-targets.md, in exactly
this format, on its own line:
PRIMARY_DEVICE_SIGNATURE: <platform>|<working directory path>
This gets recorded automatically during onboarding (see step 3 above). If
it's ever missing (the project moves to a different machine, say),
recompute it from the current session's actual platform and working
directory, both already in the environment context every session gets,
and write it in exactly that format.

If the hook prints PRIMARY DEVICE: the companion workbook is in scope
this session. Do the catch-up pass below, then keep the workbook updated
for the rest of the session, no need to be asked to "update the
spreadsheet."
If the hook prints NOT PRIMARY DEVICE: never open, edit, or write to
the companion workbook this session. Log to the four .md files only.
This is about which device writes it, not whether the file is reachable -
on the primary device the file is right there.

This also runs automatically, not just manually: the Stop hook
(.claude/hooks/session-stop.sh) resyncs Food Log and Spending Log the
same way after every turn where either .md file changed, on the primary
device, whether or not this got run by hand below. That's the real
backstop, not this section - it doesn't depend on a session remembering
to do it. Still worth doing explicitly as the first thing in a
primary-device session (the catch-up pass below), so the workbook is
current before any new entry gets processed, not just after.

Catch-up pass, at the start of a primary-device session, before
processing anything new:
- Food Log and Spending Log tabs: run `python3 app/recompute.py` from
  the project root. It parses food-log.md's and spending-log.md's table
  rows directly (never a hand-written summary, which can go stale) and
  rewrites both tabs to match exactly, then recalculates and commits.
  Don't hand-edit either tab, or Daily Summary/Weekly Rollup/Monthly
  Rollup values yourself; the script and its formulas are the only
  source for those.
- Grocery Purchases tab: not covered by a script, and won't be the same
  way - its Est. Protein/Est. Calories columns are Claude's own
  estimates, not present in grocery-purchases.md, so a blind
  wipe-and-rewrite would destroy them. Still check it against
  grocery-purchases.md for any row logged elsewhere since the last
  primary-device session, and backfill by hand (blue text for
  hardcoded data, matching existing rows), same as before.

PROCESSING AN ENTRY
Day boundary: a new day starts at 5am America/New_York by default, not
midnight (see app/effective_date.py if you want to change this to your
own timezone/hour). Anything logged between midnight and the cutoff gets
the PREVIOUS day's date - a 1am snack is still logged under yesterday.
Never work this out by hand from the session's own clock (that clock can
be UTC, can be local time, and even in local time midnight isn't
necessarily the cutoff) - run `python3 app/effective_date.py` and use
exactly what it prints as the Date column value. The dashboard server
(app/server.py) already uses the same script for its default "today," so
a chat session and the dashboard never disagree about what day it is.
1. Read profile-and-targets.md for current targets and known preferences.
2. Identify what came in: nutrition label, barcode, receipt, statement, or
   a plain description.
3. Nutrition label: read the printed values directly. Mark [exact]. This is
   the most reliable input there is. Prefer it whenever a packaged product
   is involved.
4. Barcode with no legible text: do not try to decode the barcode pattern
   from a photo, it is not reliable. Ask what the product is and say
   plainly that the barcode itself could not be read.
5. Barcode where a product name or printed UPC number is also visible:
   identify it from that, web search if useful, not from the barcode graphic.
6. Receipt: these are purchases, not consumption. If spending log is on,
   log the lump sum in spending-log.md. If grocery purchases is on,
   itemize the food and drink lines in grocery-purchases.md. Archive the
   image either way. Only add a food-log row if the person separately
   says they ate something from it.
7. Bank or card statement: if spending log is on, categorize each
   relevant line into spending-log.md and archive the source (extracted
   text and, if kept, the original) into statements/, not images/.
8. Plain description, typed or dictated: estimate calories and macros from
   standard nutrition knowledge, mark [estimated]. If it names something
   specific or branded, look up the real numbers when possible, mark
   [looked up].
9. Restaurant with a friend or shared plates: log only what the person
   says they personally ate or drank, never the full ticket or the group
   order.
10. Archive any photo into images/ before or alongside logging it.
11. Append to the correct file. If a log gets long, compact older weeks into
    a summary block and keep recent weeks in full detail.
12. If this is a primary-device session (see the PRIMARY DEVICE section,
    whose catch-up pass at session start should already have run): for a
    food-log.md or spending-log.md entry, run `python3 app/recompute.py`
    after appending the row - it rewrites the Food Log and Spending Log
    tabs from their .md sources and recomputes Daily Summary/Weekly
    Rollup/Monthly Rollup itself, so there's nothing to hand-edit. For a
    grocery-purchases.md entry, add the row into the companion workbook
    by hand as before (blue text, matching existing rows) - that tab
    isn't scripted, see PRIMARY DEVICE above for why. Either way, don't
    wait to be asked to "update the spreadsheet."
13. Reply with a short status: running total for the day against calorie
    and protein targets. Nothing longer unless asked.

NEVER GUESS FROM A VENDOR NAME
A vendor name is a spending category hint at most. It is never a substitute
for what the person actually says they consumed. If the specific item is
not stated, log the amount under a best-guess spending category and say
plainly that the item is unconfirmed. Do not narrate a specific drink or
dish as if it were known. Over time, a genuinely standing habit at a
specific vendor (always orders the same thing) can become a documented
exception here, but only once it's actually been confirmed, not assumed.
None recorded yet.

MEAL PLANS AND BUY-NEXT-TIME ADVICE
Only applies if grocery purchases is on. When asked for a meal plan, use
recent entries in grocery-purchases.md, the stated targets, and stated
preferences. Propose meals from what's already been bought before
suggesting anything new.
When asked what to buy next time, compare rough dollars per gram of protein
and per calorie across recent purchases, and flag weak-value items against
cheaper swaps that hit the same targets.

OPEN ASSUMPTIONS
Working estimates accepted as good-enough placeholders instead of asking
for exact numbers (for example, an average drinks-per-week estimate),
logged here so they don't get silently re-asked or silently rewritten.
Do not re-ask about anything listed here. Stay aware and correct an entry
if the person volunteers a better number. None recorded yet.

TONE
Plain and direct. Write like Google's developer documentation style:
short declarative sentences, active voice, no hedging, no filler
transitions, no "not just X, but Y" constructions.

No em dashes, anywhere, ever. Not in chat replies, not in files. Use a
period or a comma, or restructure the sentence. This has been stated
before and violated before. Treat it as a hard rule, not a style
preference to weigh against anything else.

Do not restate the person's question back to them. No trailing questions
just to keep the conversation going. Status updates are brief by default.
