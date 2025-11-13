# Claude Workflow Guide for Skills Repository

This document guides future Claude instances on how to maintain and manage the BitSentry Skills Repository effectively.

## Repository Overview

This repository contains:
- **BitSentry-specific skills** (root level) - Custom internal tools like `bitsentry-backend-spec-writer`
- **Anthropic example skills** - Reference implementations (unchanged)

## Core Principles

### 1. SKILL.md vs README.md

**CRITICAL DISTINCTION:**

- **SKILL.md** = The actual skill that Claude loads and executes
  - Contains instructions for Claude to follow
  - Loaded into context when skill triggers
  - Changes require rebuilding the `.skill` file

- **README.md** = Documentation for humans
  - Installation instructions
  - Usage examples
  - Feature descriptions
  - Changes do NOT require rebuilding the `.skill` file

**Rule of Thumb:**
- If you modify `SKILL.md` or any bundled resources → Rebuild `.skill` file
- If you only modify `README.md` → No rebuild needed

### 2. Diagram-First Documentation Philosophy

**For design specs and technical documentation:**

✅ **Use diagrams to explain, not code**
- Mermaid sequence diagrams for flows
- State machines for lifecycles
- Architecture diagrams for system design
- Entity-relationship diagrams for data

❌ **Avoid excessive code in specs**
- No full implementation code blocks
- No service classes or repository implementations
- No test code (testing strategy is optional)

**Acceptable code in specs:**
- Database schemas (DBML/SQL)
- API request/response examples
- Configuration examples

### 3. Required vs Optional Sections in Design Specs

**Required:**
- ✅ Review Table
- ✅ Approval Table
- ✅ Background/Context/Objective
- ✅ Database Design (if applicable)
- ✅ API Documentation (if applicable)
- ✅ State Machines (if applicable)

**Optional but beneficial:**
- Testing Strategy
- Rollback Plan
- Performance Benchmarks
- Monitoring & Alerting

## Common Workflows

### Workflow 1: Creating a New Skill

When a user asks you to create a new skill:

1. **Understand the use case**
   - Ask for concrete examples
   - Identify what scripts/references/assets are needed

2. **Initialize the skill** (if from scratch)
   ```bash
   python3 /Users/bitsentry/Projects/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>
   ```

3. **Develop the skill content**
   - Write SKILL.md with clear instructions
   - Add bundled resources (scripts, references, assets)
   - Create README.md for human documentation

4. **Add license**
   - BitSentry-specific skills → Proprietary LICENSE.txt
   - Open-source skills → Apache 2.0 LICENSE.txt
   - Add `license:` field in SKILL.md frontmatter

5. **Package the skill**
   ```bash
   python3 /Users/bitsentry/Projects/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> /tmp/
   mv /tmp/<skill-name>.zip <path/to/skill-folder>/<skill-name>.skill
   ```

6. **Update main README.md**
   - Add skill to the appropriate section
   - Include installation instructions
   - Add feature descriptions

### Workflow 2: Updating an Existing Skill

When modifying a skill, determine what changed:

#### Case A: SKILL.md or Bundled Resources Changed

**You MUST rebuild the `.skill` file:**

```bash
# 1. Make your changes to SKILL.md, scripts/, references/, or assets/

# 2. Remove old .skill file
rm <path/to/skill>/<skill-name>.skill

# 3. Repackage
python3 /Users/bitsentry/Projects/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> /tmp/
mv /tmp/<skill-name>.zip <path/to/skill-folder>/<skill-name>.skill

# 4. Update README.md if needed (installation instructions, features, etc.)
```

**Example changes requiring rebuild:**
- Modified SKILL.md content or frontmatter
- Added/modified scripts in `scripts/`
- Updated reference docs in `references/`
- Changed assets in `assets/`
- Updated LICENSE.txt

#### Case B: Only README.md Changed

**Do NOT rebuild the `.skill` file:**

```bash
# Just edit README.md and commit
# The .skill file remains unchanged
```

**Example changes NOT requiring rebuild:**
- Fixed typos in README.md
- Updated installation instructions
- Added usage examples
- Clarified feature descriptions

### Workflow 3: Adding Licenses

All skills must have licenses:

#### For Open-Source Skills:

```bash
# 1. Copy Apache 2.0 LICENSE.txt
cp /Users/bitsentry/Projects/bitsentry-skills/algorithmic-art/LICENSE.txt <skill-path>/LICENSE.txt

# 2. Update copyright year to 2025 and copyright holder to "BitSentry Contributors"

# 3. Add license field to SKILL.md frontmatter
license: Apache 2.0 (see LICENSE.txt)

# 4. Rebuild .skill file
```

