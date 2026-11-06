# NaNoGenMo census: which methods finished entries name, 2013-2025

census.py 0.1.0. Read from GitHub's public API between 2026-11-06T09:52:00+00:00 and 2026-11-06T09:54:05+00:00 UTC. Pre-registration: live on main, first committed 2026-11-06T03:58:56Z.

Made by MV2 of Munim, Inc., with AI agents working in his name. Data CC BY 4.0, code Apache-2.0.

Completed = issues carrying the organisers' `completed` label when read. Each entry's text is its title, its body and its opener's own comments up to the end of the following January. A term is a mention, not a use: whether a language model wrote the novel is decided by the primary coding.

| Year | Issues | Completed | Completion rate | Language-model terms | Earlier neural | Markov | Tracery/CFG | Gutenberg | Code link |
|---|---|---|---|---|---|---|---|---|---|
| 2013 | 91 | 19 | 20.9% | 0 (0.0%) | 0 (0.0%) | 3 (15.8%) | 0 (0.0%) | 2 (10.5%) | 12 (63.2%) |
| 2014 | 150 | 91 | 60.7% | 1 (1.1%) | 0 (0.0%) | 11 (12.1%) | 0 (0.0%) | 15 (16.5%) | 82 (90.1%) |
| 2015 | 190 | 79 | 41.6% | 2 (2.5%) | 5 (6.3%) | 12 (15.2%) | 0 (0.0%) | 13 (16.5%) | 72 (91.1%) |
| 2016 | 152 | 60 | 39.5% | 0 (0.0%) | 5 (8.3%) | 8 (13.3%) | 3 (5.0%) | 4 (6.7%) | 58 (96.7%) |
| 2017 | 131 | 60 | 45.8% | 0 (0.0%) | 6 (10.0%) | 7 (11.7%) | 6 (10.0%) | 7 (11.7%) | 56 (93.3%) |
| 2018 | 106 | 59 | 55.7% | 1 (1.7%) | 4 (6.8%) | 7 (11.9%) | 5 (8.5%) | 7 (11.9%) | 54 (91.5%) |
| 2019 | 145 | 97 | 66.9% | 16 (16.5%) | 6 (6.2%) | 8 (8.2%) | 6 (6.2%) | 16 (16.5%) | 83 (85.6%) |
| 2020 | 84 | 56 | 66.7% | 6 (10.7%) | 1 (1.8%) | 12 (21.4%) | 4 (7.1%) | 5 (8.9%) | 47 (83.9%) |
| 2021 | 92 | 57 | 62.0% | 0 (0.0%) | 2 (3.5%) | 2 (3.5%) | 1 (1.8%) | 7 (12.3%) | 53 (93.0%) |
| 2022 | 51 | 33 | 64.7% | 4 (12.1%) | 0 (0.0%) | 0 (0.0%) | 4 (12.1%) | 4 (12.1%) | 30 (90.9%) |
| 2023 | 35 | 23 | 65.7% | 7 (30.4%) | 1 (4.3%) | 3 (13.0%) | 4 (17.4%) | 5 (21.7%) | 19 (82.6%) |
| 2024 | 29 | 22 | 75.9% | 13 (59.1%) | 0 (0.0%) | 7 (31.8%) | 2 (9.1%) | 6 (27.3%) | 18 (81.8%) |
| 2025 | 22 | 19 | 86.4% | 6 (31.6%) | 0 (0.0%) | 0 (0.0%) | 1 (5.3%) | 2 (10.5%) | 16 (84.2%) |

Issues = issues opened in the year's repository, without pull requests and admin issues.

## Predictions this script can grade

- **P1**: held. 4 of 5 years match exactly; found 2020: 56, 2021: 57, 2022: 33, 2023: 23, 2024: 22, Montfort 2020: 56, 2021: 56, 2022: 33, 2023: 23, 2024: 22
- **P2**: held. highest language-model-term share 2013-2018: 0.025
- **P3**: pending. graded from the primary coding of snippets.jsonl
- **P4**: pending. graded from the primary coding of snippets.jsonl
- **P5**: held. highest earlier-neural share 0.100 in 2017
- **P6**: held. most completed in 2022-2025: 33; fewest in 2014-2021: 56

## Exploratory (not a prediction)

2023-2025: 64 completed entries, 26 name a language-model term. Share linking to code: 88.5% with a term, 78.9% without.

## Limits

- The `completed` label is the organisers' own; an entry that finished without it is not counted, and labels can change after the event.
- Terms are matched in the opener's own words only. Methods described only in a linked repository, a blog post or the novel itself are missed.
- Term matching over-counts (a critique of LLMs, a character named Claude) and under-counts (a model named in a way the list does not cover). The language-model column is a mention count; the primary coding reads every mention.
- A code link means a link to a code host, sandbox or source file. It does not check that the link still works or that the code is complete.
