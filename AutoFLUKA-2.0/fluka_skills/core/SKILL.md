---
name: AutoFLUKA Core Rules
description: Must-follow rules loaded first on every turn; the lane skills hold the details.
---

# Core rules (always loaded)

- Skill text injected each turn is a preview: a file may end with "[cut at ...]", and files that got no room are listed at the end. When the task needs one of them, read the full file the way its note says before acting. SkillLookupTool('<pack>'), where available, also lists the pack's rules files and the troubleshooting KB.
- Cards: take each field's meaning and order from the closest working example, then write the card with fluka_card_formatter_tool. Never space values by hand: FLUKA reads fixed 10-column fields, and a misplaced value is rejected or silently read as a different number.
- USRTRACK and USRBDX continuation cards hold Emax in WHAT(1) and Emin in WHAT(2), high before low. FLUKA does not compute detector size: set the true volume (USRTRACK WHAT(5)) or area (USRBDX WHAT(6)), or normalize afterward and say so.
- A point or pencil source needs only BEAM and BEAMPOS; BEAM WHAT(3) above 2000*pi mrad (e.g. 10000.0) makes it isotropic. Write a SOURCE routine only for what cards cannot express.
- Run ladder: a low-statistics test-N first, each repair in a fresh test-(N+1). After a test passes, production-N runs seeded copies of that exact deck. A deck changed after its test needs a new test before production. After two identical failures in a row, stop and ask.
- Questions get answers, not runs: start a FLUKA run only when the user asks for one or agrees to a run you proposed.
- A detector total of exactly 0 is a set-up failure until shown otherwise: read that scorer's set-up lines in the .out (energy grid, region, volume or area) and the troubleshooting KB before reporting it.
- Claim success only with run artifacts on disk, and report every test-N and production-N created in the turn with its outcome.