#### For BitSentry-Specific Skills:

```bash
# 1. Copy proprietary LICENSE.txt from an existing BitSentry skill
cp /Users/bitsentry/Projects/bitsentry-skills/bitsentry-backend-spec-writer/LICENSE.txt <skill-path>/LICENSE.txt

# 2. Add license field to SKILL.md frontmatter
license: Proprietary - Internal BitSentry Use Only (see LICENSE.txt)

# 3. Rebuild .skill file
```

### Workflow 4: Cleaning Up Bad Examples

When reviewing design spec examples:

1. **Check for required sections:**
   - Review Table ✅
   - Approval Table ✅

2. **Evaluate code vs diagrams ratio:**
   - Too much code? Remove it
   - Replace with Mermaid diagrams

3. **Remove if:**
   - Missing required tables
   - Excessive implementation code
   - Unresolved "Open for discussion" items marked as [SELECTED]

4. **After removing examples:**
   ```bash
   # Rebuild the skill
   rm <skill-path>/<skill-name>.skill
   python3 /Users/bitsentry/Projects/skills/skill-creator/scripts/package_skill.py <skill-path> /tmp/
   mv /tmp/<skill-name>.zip <skill-path>/<skill-name>.skill
   ```

### Workflow 5: Updating README.md in Repository Root

When adding new skills or restructuring:

1. **Update the appropriate section:**
   - BitSentry Skills → Add to "BitSentry Skills" section
   - Anthropic examples → Don't modify

2. **Include:**
   - Skill name and brief description
   - Installation command (curl from GitHub)
   - Key features

3. **Format consistently:**
   ```markdown
   ### Skill Name

   Brief description here.

   **Installation:**
   ```bash
   curl -L https://raw.githubusercontent.com/bitsentry-ai/bitsentry-skills/main/path/to/skill.skill -o skill.skill
   ```

   **Features:**
   - Feature 1
   - Feature 2
   ```

## Packaging Best Practices

### Always Package to /tmp First

**NEVER package directly to the skill directory to avoid recursive packaging:**

```bash
# ❌ WRONG - Creates recursive packaging
python3 package_skill.py /path/to/skill /path/to/skill

# ✅ CORRECT - Package to temp, then move
python3 package_skill.py /path/to/skill /tmp/
mv /tmp/skill-name.zip /path/to/skill/skill-name.skill
```

### Verify No Recursive Packaging

After packaging, always verify:

```bash
cd /tmp && mkdir verify && cd verify
unzip -q /path/to/skill.skill
find skill-name -name "*.skill" -o -name "*.zip" | wc -l
# Should output: 0
```

### Check Package Contents

Before finalizing:

```bash
unzip -l /path/to/skill.skill
# Verify:
# - SKILL.md present
# - LICENSE.txt present
# - No .skill or .zip files inside
# - All scripts/, references/, assets/ included as expected
```

## Quality Checklist

Before considering any skill complete:

- [ ] SKILL.md has proper frontmatter (name, description, license)
- [ ] LICENSE.txt exists and is appropriate (Apache 2.0 or Proprietary)
- [ ] README.md has installation instructions
- [ ] No recursive .skill or .zip files in package
- [ ] All filenames use only ASCII-safe characters (no `[ ] # ( ) & + × — ‑`)
- [ ] No .DS_Store files in package
- [ ] Design specs follow diagram-first approach (if applicable)
- [ ] All design spec examples have Review and Approval tables
- [ ] `.skill` file is clean and properly packaged
- [ ] Main repository README.md is updated (if new skill)

## Troubleshooting

### Problem: Package contains nested .skill files

**Solution:** The package script picked up an existing .skill file. Remove it first:

```bash
rm /path/to/skill/<skill-name>.skill
# Then repackage
python3 package_skill.py /path/to/skill /tmp/
mv /tmp/<skill-name>.zip /path/to/skill/<skill-name>.skill
```

### Problem: Skill validation fails

**Solution:** Run the validation script directly to see detailed errors:

```bash
python3 /Users/bitsentry/Projects/skills/skill-creator/scripts/quick_validate.py /path/to/skill
```

Common issues:
- Missing required fields in frontmatter (name, description)
- Invalid YAML syntax in frontmatter
- Missing SKILL.md file

### Problem: "Zip file contains path with invalid characters"

**Critical Issue:** This error occurs when filenames contain special characters that some systems reject during upload.

