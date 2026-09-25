Running food/drink log. This is the primary tracking surface - you don't touch this file yourself. Send what you ate or drank in whatever form is easiest (photo, text, or voice), and whoever is processing (any session in this project) does the parsing and logging. See CLAUDE.md for image archiving and shared-order handling.

How to process a new entry:
1. Read profile-and-targets.md first for the current targets and context.
2. Nutrition label photo: read the printed values directly, mark [exact]. This is the most reliable input available - prefer it when a packaged product is involved.
3. Barcode photo: a barcode's black-and-white pattern usually cannot be decoded reliably from an image without a dedicated scanner - look for a printed UPC number or product name/brand visible in the same photo and use that to identify the product (web search it if needed) rather than the barcode pattern itself. If nothing is legible, ask what the product is rather than guessing, and say plainly the barcode itself couldn't be read.
4. Receipt photo: these are groceries purchased, not necessarily eaten - log them into spending-log.md and grocery-purchases.md, and only add a food-log row if the person separately says they ate/drank something specific from it.
5. Restaurant with a friend / shared plates: log only what the person says they personally ate or drank, never the full ticket or the group order - see CLAUDE.md.
6. Plain text/voice description ("chicken thigh, rice, one beer"): estimate calories and macros from standard nutrition knowledge, mark [estimated]. For a specific branded or restaurant item, look up the real numbers when possible, mark [looked up].
7. Archive any uploaded image per CLAUDE.md (images/, or statements/ for bank/card statements).
8. Append a new row to the table below (if the file gets unwieldy, summarize older weeks into a compact block and keep recent weeks in full detail).
9. Reply with a short status only: today's running total vs. calorie and protein targets from profile-and-targets.md, nothing more elaborate unless asked.
10. The Carbs column is net carbs (total carbohydrate minus dietary fiber) whenever fiber content is known (label or a reliable look-up). When fiber isn't known (plain estimate with no label), log total carb as before since there's no fiber figure to subtract - don't invent one.

| Date | Item | Calories | Protein (g) | Carbs (g) | Fat (g) | Alcohol? | Confidence |
|---|---|---|---|---|---|---|---|
