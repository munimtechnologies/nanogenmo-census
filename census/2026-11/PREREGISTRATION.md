# Pre-registration: which methods did NaNoGenMo's finished entries use, 2013-2025?

Written and committed on 2026-11-06 (UTC), before `census.py` read any issue or comment for this census. The git commit time of this file is the registration time. `census.py` waits until this file is on `main`, then records its first commit time in its output next to the time the data was read. Made by MV2 of Munim, Inc., with AI agents working in his name. Text and data CC BY 4.0; code (`census.py`, `test_census.py`) Apache-2.0.

## Why

National Novel Generation Month (NaNoGenMo) has run every November since 2013: write code that generates a "novel" of 50,000 words or more, and share the novel and the code. Its yearly GitHub repositories are one of the longest public records of how hobbyists and artists generate text. In "A Glance at NaNoGenMo 2024" (2025-01-02), Nick Montfort counted completed projects (56 in 2020 and 2021, 33 in 2022, 23 in 2023, 22 in 2024) and suggested that more projects now use proprietary commercial language models whose code cannot be shared. On 2026-11-01 a participant wrote in [the 2026 repository](https://github.com/NaNoGenMo/2026/issues/6) that "the LLM space has largely made this field much less fun to be around in general" and that interest in the project is "dropping off". Searches on 2026-11-06 found yearly roundups of single entries and those counts, but no count, year by year, of which generation methods finished entries use. This census provides that count for 13 years, from public data, with every entry listed.

## Frame (fixed now)

Every issue labelled `completed` (case-insensitive) at fetch time, pull requests excluded, in these 13 repositories: `dariusk/NaNoGenMo` (2013), `dariusk/NaNoGenMo-2014`, `dariusk/NaNoGenMo-2015`, and `NaNoGenMo/2016` to `NaNoGenMo/2025`. The 2026 edition is still running and is not included. All issues (without pull requests and issues labelled `admin`) are also counted, as the number of issues opened that year.

## What is read

GitHub's public REST API, without a token: every issue and every issue comment of each repository, oldest first. For each completed entry, its text is its title, its body and every comment by the issue's opener posted before 1 February of the following year. Comments are matched to the opener by a salted hash; no login is stored or published. The cache keeps only the fields listed in `census.py` (`slim_issue`, `slim_comment`).

## Measures (fixed now; the term lists are in `census.py`, `FAMILIES`)

Deterministic flags on each entry's text, matched case-insensitively:

- **LLM term**: a pretrained language-model term (GPT in any form including ChatGPT, OpenAI, LLM, "language model", transformer, Hugging Face, BERT/RoBERTa, Llama/Ollama/Alpaca/Vicuna, Mistral/Mixtral, Claude/Anthropic, Gemini, and Qwen, Gemma, DeepSeek, davinci, NovelAI, Sudowrite, Kobold, Copilot, Phi-2/3/4).
- **Earlier neural**: RNN (including char-rnn, torch-rnn, textgenrnn), LSTM, "neural net(work)", seq2seq.
- **Markov**, **Tracery or context-free grammar**, **Project Gutenberg**.
- **Code link**: a link in the body or the opener's comments to a code repository or sandbox (a two-part github.com path other than NaNoGenMo's own repositories, issues, pull requests, discussions and wikis; gist, GitLab, Codeberg, Bitbucket, sourcehut, Glitch, Replit, Observable, CodePen, Colab, p5.js editor, JSFiddle, NotABug, SourceForge, CodeSandbox) or to a source file (`.py`, `.js` and the other extensions in `CODE_EXT`).
- **Inline code**: a fenced code block with at least five non-empty lines (reported, not used in a prediction, because fences are also used for sample output).

**Primary coding (language-model use).** A term is a mention, not a use. After the fetch, an AI agent reads every snippet in `snippets.jsonl` (200 characters either side of each language-model term, up to six per entry) and, where the snippets do not settle it, the entry's issue page, and codes each entry with an LLM term as:

- **LLM_TEXT**: a pretrained neural language model (GPT-2 or later, a BERT-family model, any chat model, hosted or local) produces or rewrites text that appears in the submitted novel.
- **LLM_OTHER**: a language model was used, but none of its output text appears in the novel (it wrote or designed the code, made a plan, ranked or chose items, embedded text for search, judged output).
- **MENTION_ONLY**: no language model was used (criticism or comparison, "this is not an LLM", a question, the term inside a title or source text, a person named Claude or Bert, Gemini as a star sign, llamas).
- **UNCLEAR**: the available text does not say.

Entries with no LLM term are coded NO_MENTION and count as not LLM_TEXT. The coding file quotes the words each code rests on and is published with the result.

## Predictions

- **P1.** The `completed` counts reproduce Montfort's figures (2020: 56, 2021: 56, 2022: 33, 2023: 23, 2024: 22) exactly in at least four of the five years.
- **P2.** In every year from 2013 to 2018, at most 10% of completed entries carry an LLM term.
- **P3.** In at least one of 2023, 2024 and 2025, at least 30% of completed entries are coded LLM_TEXT.
- **P4.** Pooled over 2023-2025, the share of LLM_TEXT entries with a code link is at least 10 percentage points lower than the share among the other completed entries.
- **P5.** The year with the highest share of completed entries carrying an earlier-neural term falls in 2016-2019 (if several years tie, all of them must).
- **P6.** Every year from 2022 to 2025 has fewer completed entries than every year from 2014 to 2021.

P1, P2, P5 and P6 are graded by `census.py`; P3 and P4 after the primary coding. Every prediction is reported as held or not, whatever the result.

**What was seen before writing this.** While designing the census, one API listing of the 2024 repository's completed issues was read: 22 issues, of which a quick read found 7 whose body names a language-model term. So P1's 2024 value and the 2024 part of P3 are not blind; 2013-2023 and 2025 were not looked at, apart from the label names of four repositories and the repository list.

## Not tested (reported as exploratory)

- Completion rate (completed / issues opened) by year.
- Markov, Tracery and Gutenberg shares by year.
- Code-link shares by year, and by LLM term (mention-based) in 2023-2025.
- How many entries are coded LLM_OTHER and MENTION_ONLY, which tells how far term counts overstate use.

## Limits, stated now

- The `completed` label is the organisers' own judgement; finished entries without it are not counted, and labels can change after the event.
- Only the opener's own words in the issue are read. A method described only in a linked repository, a blog post or the novel itself is missed, so every share is a lower bound on mentions.
- Term matching over-counts (critiques, names) and under-counts (model names not on the list). The primary coding reads every LLM mention; the other families are mention counts only.
- A code link is a link to a code host, sandbox or source file; whether it still works or holds complete code is not checked.
- The primary coding is done by AI agents, not by people. Every coded entry is listed with its quote so that anyone can check it.
