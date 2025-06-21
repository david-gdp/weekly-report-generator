#!/usr/bin/env python3
"""
Script to summarize accomplishments from markdown file using OpenRouter LLM API.
Organizes accomplishments by project and converts to past tense.
"""

import argparse
import os
from datetime import datetime
from typing import Any, Dict

import requests


class AccomplishmentSummarizer:
    def __init__(self, api_key: str = None, model: str = "anthropic/claude-3.5-sonnet"):
        """
        Initialize the summarizer with OpenRouter API configuration.

        Args:
            api_key: OpenRouter API key (if None, will try to get from env)
            model: Model to use for summarization
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Set OPENROUTER_API_KEY env var or pass as parameter."
            )

        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def read_accomplishment_file(self, file_path: str) -> str:
        """Read the accomplishment markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Accomplishment file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file: {e}")

    def generate_prompt(self, accomplishment_text: str) -> str:
        """
        Generate a comprehensive prompt for LLM to summarize accomplishments.

        Args:
            accomplishment_text: Raw accomplishment text from markdown

        Returns:
            Formatted prompt for the LLM
        """
        prompt = f"""
You are a professional technical writer tasked with summarizing weekly accomplishments. Please analyze the following weekly accomplishment report and provide a well-organized summary.

**Instructions:**
1. Group all accomplishments by project/organization
2. Convert all tasks to past tense
3. Merge similar or related tasks into cohesive statements
4. Use clear, professional language
5. Maintain technical accuracy
6. Include any issues/challenges encountered
7. Format the output as clean markdown, each project/organization in a numbered list
8. Use numbered list (with real numbers) for sub-tasks and accomplishments

**Input Accomplishment Report:**
```
{accomplishment_text}
```

**Required Output Format:**
```markdown
# Weekly Accomplishment Summary

1. [Project/Organization Name 1]
   1. [Summarized accomplishment in past tense]
   2. [Another accomplishment]
      1. [Sub-task or related accomplishment]
      2. [Another sub-task]
   3. [Any challenges or issues faced]

2. [Project/Organization Name 2]
   1. [Summarized accomplishment in past tense]
   2. [Another accomplishment]

3. Other Activities
   1. [Any miscellaneous tasks or activities]

4. Key Challenges
   1. [List any significant issues or blockers encountered]
```

**Guidelines for summarization:**
- Combine related sub-tasks into broader accomplishments
- Focus on outcomes and deliverables
- Mention specific technologies, tools, or metrics when relevant
- Keep bullet points concise but informative
- Ensure all accomplishments are in past tense
- Group Docker, database, testing, and infrastructure work appropriately
- Highlight performance improvements, data processing, and system optimizations
- Persist the tag inside the content like <Project 1>, <Project 2> for easy reference

Please provide the summary now:
"""
        return prompt

    def call_openrouter_api(self, prompt: str) -> str:
        """
        Make API call to OpenRouter to get the summary.

        Args:
            prompt: The formatted prompt for summarization

        Returns:
            The LLM's response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/accomplishment-summarizer",
            "X-Title": "Accomplishment Summarizer",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000,
            "top_p": 0.9,
        }

        try:
            response = requests.post(
                self.base_url, headers=headers, json=payload, timeout=60
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except KeyError as e:
            raise Exception(f"Unexpected API response format: {e}")
        except Exception as e:
            raise Exception(f"Error calling OpenRouter API: {e}")

    def save_summary(self, summary: str, output_path: str = None) -> str:
        """
        Save the generated summary to a file.

        Args:
            summary: The generated summary text
            output_path: Path to save the summary (if None, auto-generate)

        Returns:
            Path where the summary was saved
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"accomplishment_summary_{timestamp}.md"

        try:
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(summary)
            return output_path
        except Exception as e:
            raise Exception(f"Error saving summary: {e}")

    def summarize(
        self, input_file: str, output_file: str = None, save_prompt: bool = False
    ) -> Dict[str, Any]:
        """
        Complete summarization process.

        Args:
            input_file: Path to the accomplishment markdown file
            output_file: Path to save the summary (optional)
            save_prompt: Whether to save the generated prompt

        Returns:
            Dictionary with summary, prompt, and file paths
        """
        print(f"Reading accomplishment file: {input_file}")
        accomplishment_text = self.read_accomplishment_file(input_file)

        print("Generating prompt...")
        prompt = self.generate_prompt(accomplishment_text)

        if save_prompt:
            prompt_file = "generated_prompt.txt"
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt)
            print(f"Prompt saved to: {prompt_file}")

        print(f"Calling OpenRouter API with model: {self.model}")
        summary = self.call_openrouter_api(prompt)

        print("Saving summary...")
        summary_path = self.save_summary(summary, output_file)

        print(f"Summary saved to: {summary_path}")

        return {
            "summary": summary,
            "prompt": prompt,
            "summary_file": summary_path,
            "input_file": input_file,
        }


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Summarize accomplishments using OpenRouter LLM"
    )
    parser.add_argument("input_file", help="Path to accomplishment markdown file")
    parser.add_argument("-o", "--output", help="Output file path for summary")
    parser.add_argument(
        "-m",
        "--model",
        default="google/gemini-2.5-flash-preview-05-20",
        help="OpenRouter model to use",
    )
    parser.add_argument("-k", "--api-key", help="OpenRouter API key")
    parser.add_argument(
        "--save-prompt", action="store_true", help="Save the generated prompt to file"
    )
    parser.add_argument(
        "--print-summary", action="store_true", help="Print summary to console"
    )

    args = parser.parse_args()

    try:
        summarizer = AccomplishmentSummarizer(api_key=args.api_key, model=args.model)
        result = summarizer.summarize(
            input_file=args.input_file,
            output_file=args.output,
            save_prompt=args.save_prompt,
        )

        if args.print_summary:
            print("\n" + "=" * 60)
            print("GENERATED SUMMARY:")
            print("=" * 60)
            print(result["summary"])

        print("\n✅ Summarization completed successfully!")
        print(f"📁 Summary saved to: {result['summary_file']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
