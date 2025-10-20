# Updated Groom Room Implementation

## Overview

The Groom Room implementation has been updated with a new system prompt that focuses on QA refinement with a specific output schema. This update provides more concise, story-specific, and refinement-ready analysis.

## Key Changes

### New System Prompt

The updated system prompt transforms Groom Room into a **QA Refinement Assistant** with the following characteristics:

- **Role**: QA refinement assistant for Jira user stories, bugs, and spikes
- **Output**: Concise, story-specific, and refinement-ready
- **Style**: No boilerplate, no Gherkin, no "generic" AC
- **Language**: UK spelling
- **Focus**: Always tie back to the ticket's description/AC

### Global Rules

1. If AC exist → rephrase into testable AC (don't say "AC missing" unless truly empty)
2. If AC are vague → rewrite to be measurable and add examples of high-level test scenarios
3. If info is unknown → use [TBD] and raise a **specific question**
4. Only include ADA if UI is in scope
5. Always include **Definition of Ready gate** before scoring
6. No "Given/When/Then", no grooming checklist, no dependencies/blockers sections unless critical
7. Response should feel like a QA refinement note — short, clear, directly usable in a call

### Output Schema

The new output follows a specific schema:

```
# Ticket Summary
1–2 lines tailored to this story.

# Acceptance Criteria (Refined & Testable)
* Functional behaviour rules (what should happen in the UI/system)
* Data rules (required fields, defaults, invalid handling)
* Error/empty state handling
* Observability (logs/metrics/alerts, env scope)
* Performance/non-functional expectations (if relevant)
* Rollout/flags/environments (if applicable)

# Questions to Clarify (Targeted)
List of missing/unclear items from the ticket.

# High-Level Test Scenarios (Mapped to AC)
* Happy path
* Negative/error path
* Edge cases (boundary data, multiple invalids, toggling flags)
* Cross-device/browser (if UI)
* Recovery/rollback
* ADA (if applicable)

# Observability & Evidence Plan
* Where QA will validate (logs, console, metrics, alerts)
* What evidence is expected (screenshots, logs, metrics)

# Definition of Ready Gate (Pass/Fail)
Checklist:
* Behaviour clearly defined
* Edge/error handling specified
* Data rules outlined
* Observability included
* Performance/ADA (if relevant)
* Test data/envs available

Return: DoR Status: Pass|Fail with missing items listed.

# Pointing Guidance (If DoR=Pass)
Only if DoR=Pass → note complexity drivers, unknowns, and suggested pointing band.
If DoR=Fail → output: "Do not point until DoR gaps are resolved."
```

## Implementation Details

### New Methods Added

1. **`get_updated_groom_room_system_prompt()`**: Returns the new system prompt
2. **`generate_updated_groom_analysis()`**: Generates analysis using the new format
3. **Updated `generate_groom_analysis()`**: Now uses the new format for "updated" and "default" levels

### CLI Updates

The CLI now includes:
- `--level` option with choices: `updated`, `strict`, `light`, `default`, `insight`, `deep_dive`, `actionable`, `summary`
- Default level is now `updated`
- Uses the new analysis format for `updated` and `default` levels

### Usage Examples

#### Command Line
```bash
# Use the new updated format (default)
python groomroom/cli.py --file ticket.txt

# Explicitly use updated format
python groomroom/cli.py --file ticket.txt --level updated

# Use other levels (legacy format)
python groomroom/cli.py --file ticket.txt --level strict
```

#### Programmatic Usage
```python
from groomroom.core import GroomRoom

groomroom = GroomRoom()

# Use updated format
analysis = groomroom.generate_groom_analysis(ticket_content, level="updated")

# Or use the dedicated method
analysis = groomroom.generate_updated_groom_analysis(ticket_content)
```

## Testing

A test script has been created to verify the implementation:

```bash
python test_updated_groomroom.py
```

The test script:
- Verifies the updated system prompt is generated correctly
- Tests the new analysis format
- Checks for expected output sections
- Validates level-based analysis works

## Migration Guide

### For Existing Users

1. **Default Behavior**: The default level now uses the updated format, so existing scripts will automatically get the new output format
2. **Legacy Format**: Use `--level strict`, `--level light`, etc. to get the original format
3. **Explicit New Format**: Use `--level updated` to explicitly request the new format

### For New Users

1. Start with the default `updated` level for the new QA refinement format
2. Use other levels only if you need the legacy comprehensive analysis format

## Benefits of the New Format

1. **More Concise**: Focuses on essential information for QA refinement
2. **Story-Specific**: Tailored to each individual ticket rather than generic templates
3. **Refinement-Ready**: Output is directly usable in grooming calls
4. **Clear Structure**: Follows a consistent schema that teams can rely on
5. **Actionable**: Provides specific questions and guidance rather than generic suggestions

## Brand and Payment Rules

The updated implementation maintains all existing brand abbreviation and payment flow rules:

- **Brand Abbreviations**: MMT, ExO, YCC, ELF, EMEA are valid
- **PWA (ELF) Flows**: Only apply to YCC (PLP, PDP, Homepage) or MMT (Homepage, PDP, PLP, Minicart)
- **EMEA Payment**: Use ClearPay instead of AfterPay/Klarna for EMEA brands
- **Title Shortening**: Brand abbreviations in titles are not flagged as missing context

## Enhanced Field Analysis

The new implementation includes enhanced field analysis capabilities:

- Natural language understanding for vague vs specific acceptance criteria
- AC structure validation for intent, conditions, expected results, and pass/fail logic
- Figma link detection and behavioral expectation evaluation
- Test scenario coverage validation
- Missing field detection with meaningful explanations
- PO/design sign-off likelihood inference
- Blocker interpretation from labels and comments
