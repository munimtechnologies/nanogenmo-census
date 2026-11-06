# Result: which methods did NaNoGenMo's finished entries use, 2013-2025?

Graded on 2026-11-06 (UTC) against [PREREGISTRATION.md](PREREGISTRATION.md), which was first committed at 2026-11-06T03:58:56Z. `census.py` 0.1.0 read the data between 09:52:00 and 09:54:05 UTC the same day (76 API requests, all 13 years complete; see [meta.json](meta.json)). Made by MV2 of Munim, Inc., with AI agents working in his name. The primary coding was done by an AI agent, not by people. Every coded entry is listed with the words its code rests on in [coding.csv](coding.csv). Text and data CC BY 4.0.

## Predictions

| | Prediction | Result | Held? |
|---|---|---|---|
| P1 | `completed` counts match Montfort's 2020-2024 figures exactly in at least 4 of 5 years | 56, 57, 33, 23, 22 against 56, 56, 33, 23, 22 (2021 is one higher) | **held** |
| P2 | At most 10% of completed entries carry a language-model term in every year 2013-2018 | highest is 2.5% (2015) | **held** |
| P3 | At least 30% of completed entries are coded LLM_TEXT in at least one of 2023, 2024, 2025 | 21.7%, **40.9%**, 10.5% | **held, but only in 2024, the one year seen during design** |
| P4 | Pooled 2023-2025, LLM_TEXT entries link to code at least 10 points less often than the other completed entries | 87.5% (14 of 16) against 81.3% (39 of 48): 6.3 points *more* often | **failed** |
| P5 | The year with the highest earlier-neural share falls in 2016-2019 | 2017 (10.0%) | **held** |
| P6 | Every year 2022-2025 has fewer completed entries than every year 2014-2021 | most in 2022-2025: 33; fewest in 2014-2021: 56 | **held** |

Five held and one failed. P3 needs a caveat. The pre-registration says that one listing of 2024's completed issues was read while the census was being designed. 2024 is the only year that clears 30%. The two years nobody had looked at, 2023 and 2025, are both below it. Read P3 as held on non-blind data.

## Primary coding: what the language-model mentions turned out to be

56 completed entries (2013-2025) name a language-model term. Each one was read, and where the snippets did not settle the question, so was its issue page.

| Year | Completed | Term mentions | LLM_TEXT | LLM_OTHER | MENTION_ONLY | UNCLEAR | LLM_TEXT share |
|---|---|---|---|---|---|---|---|
| 2013 | 19 | 0 | 0 | 0 | 0 | 0 | 0.0% |
| 2014 | 91 | 1 | 0 | 0 | 1 | 0 | 0.0% |
| 2015 | 79 | 2 | 0 | 0 | 2 | 0 | 0.0% |
| 2016 | 60 | 0 | 0 | 0 | 0 | 0 | 0.0% |
| 2017 | 60 | 0 | 0 | 0 | 0 | 0 | 0.0% |
| 2018 | 59 | 1 | 0 | 0 | 1 | 0 | 0.0% |
| 2019 | 97 | 16 | 9 | 0 | 5 | 2 | 9.3% |
| 2020 | 56 | 6 | 6 | 0 | 0 | 0 | 10.7% |
| 2021 | 57 | 0 | 0 | 0 | 0 | 0 | 0.0% |
| 2022 | 33 | 4 | 2 | 1 | 0 | 1 | 6.1% |
| 2023 | 23 | 7 | 5 | 0 | 2 | 0 | 21.7% |
| 2024 | 22 | 13 | 9 | 1 | 3 | 0 | 40.9% |
| 2025 | 19 | 6 | 2 | 4 | 0 | 0 | 10.5% |
| **All** | **675** | **56** | **33** | **6** | **14** | **3** | **4.9%** |

What the coding shows (exploratory, not predicted):

- **Mentions overstate use.** 33 of the 56 entries that name a language-model term put model-written text into the novel. In 2023-2025 the figure is 16 of 26. Mentions that were not uses include a star sign ("Gemini"), creatures in sample output ("Kobold", "llama"), a URL to a magazine article about GPT-2, an arcade game (Q*BERT), and entrants explaining why they would *not* use a chatbot.
- **Model-written text reached NaNoGenMo with GPT-2 in 2019, not with ChatGPT.** 2019 and 2020 already had 9 and 6 such entries, mostly fine-tuned GPT-2 and AI Dungeon/GPT-3. Pooled 2019-2022, 17 of 243 completed entries (7.0%) are LLM_TEXT; pooled 2023-2025, 16 of 64 (25.0%).
- **2024 was the peak; 2025 dropped back.** 2025 has 2 LLM_TEXT entries (10.5%). It also has 4 entries where a model wrote or helped write the code, or only scored choices, with none of its text in the novel (LLM_OTHER). This is the first year where those outnumber model-text entries. The counts are small (19 entries), so this is a pattern to watch, not a trend.
- **Model-text entries do not share code less often.** This was P4, and it failed. Montfort's 2025 note suggested that more entries now use proprietary commercial models whose code can't be shared. Among *completed* entries the data don't support that: 14 of the 16 LLM_TEXT entries in 2023-2025 link to code, a higher share than the other entries. This census can't see entries that were never labelled `completed`. If unfinished or code-less LLM entries are kept out of the label, the frame itself hides the effect.
- **Fewer entries, but more of them finish.** Issues opened fell from 190 (2015) to 22 (2025), and completed entries from 97 (2019) to 19 (2025). The completion rate, which ran between 40% and 67% in 2014-2022, reached 76% in 2024 and 86% in 2025 ([years.csv](years.csv)).

## Files

- [coding.csv](coding.csv): one row for each of the 56 entries with a language-model term: code, quote (25 words or fewer) and a note when the issue page decided it.
- [REPORT.md](REPORT.md), [years.csv](years.csv), [entries.csv](entries.csv), [summary.json](summary.json), [meta.json](meta.json): the unedited output of `census.py`.
- The snippet file and the page cache are not published. Every snippet comes from a public issue linked in `coding.csv`.

## Limits

- One AI agent did the coding, once, with no second coder. Three entries stay UNCLEAR because their issue pages never say which model, if any, wrote the text. Counting all three as LLM_TEXT would change 2019 to 11.3% and 2022 to 9.1%. No 2023-2025 entry is UNCLEAR, so P3 and P4 don't depend on them.
- Two coding calls lean on reading the rubric closely. char-rnn (2015) and entrants' own small models (2014, 2018, 2024) are not *pretrained* language models, so they are MENTION_ONLY. A sentence-embedding model that only scores deletions (2025) is LLM_OTHER.
- Only the entrant's own words in the issue were read, so an entry that used a model without saying so in its issue counts as not using one. One 2024 entry was found only because it also said "local LLM": its main statement misspells ChatGPT as "ChatCPT".
- The `completed` label is the organisers' own, and labels can change.

*MV2, Munim, Inc.*
