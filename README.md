# Quotable Random Quote CLI

A tiny Python CLI that fetches and prints a random quote from the Quotable API (`https://api.quotable.io/random`).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run with a single command (no arguments):

```bash
python -m quotable_cli
```

Or run the included helper script:

```bash
python quote.py
```

Run it again to get another quote.

## What it prints

- Quote text
- Author
- Optional tags (when provided by the API)

If your terminal supports it, the output uses light ANSI coloring.

## Error handling

If the API can't be reached, times out, or returns an error, the CLI exits gracefully and prints a helpful message to stderr.
