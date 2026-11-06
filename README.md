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