**Problematic Characters:**
- ❌ Brackets: `[ ]`
- ❌ Hash/Pound: `#`
- ❌ Parentheses: `( )`
- ❌ Ampersand: `&`
- ❌ Plus: `+` (in some contexts)
- ❌ Unicode symbols: `×` (multiplication), `—` (em dash), `‑` (non-breaking hyphen)
- ❌ macOS metadata: `.DS_Store` files

**Solution:** Clean all filenames to use only ASCII-safe characters:

```bash
# 1. Remove all .DS_Store files
find /path/to/skill -name ".DS_Store" -delete

# 2. Rename files with special characters
# Replace brackets, hash, parentheses with hyphens or words
# Examples:
# [DRAFT] Requirements.md → DRAFT - Requirements.md
# Architecture [Version #2].md → Architecture - Version 2.md
# API × Database (Integration) — Technical + Implementation.md → API x Database Integration - Technical and Implementation.md

# 3. Rebuild the skill
rm /path/to/skill/<skill-name>.skill
python3 /Users/bitsentry/Projects/skills/skill-creator/scripts/package_skill.py /path/to/skill /tmp/
mv /tmp/<skill-name>.zip /path/to/skill/<skill-name>.skill
```

**Allowed Characters:**
- ✅ Letters: `a-z`, `A-Z`
- ✅ Numbers: `0-9`
- ✅ Spaces
- ✅ Hyphens: `-`
- ✅ Underscores: `_`
- ✅ Periods: `.`

**Before/After Examples:**
```
❌ [FINAL] Database Schema & Migration Plan.md
✅ FINAL - Database Schema and Migration Plan.md

❌ Security Requirements [Phase #1] [APPROVED].md
✅ Security Requirements - Phase 1 - APPROVED.md

❌ Service × Gateway (Config) — REST‑API + GraphQL.md
✅ Service x Gateway Config - REST-API and GraphQL.md
```

**Verification:**
```bash
# Check package for special characters
unzip -l /path/to/skill.skill | grep -E "\[|\]|×|—|‑|#|&|\+"

# Should return no results (exit code 1)
```

### Problem: Not sure if rebuild is needed

**Decision tree:**

```
Did you change SKILL.md?
├─ Yes → Rebuild .skill file
└─ No → Did you change scripts/, references/, or assets/?
    ├─ Yes → Rebuild .skill file
    └─ No → Did you change LICENSE.txt?
        ├─ Yes → Rebuild .skill file
        └─ No → Did you ONLY change README.md?
            ├─ Yes → NO rebuild needed
            └─ No → If unsure, rebuild to be safe
```

## File Structure Reference

### Typical Skill Structure

```
skill-name/
├── SKILL.md              # The skill itself (triggers rebuild)
├── LICENSE.txt           # License (triggers rebuild)
├── README.md             # Human docs (no rebuild needed)
├── skill-name.skill      # Packaged skill (distribute this)
├── scripts/              # Optional executable code (triggers rebuild)
│   └── example.py
├── references/           # Optional docs loaded as needed (triggers rebuild)
│   └── patterns.md
└── assets/               # Optional templates/files (triggers rebuild)
    └── template.md
```

### Skill Frontmatter Template

```yaml
---
name: skill-name
description: Complete description of what this skill does and when to use it. Use third-person (This skill should be used when...).
license: Apache 2.0 (see LICENSE.txt)  # or: Proprietary - Internal BitSentry Use Only (see LICENSE.txt)
---
```

## Git Remote for Installation Instructions

The repository is hosted at:
```
https://github.com/bitsentry-ai/bitsentry-skills
```

Installation command template:
```bash
curl -L https://raw.githubusercontent.com/bitsentry-ai/bitsentry-skills/main/<path>/<skill-name>.skill -o <skill-name>.skill
```

## Key Tools Reference

Located in `/Users/bitsentry/Projects/skills/skill-creator/scripts/`:

1. **init_skill.py** - Create new skill from template
2. **package_skill.py** - Validate and package skill into .skill file
3. **quick_validate.py** - Validate skill without packaging

Always use these tools rather than manually creating zip files.

---

## Final Notes

- **Stay consistent**: Follow the patterns established in existing skills
- **Document decisions**: If you make a significant change, explain why in commit messages
- **Verify packages**: Always check the final .skill file contents
- **Test locally**: Unzip and verify before considering work complete
- **Update README.md**: Keep main documentation in sync with actual skills

This repository is a living system. When in doubt, look at existing well-structured skills like `bitsentry-backend-spec-writer` as references.
