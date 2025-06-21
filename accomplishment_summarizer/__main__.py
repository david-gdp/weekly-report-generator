#!/usr/bin/env python3
"""
Accomplishment Tool - Unified CLI for anonymizing and summarizing accomplishments

This script provides a unified interface for:
1. Anonymizing accomplishment files (masking/unmasking)
2. Summarizing accomplishments using LLM
3. Combined workflow: anonymize -> summarize -> unmask
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Import functionality from existing modules
from accomplishment_summarizer.anonymize_accomplishment import (
    apply_anonymization,
    create_legacy_mask_mapping,
    create_legacy_unmask_mapping,
    create_mask_mapping,
    create_unmask_mapping,
    load_anonymize_config,
    load_anonymize_list,
)
from accomplishment_summarizer.summarize_accomplishment import AccomplishmentSummarizer


class AccomplishmentTool:
    """Unified tool for accomplishment processing."""

    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.temp_files = []  # Track temporary files for cleanup

    def cleanup_temp_files(self):
        """Clean up temporary files created during processing."""
        for temp_file in self.temp_files:
            try:
                if Path(temp_file).exists():
                    os.remove(temp_file)
                    print(f"🧹 Cleaned up temporary file: {temp_file}")
            except Exception as e:
                print(f"⚠️  Warning: Could not remove temp file {temp_file}: {e}")

    def anonymize_file(self, input_file, output_file, action="mask"):
        """Anonymize or deanonymize a file."""
        print(
            f"{'🔒 Anonymizing' if action == 'mask' else '🔓 Deanonymizing'} file: {input_file}"
        )

        # Check if input files exist
        if not Path(input_file).exists():
            raise FileNotFoundError(f"Input file '{input_file}' not found")

        if not Path(self.config_file).exists():
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found"
            )

        # Determine if using YAML config or legacy text file
        if self.config_file.endswith(".yaml") or self.config_file.endswith(".yml"):
            # Load YAML configuration
            config = load_anonymize_config(self.config_file)
            if action == "mask":
                mapping = create_mask_mapping(config)
            else:
                mapping = create_unmask_mapping(config)

            print(f"📋 Applied {len(mapping)} name mappings:")
            print(f"  • Organizations: {len(config['organizations'])}")
            print(f"  • Projects: {len(config['projects'])}")
            print(f"  • People: {len(config['people'])}")
        else:
            # Legacy text file support
            project_names = load_anonymize_list(self.config_file)
            if action == "mask":
                mapping = create_legacy_mask_mapping(project_names)
            else:
                mapping = create_legacy_unmask_mapping(project_names)
            print(f"📋 Applied {len(mapping)} project name mappings (legacy mode)")

        # Read input file
        with open(input_file, "r") as f:
            content = f.read()

        # Apply anonymization
        processed_content = apply_anonymization(content, mapping)

        # Write to output file
        with open(output_file, "w") as f:
            f.write(processed_content)

        print(
            f"✅ {'Masked' if action == 'mask' else 'Unmasked'} accomplishment saved to: {output_file}"
        )
        return output_file

    def summarize_file(
        self,
        input_file,
        output_file=None,
        model="google/gemini-2.5-flash-preview-05-20",
        api_key=None,
    ):
        """Summarize an accomplishment file."""
        print(f"📝 Summarizing file: {input_file}")

        try:
            summarizer = AccomplishmentSummarizer(api_key=api_key, model=model)
            result = summarizer.summarize(
                input_file=input_file, output_file=output_file
            )

            print(f"✅ Summary saved to: {result['summary_file']}")
            return result["summary_file"]

        except Exception as e:
            raise Exception(f"Summarization failed: {e}")

    def process_workflow(
        self,
        input_file,
        final_output=None,
        model="google/gemini-2.5-flash-preview-05-20",
        api_key=None,
        keep_temp=False,
    ):
        """Complete workflow: mask -> summarize -> unmask."""
        print("🔄 Starting complete workflow: mask -> summarize -> unmask")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Step 1: Mask the input file
            masked_file = f"temp_masked_{timestamp}.md"
            self.temp_files.append(masked_file)
            self.anonymize_file(input_file, masked_file, action="mask")

            # Step 2: Summarize the masked file
            masked_summary_file = f"temp_summary_masked_{timestamp}.md"
            self.temp_files.append(masked_summary_file)
            self.summarize_file(
                masked_file, masked_summary_file, model=model, api_key=api_key
            )

            # Step 3: Unmask the summary
            if final_output is None:
                final_output = f"accomplishment_summary_final_{timestamp}.md"

            self.anonymize_file(masked_summary_file, final_output, action="unmask")

            print(f"🎉 Complete workflow finished! Final output: {final_output}")

            # Cleanup temporary files unless requested to keep them
            if not keep_temp:
                self.cleanup_temp_files()

            return final_output

        except Exception as e:
            # Cleanup on error
            if not keep_temp:
                self.cleanup_temp_files()
            raise e


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Unified tool for accomplishment anonymization and summarization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Anonymize a file
  python accomplishment_tool.py anonymize input.md -o masked.md

  # Summarize a file
  python accomplishment_tool.py summarize input.md -o summary.md

  # Complete workflow (mask -> summarize -> unmask)
  python accomplishment_tool.py workflow input.md -o final_summary.md

  # Deanonymize a file
  python accomplishment_tool.py deanonymize masked.md -o unmasked.md
        """,
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Anonymize command
    anonymize_parser = subparsers.add_parser(
        "anonymize", help="Anonymize (mask) accomplishment file"
    )
    anonymize_parser.add_argument("input", help="Input accomplishment file")
    anonymize_parser.add_argument(
        "-o", "--output", help="Output file (default: accomplishment_masked.md)"
    )
    anonymize_parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Configuration file (default: config.yaml)",
    )

    # Deanonymize command
    deanonymize_parser = subparsers.add_parser(
        "deanonymize", help="Deanonymize (unmask) accomplishment file"
    )
    deanonymize_parser.add_argument("input", help="Input masked file")
    deanonymize_parser.add_argument(
        "-o", "--output", help="Output file (default: accomplishment_unmasked.md)"
    )
    deanonymize_parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Configuration file (default: config.yaml)",
    )

    # Summarize command
    summarize_parser = subparsers.add_parser(
        "summarize", help="Summarize accomplishment file"
    )
    summarize_parser.add_argument("input", help="Input accomplishment file")
    summarize_parser.add_argument(
        "-o", "--output", help="Output file (default: auto-generated)"
    )
    summarize_parser.add_argument(
        "-m",
        "--model",
        default="google/gemini-2.5-flash-preview-05-20",
        help="OpenRouter model to use",
    )
    summarize_parser.add_argument("-k", "--api-key", help="OpenRouter API key")

    # Workflow command
    workflow_parser = subparsers.add_parser(
        "workflow", help="Complete workflow: anonymize -> summarize -> deanonymize"
    )
    workflow_parser.add_argument("input", help="Input accomplishment file")
    workflow_parser.add_argument(
        "-o", "--output", help="Final output file (default: auto-generated)"
    )
    workflow_parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Configuration file (default: config.yaml)",
    )
    workflow_parser.add_argument(
        "-m",
        "--model",
        default="google/gemini-2.5-flash-preview-05-20",
        help="OpenRouter model to use",
    )
    workflow_parser.add_argument("-k", "--api-key", help="OpenRouter API key")
    workflow_parser.add_argument(
        "--keep-temp", action="store_true", help="Keep temporary files"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        tool = AccomplishmentTool(config_file=getattr(args, "config", "config.yaml"))

        if args.command == "anonymize":
            output = args.output or "accomplishment_masked.md"
            tool.anonymize_file(args.input, output, action="mask")

        elif args.command == "deanonymize":
            output = args.output or "accomplishment_unmasked.md"
            tool.anonymize_file(args.input, output, action="unmask")

        elif args.command == "summarize":
            tool.summarize_file(
                args.input, args.output, model=args.model, api_key=args.api_key
            )

        elif args.command == "workflow":
            tool.process_workflow(
                args.input,
                args.output,
                model=args.model,
                api_key=args.api_key,
                keep_temp=args.keep_temp,
            )

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
