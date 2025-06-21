#!/usr/bin/env python3
"""
Anonymize Accomplishment Script

This script masks and unmasks organization names, project names, and people names
in accomplishment files based on a YAML configuration file.
It creates mappings between real names and placeholder names for anonymization.
"""

import argparse
import re
from pathlib import Path

import yaml


def load_anonymize_config(file_path):
    """Load the anonymization configuration from a YAML file."""
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)

    # Ensure all required sections exist
    if not isinstance(config, dict):
        raise ValueError("Configuration file must contain a YAML dictionary")

    # Check if config has the new nested structure under 'anonymize' key
    if "anonymize" in config:
        anonymize_config = config["anonymize"]
        organizations = anonymize_config.get("organizations", [])
        projects = anonymize_config.get("projects", [])
        people = anonymize_config.get("people", [])
    else:
        # Fallback to old flat structure for backward compatibility
        organizations = config.get("organizations", [])
        projects = config.get("projects", [])
        people = config.get("people", [])

    return {"organizations": organizations, "projects": projects, "people": people}


def load_anonymize_list(file_path):
    """Load the list of project names to anonymize from a text file (legacy support)."""
    with open(file_path, "r") as f:
        return [
            line.strip() for line in f if line.strip() and not line.startswith("//")
        ]


def create_mask_mapping(config):
    """Create a mapping from real names to masked placeholders."""
    mapping = {}

    # Map organizations
    for i, org in enumerate(config["organizations"]):
        mapping[org] = f"<Organization {i + 1}>"

    # Map projects
    for i, project in enumerate(config["projects"]):
        mapping[project] = f"<Project {i + 1}>"

    # Map people
    for i, person in enumerate(config["people"]):
        mapping[person] = f"<Person {i + 1}>"

    return mapping


def create_unmask_mapping(config):
    """Create a mapping from masked placeholders to real names."""
    mapping = {}

    # Map organizations
    for i, org in enumerate(config["organizations"]):
        mapping[f"<Organization {i + 1}>"] = org
        mapping[f"Organization {i + 1}"] = org  # Support both < and no <>

    # Map projects
    for i, project in enumerate(config["projects"]):
        mapping[f"<Project {i + 1}>"] = project
        mapping[f"Project {i + 1}"] = project  # Support both < and no <>

    # Map people
    for i, person in enumerate(config["people"]):
        mapping[f"<Person {i + 1}>"] = person
        mapping[f"Person {i + 1}"] = person

    return mapping


def create_legacy_mask_mapping(project_names):
    """Create a mapping from real project names to masked placeholders (legacy support)."""
    mapping = {}
    for i, name in enumerate(project_names):
        mapping[name] = f"<Project {i + 1}>"
    return mapping


def create_legacy_unmask_mapping(project_names):
    """Create a mapping from masked placeholders to real project names (legacy support)."""
    mapping = {}
    for i, name in enumerate(project_names):
        mapping[f"<Project {i + 1}>"] = name
    return mapping


def apply_anonymization(content, mapping):
    """Apply anonymization mapping to content."""
    result = content
    for original, replacement in mapping.items():
        # For placeholders with < and >, use exact matching
        if original.startswith("<") and original.endswith(">"):
            pattern = re.escape(original)
        else:
            # Use word boundaries for regular project names
            pattern = r"\b" + re.escape(original) + r"\b"
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def mask_accomplishment(input_file, output_file, config_file):
    """Mask organization, project, and people names in accomplishment file."""
    # Determine if using YAML config or legacy text file
    if config_file.endswith(".yaml") or config_file.endswith(".yml"):
        # Load YAML configuration
        config = load_anonymize_config(config_file)
        mask_mapping = create_mask_mapping(config)

        print(f"📋 Applied {len(mask_mapping)} name mappings:")
        print(f"  • Organizations: {len(config['organizations'])}")
        print(f"  • Projects: {len(config['projects'])}")
        print(f"  • People: {len(config['people'])}")
    else:
        # Legacy text file support
        project_names = load_anonymize_list(config_file)
        mask_mapping = create_legacy_mask_mapping(project_names)
        print(f"📋 Applied {len(mask_mapping)} project name mappings (legacy mode)")

    # Read input file
    with open(input_file, "r") as f:
        content = f.read()

    # Apply masking
    masked_content = apply_anonymization(content, mask_mapping)

    # Write to output file
    with open(output_file, "w") as f:
        f.write(masked_content)

    print(f"✅ Masked accomplishment saved to: {output_file}")

    # Show mapping for reference
    print("\n🔒 Masking mappings applied:")
    for original, masked in mask_mapping.items():
        print(f"  {original} → {masked}")


def unmask_accomplishment(input_file, output_file, config_file):
    """Unmask organization, project, and people names in accomplishment file."""
    # Determine if using YAML config or legacy text file
    if config_file.endswith(".yaml") or config_file.endswith(".yml"):
        # Load YAML configuration
        config = load_anonymize_config(config_file)
        unmask_mapping = create_unmask_mapping(config)

        print(f"📋 Applied {len(unmask_mapping)} name mappings:")
        print(f"  • Organizations: {len(config['organizations'])}")
        print(f"  • Projects: {len(config['projects'])}")
        print(f"  • People: {len(config['people'])}")
    else:
        # Legacy text file support
        project_names = load_anonymize_list(config_file)
        unmask_mapping = create_legacy_unmask_mapping(project_names)
        print(f"📋 Applied {len(unmask_mapping)} project name mappings (legacy mode)")

    # Read input file
    with open(input_file, "r") as f:
        content = f.read()

    # Apply unmasking
    unmasked_content = apply_anonymization(content, unmask_mapping)

    # Write to output file
    with open(output_file, "w") as f:
        f.write(unmasked_content)

    print(f"✅ Unmasked accomplishment saved to: {output_file}")

    # Show mapping for reference
    print("\n🔓 Unmasking mappings applied:")
    for masked, original in unmask_mapping.items():
        print(f"  {masked} → {original}")


def main():
    parser = argparse.ArgumentParser(
        description="Anonymize or deanonymize accomplishment files"
    )
    parser.add_argument(
        "action",
        choices=["mask", "unmask"],
        help="Action to perform: mask (anonymize) or unmask (deanonymize)",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="accomplishment.md",
        help="Input accomplishment file (default: accomplishment.md)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file (default: accomplishment_masked.md for mask, accomplishment_unmasked.md for unmask)",
    )
    parser.add_argument(
        "-c",
        "--config",
        default="anonymize_config.yaml",
        help="Configuration file containing entities to anonymize (default: anonymize_config.yaml). Supports YAML format for organizations/projects/people or legacy text format for projects only.",
    )

    args = parser.parse_args()

    # Set default output file based on action
    if not args.output:
        if args.action == "mask":
            args.output = "accomplishment_masked.md"
        else:
            args.output = "accomplishment_unmasked.md"

    # Check if input files exist
    if not Path(args.input).exists():
        print(f"❌ Error: Input file '{args.input}' not found")
        return 1

    if not Path(args.config).exists():
        print(f"❌ Error: Configuration file '{args.config}' not found")
        return 1

    try:
        if args.action == "mask":
            mask_accomplishment(args.input, args.output, args.config)
        else:
            unmask_accomplishment(args.input, args.output, args.config)

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
