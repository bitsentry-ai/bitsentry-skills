# BitSentry Skills Repository

This repository contains **skills for BitSentry** to standardize development practices using Claude Code. It includes both **BitSentry-specific skills** tailored to our engineering workflows and **Anthropic's default example skills** that demonstrate general capabilities.

Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. They help standardize how we write specs, tests, and architecture using Claude.

**Website:** [bitsentry.ai](https://bitsentry.ai)

For more information about skills, check out:
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Equipping agents for the real world with Agent Skills](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

# About This Repository

This is a **fork of Anthropic's skills repository**, customized for BitSentry's development workflows. It contains:

1. **BitSentry-specific skills** - Custom skills for our engineering practices
2. **Anthropic's example skills** - Reference implementations for inspiration

Each skill is self-contained in its own directory with a `SKILL.md` file containing the instructions and metadata that Claude uses. The example skills from Anthropic are open source (Apache 2.0). BitSentry-specific skills are internal tools for our team.

**Note:** Anthropic's example skills are reference examples for inspiration and learning. They showcase general-purpose capabilities rather than organization-specific workflows.

## Disclaimer

**These skills are provided for demonstration and educational purposes only.** While some of these capabilities may be available in Claude, the implementations and behaviors you receive from Claude may differ from what is shown in these examples. These examples are meant to illustrate patterns and possibilities. Always test skills thoroughly in your own environment before relying on them for critical tasks.

# BitSentry Skills

Skills specifically designed for BitSentry's engineering workflows and development practices.

## Installing BitSentry Skills

You can install BitSentry skills using one of these methods:

### Method 1: Direct Download (All Claude Interfaces)

Download the `.skill` file and upload it via Claude's skills interface:

```bash
# BitSentry Backend Spec Writer
curl -L https://raw.githubusercontent.com/bitsentry-ai/bitsentry-skills/main/bitsentry-backend-spec-writer/bitsentry-backend-spec-writer.skill -o bitsentry-backend-spec-writer.skill
```

Then upload the downloaded `.skill` file to Claude via the skills interface.

### Method 2: Manual Installation (Claude Code)

For Claude Code users, you can manually install skills by placing them in the `~/.claude/skills/` directory:

```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Download and extract bitsentry-backend-spec-writer
curl -L https://raw.githubusercontent.com/bitsentry-ai/bitsentry-skills/main/bitsentry-backend-spec-writer/bitsentry-backend-spec-writer.skill -o /tmp/bitsentry-backend-spec-writer.skill
unzip /tmp/bitsentry-backend-spec-writer.skill -d ~/.claude/skills/

# Clean up temporary files
rm /tmp/*.skill
```

After installation, restart Claude Code to load the new skills. They will be automatically available in your Claude Code sessions.

### Available BitSentry Skills

- **bitsentry-backend-spec-writer** - Write comprehensive backend engineering design specs following DDD and hexagonal architecture patterns

# Anthropic Example Skills

This repository includes a diverse collection of example skills demonstrating different capabilities:

## Creative & Design
- **algorithmic-art** - Create generative art using p5.js with seeded randomness, flow fields, and particle systems
- **canvas-design** - Design beautiful visual art in .png and .pdf formats using design philosophies
- **slack-gif-creator** - Create animated GIFs optimized for Slack's size constraints

## Development & Technical
- **artifacts-builder** - Build complex claude.ai HTML artifacts using React, Tailwind CSS, and shadcn/ui components
- **mcp-server** - Guide for creating high-quality MCP servers to integrate external APIs and services
- **webapp-testing** - Test local web applications using Playwright for UI verification and debugging

## Enterprise & Communication
- **brand-guidelines** - Apply Anthropic's official brand colors and typography to artifacts
- **internal-comms** - Write internal communications like status reports, newsletters, and FAQs
- **theme-factory** - Style artifacts with 10 pre-set professional themes or generate custom themes on-the-fly

## Meta Skills
- **skill-creator** - Guide for creating effective skills that extend Claude's capabilities
- **template-skill** - A basic template to use as a starting point for new skills

# Document Skills

The `document-skills/` subdirectory contains skills that Anthropic developed to help Claude create various document file formats. These skills demonstrate advanced patterns for working with complex file formats and binary data:

- **docx** - Create, edit, and analyze Word documents with support for tracked changes, comments, formatting preservation, and text extraction
- **pdf** - Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms
- **pptx** - Create, edit, and analyze PowerPoint presentations with support for layouts, templates, charts, and automated slide generation
- **xlsx** - Create, edit, and analyze Excel spreadsheets with support for formulas, formatting, data analysis, and visualization

**Important Disclaimer:** These document skills are point-in-time snapshots and are not actively maintained or updated. Versions of these skills ship pre-included with Claude. They are primarily intended as reference examples to illustrate how Anthropic approaches developing more complex skills that work with binary file formats and document structures.

# Using These Skills

## For BitSentry Team Members

### Claude Code
For **BitSentry-specific skills**, download the skill files using the curl commands above, then upload them to Claude Code via the skills interface.

For **Anthropic's example skills**, you can register the original Anthropic repository as a Claude Code Plugin marketplace:
```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

After installing a skill, you can use it by mentioning it. For example: "Use the bitsentry-backend-spec-writer skill to create a new engineering spec for the authentication system."

### Claude.ai

**Anthropic's example skills** are already available to paid plans in Claude.ai.

For **BitSentry-specific skills**, download them using the curl commands above, then follow the instructions in [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_a4222fa77b) to upload custom skills.

### Claude API

You can upload BitSentry's custom skills via the Claude API. See the [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill) for more information.

# Creating a Basic Skill

Skills are simple to create - just a folder with a `SKILL.md` file containing YAML frontmatter and instructions. You can use the **template-skill** in this repository as a starting point:

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

The frontmatter requires only two fields:
- `name` - A unique identifier for your skill (lowercase, hyphens for spaces)
- `description` - A complete description of what the skill does and when to use it

The markdown content below contains the instructions, examples, and guidelines that Claude will follow. For more details, see [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills).

# Partner Skills

Skills are a great way to teach Claude how to get better at using specific pieces of software. As we see awesome example skills from partners, we may highlight some of them here:

- **Notion** - [Notion Skills for Claude](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0)