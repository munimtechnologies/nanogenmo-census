# Pre-registration: a forward forecast of NaNoGenMo 2026's finished entries

Written and committed on 2026-11-06 (UTC), while NaNoGenMo 2026 is still running (1 November to 1 December 2026). The git commit time of this file is the registration time. Made by MV2 of Munim, Inc., with AI agents working in his name. Text CC BY 4.0.

## Why

The 2013-2025 census ([../2026-11/RESULT.md](../2026-11/RESULT.md)) found that model-written text (LLM_TEXT) peaked in 2024 at 40.9% of completed entries and fell to 10.5% in 2025. In 2025, entries where a language model only wrote code or scored choices (LLM_OTHER, 4) outnumbered entries with model text (2) for the first time. With 19 entries, that could be noise. A forecast fixed before the 2026 entries are finished tests whether it was.

## What was seen before writing this

- All of the 2013-2025 census results.
- One count: on 2026-11-06 the GitHub search API reported 11 issues in `NaNoGenMo/2026`, and 11 in `NaNoGenMo/2025` created before 2025-11-07. No 2026 issue title, body, comment or label was read for this forecast. A participant's comment in [issue #6](https://github.com/NaNoGenMo/2026/issues/6) had been read earlier (it is quoted in the census pre-registration).

## Frame and measures (the same as the census)

- Repository `NaNoGenMo/2026`. Every issue labelled `completed` (case-insensitive) when read, pull requests excluded. Issues opened = all issues without pull requests and without the `admin` label.
- `census.py` 0.2.0, which differs from 0.1.0 only in adding 2026 to the repository list. Because the census rule (comments up to 1 February of the following year) would wait until 2027, 2026 entries are read with comments up to the time of reading. Every term list, flag and code-link rule stays unchanged.
- Read **on or after 2026-12-15** (two weeks after the event ends, to give the organisers time to label). If fewer than 5 issues carry `completed` on that date, the read is repeated weekly until 2027-01-15. If there are still fewer than 5, the forecast is reported as not gradable.
- Primary coding: the same rubric as the census (LLM_TEXT, LLM_OTHER, MENTION_ONLY, UNCLEAR, NO_MENTION), done by an AI agent from the snippets and, where needed, the issue page. Every code is published with its quote.

## Predictions

- **F1.** 2026 has at most 22 completed entries. That is fewer than 2023's 23; 2024 had 22 and 2025 had 19.
- **F2.** At most 20% of 2026's completed entries are coded LLM_TEXT.
- **F3.** In 2026, LLM_OTHER entries are at least as many as LLM_TEXT entries.
- **F4.** The completion rate (completed / issues opened) is at least 70%. It was 75.9% in 2024 and 86.4% in 2025.
- **F5.** At least 80% of 2026's completed entries link to code. The 2023-2025 rates were 82.6%, 81.8% and 84.2%.

Each prediction is reported as held or not, whatever the result. UNCLEAR entries count as not LLM_TEXT and not LLM_OTHER for F2 and F3, and the result also reports what F2 and F3 would be if every UNCLEAR entry were LLM_TEXT.

## Limits, stated now

- A year has about 20 entries, so one or two entries move every share by 5-10 points. These are forecasts about one small year, not tests of a trend.
- Reading comments only up to mid-December, rather than to 1 February, can miss method notes added late. Every share is a lower bound on mentions.
- The coding is done by AI agents, not by people.
- This is an independent study. It is not run by or affiliated with NaNoGenMo or its organisers, and it does not post in the NaNoGenMo repositories.
