# Session 01: Bug hunt on browse, search, and filter

## Charter
**Explore** the product catalog (home page, search, sort, price range, category and brand filters, pagination)
**with** the Toolshop *with-bugs* build and a mix of typical and unusual inputs
**to discover** defects in what is shown, how it is labelled, and whether results match what was asked for.

| | |
|---|---|
| **Tester** | PK Ganow |
| **Environment** | https://with-bugs.practicesoftwaretesting.com (Toolshop v5.0 with bugs) |
| **Browser / OS** | |
| **Date / start time** | |
| **Time box** | 60 minutes |

## Heuristics and oracles I'll use
- **Consistency with the main build:** the same action on https://practicesoftwaretesting.com is the reference ("this is what it should do").
- **Consistency within the page:** counts, labels, and results agree with each other (e.g. "X products found" matches what's listed).
- **Boundaries:** price range edges, first and last page, empty search, very long search text.
- **Claims:** visible text (labels, buttons, headings) says what it does and is spelled correctly.
- **CRUD-adjacent state:** filters, sort, and search combined, then cleared. Does the page return to its starting state?

## Session notes
*Write as you go: what you tried, what happened, what you noticed. Short lines are fine.*

- 

## Bugs found
*One line each. File the full report as a GitHub issue with the bug template, then link it here.*

| # | Title | Severity | Issue |
|---|-------|----------|-------|
| 1 | Login form gives no feedback when the email is invalid and password is blank (found while confirming an automated failure, before this session) | Major | [#1](https://github.com/ganow-pk/toolshop-qa-portfolio/issues/1) |
| 2 | | | |

## Issues and questions
*Things that aren't clearly bugs: unclear requirements, things to ask a developer, test obstacles.*

- 

## Coverage
*What did you actually get to? What did you not get to?*

- Covered:
- Not covered:

## Time split
| Activity | % of session |
|----------|--------------|
| Test design and execution | |
| Bug investigation and reporting | |
| Session setup | |

## Follow-up charters
*Ideas this session gave you for the next one.*

- 
