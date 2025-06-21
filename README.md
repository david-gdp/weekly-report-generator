# Accomplishment Summarizer

This tool provides a unified command-line interface for:
- Anonymizing (masking) accomplishment files
- Deanonymizing (unmasking) files
- Summarizing accomplishments using OpenRouter's LLM API
- Running a complete workflow: anonymize → summarize → deanonymize

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

Run the tool using:
```bash
python -m accomplishment_summarizer <command> [options]
```
Or, if you have a script entry point:
```bash
python accomplishment_tool.py <command> [options]
```

### Config File

The config file (`config.yaml` by default) should be placed in the same directory as this README.

Example template:
```yaml
organizations:
  - Organization Name 1
  - Organization Name 2
  # ...more organizations
projects:
  - Project A
  - Project B
  # ...more projects
people:
  - Name A
  - Name B
  # ...more people
repo:
  key: [github urls]
```

- The `organizations`, `projects`, and `people` sections list names to be anonymized or deanonymized.
- The `repo` section can be used to specify related GitHub repositories.

### Commands

#### 1. Anonymize (mask) a file
```bash
python -m accomplishment_summarizer anonymize input.md -o masked.md
```
- `-c config.yaml` (optional): Specify config file (default: `config.yaml`)

#### 2. Deanonymize (unmask) a file
```bash
python -m accomplishment_summarizer deanonymize masked.md -o unmasked.md
```
- `-c config.yaml` (optional): Specify config file (default: `config.yaml`)

#### 3. Summarize a file
```bash
python -m accomplishment_summarizer summarize input.md -o summary.md
```
- `-m <model>` (optional): Specify OpenRouter model (default: `google/gemini-2.5-flash-preview-05-20`)
- `-k <api_key>` (optional): Pass API key directly

#### 4. Complete workflow (anonymize → summarize → deanonymize)
```bash
python -m accomplishment_summarizer workflow input.md -o final_summary.md
```
- `-c config.yaml` (optional): Specify config file (default: `config.yaml`)
- `-m <model>` (optional): Specify OpenRouter model
- `-k <api_key>` (optional): Pass API key directly
- `--keep-temp` (optional): Keep temporary files

### Help
For detailed help and all options:
```bash
python -m accomplishment_summarizer --help
```

## Available Models

Popular models on OpenRouter:
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `meta-llama/llama-3.1-70b-instruct`
- `google/gemini-2.5-flash-preview-05-20` (default)

## Output

The tool generates a markdown summary organized by:
- Project/Organization sections
- Past tense accomplishments
- Key challenges encountered
- Other miscellaneous activities
