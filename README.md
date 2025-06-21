# Accomplishment Summarizer

This tool uses OpenRouter's LLM API to summarize weekly accomplishments organized by project in past tense.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get an OpenRouter API key from https://openrouter.ai/

3. Set your API key as an environment variable:
```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

## Usage

### Basic usage:
```bash
python summarize_accomplishment.py accomplishment_masked.md
```

### With custom output file:
```bash
python summarize_accomplishment.py accomplishment_masked.md -o weekly_summary.md
```

### Save the generated prompt:
```bash
python summarize_accomplishment.py accomplishment_masked.md --save-prompt
```

### Print summary to console:
```bash
python summarize_accomplishment.py accomplishment_masked.md --print-summary
```

### Use different model:
```bash
python summarize_accomplishment.py accomplishment_masked.md -m "openai/gpt-4"
```

### Pass API key directly:
```bash
python summarize_accomplishment.py accomplishment_masked.md -k "your_api_key"
```

## Available Models

Popular models on OpenRouter:
- `anthropic/claude-3.5-sonnet` (default)
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `meta-llama/llama-3.1-70b-instruct`

## Output

The tool generates a markdown summary organized by:
- Project/Organization sections
- Past tense accomplishments
- Key challenges encountered
- Other miscellaneous activities
