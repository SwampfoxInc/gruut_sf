# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Gruut is a tokenizer, text cleaner, and IPA phonemizer for 14 human languages with SSML support. It's used in text-to-speech pipelines. Python 3.6+, setuptools-based.

## Commands

```bash
# Lint & type check (flake8, pylint, mypy, black --check, isort --check)
make check

# Auto-format (black + isort)
make reformat

# Run tests with coverage
make test

# Run tests directly (faster, no coverage)
PYTHONPATH="." python -m pytest tests/

# Run a single test
PYTHONPATH="." python -m pytest tests/test_en.py::EnglishTestCase::test_pos -v

# Install (creates .venv)
make install
```

Note: `gruut-lang-*` directories must be on `PYTHONPATH` for language-specific tests (the `scripts/run-tests.sh` script handles this automatically).

## Architecture

### Graph-based text processing

The core abstraction is a **directed graph** (NetworkX) built from input text or SSML. Processing flows through graph nodes:

`SpeakNode → ParagraphNode → SentenceNode → WordNode/BreakWordNode/PunctuationWordNode`

The `TextProcessor` class (`gruut/text_processor.py`, ~2900 lines) orchestrates the full pipeline: tokenization → number/date/currency verbalization → phonemization → post-processing. It uses DFS traversal over the graph to emit `Sentence` objects containing `Word` objects.

### Language system

`gruut/lang.py` (~3000 lines) defines `get_settings()` which returns a `TextProcessorSettings` dataclass for each language. Each language configures break characters, punctuation sets, number/date formats, and pre/post-processing callbacks.

Language data (lexicon DBs, CRF models) lives in separate `gruut-lang-*` packages at the repo root. These are resolved at runtime via installed packages, `~/.config/gruut/`, or `search_dirs`.

### Phonemization pipeline

1. **Lexicon lookup** (`gruut/phonemize.py`): SQLite `lexicon.db` with word transforms (lowercase, strip punctuation) as fallbacks
2. **G2P model** (`gruut/g2p.py`): CRF-based grapheme-to-phoneme for unknown words
3. **POS tagging** (`gruut/pos.py`): CRF-based part-of-speech (English, French)

All three use lazy loading (`Delayed*` wrapper classes) to defer model loading until first use.

### Key data structures

Defined in `gruut/const.py`:
- `Word`: text, phonemes, POS tag, flags (is_spoken, is_punctuation, is_break), pause timings
- `Sentence`: list of Words, text, language, voice, SSML marks
- `TextProcessorSettings`: full language configuration (breaks, punctuation, phonemizer, G2P, POS tagger, pre/post-process hooks)

### Public API

```python
from gruut import sentences
for sentence in sentences("Hello world", lang="en-us"):
    for word in sentence:
        print(word.text, word.phonemes)
```

CLI entry point: `gruut/__main__.py` — outputs JSONL by default, CSV with `--csv`.

### Thread safety

`TextProcessor` instances are cached in thread-local storage with an `RLock` for the cache itself (`gruut/__init__.py`).

## Code style

- **Black** (88-char lines), **isort** (mode 3), **flake8**, **pylint**, **mypy**
- Config in `setup.cfg`, `.pylintrc`, `mypy.ini`, `.isort.cfg`
- Tests use `unittest.TestCase` style with pytest runner
