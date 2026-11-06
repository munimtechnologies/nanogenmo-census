# nanogenmo-census

Which generation methods did the finished entries of National Novel Generation Month (NaNoGenMo) use, year by year from 2013 to 2025? A pre-registered census of every entry the organisers labelled `completed`, read from the public GitHub repositories of each year.

By MV2 of Munim, Inc. The code, the pre-registration and the coding are made by AI agents working in his name. Code Apache-2.0; text and data CC BY 4.0.

## Status

- **2026-11-06: pre-registered.** [census/2026-11/PREREGISTRATION.md](census/2026-11/PREREGISTRATION.md) fixes the frame, the measures, the coding rubric and six predictions before any data is read. Results will be added under `census/2026-11/` and nothing above them will be edited.

## What it measures

For each completed entry, the opener's own words (title, issue body and their comments up to the end of the following January) are checked for:

- language-model terms (GPT, LLM, Llama, Claude and others); every mention is then read and coded as use or not;
- earlier neural networks (RNN, LSTM), Markov chains, Tracery or context-free grammars, Project Gutenberg;
- a link to source code, which NaNoGenMo's one rule asks for.

## Run it

```
python -m unittest -v
python census.py --out-dir out --cache-dir cache
```

Python 3.10+, standard library only. It uses GitHub's public API without a token, waits out the rate limit (60 requests an hour), and caches each page, so an interrupted run resumes where it stopped. No login is stored: comments are matched to the issue's opener by a salted hash.

## Outputs

- `years.csv`: per year, issues opened, completed entries, and the share naming each method family or linking to code.
- `entries.csv`: one row per completed entry with its issue link, title and flags.
- `REPORT.md`, `summary.json`, `meta.json`: tables, the mechanically graded predictions, and how the run went.
- `snippets.jsonl` and `coding.csv`: the context of every language-model mention, for the primary coding.

## Not affiliated

This is an independent study. It is not run by or affiliated with NaNoGenMo or its organisers.

## Result (added 2026-11-06)

Full write-up: [census/2026-11/RESULT.md](census/2026-11/RESULT.md). Data read 2026-11-06 09:52-09:54 UTC, after the pre-registration went live at 03:58:56 UTC.

- **675 completed entries in 13 years.** 56 of them name a language-model term, and 33 of those 56 put model-written text into the novel (LLM_TEXT). The other mentions are star signs, creatures named "llama", article links, and entrants explaining why they won't use a chatbot.
- **Model-written text arrived with GPT-2 in 2019,** not with ChatGPT: 9 entries in 2019 and 6 in 2020. LLM_TEXT share: 7.0% of completed entries in 2019-2022 and 25.0% in 2023-2025. It peaked at 40.9% in 2024 and fell to 10.5% in 2025. In 2025, entries where a model only wrote code or scored choices (4) outnumber entries with model-written text (2).
- **Predictions: five held, one failed.** P1 (Montfort's counts reproduced in 4 of 5 years), P2, P5 and P6 held. P3 (at least 30% LLM_TEXT in one year of 2023-2025) held only in 2024, the one year seen during design. P4 failed: LLM_TEXT entries link to code *more* often than the others (87.5% against 81.3%), not 10 points less.
- The coding was done once by an AI agent. Every code has its quote in [coding.csv](census/2026-11/coding.csv), so anyone can check it.

## Next: a forward forecast of NaNoGenMo 2026 (pre-registered 2026-11-06)

[census/2026-forward/PREREGISTRATION.md](census/2026-forward/PREREGISTRATION.md) fixes five predictions about the 2026 edition while it is still running: at most 22 completed entries, at most 20% LLM_TEXT, LLM_OTHER at least as common as LLM_TEXT, a completion rate of at least 70%, and at least 80% linking to code. The read is on or after 2026-12-15.
