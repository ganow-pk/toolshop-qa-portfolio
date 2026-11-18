# How AI was used in this project

I build test automation with an AI coding assistant (Claude Code) the same way I would work with a fast junior developer: it drafts, I decide.

## Operating rules
- **The assistant drafts, I approve.** Nothing is committed, pushed, or posted anywhere without my explicit go-ahead.
- **No secrets in chat.** Credentials come from environment variables (`config/settings.py`), never from a prompt.
- **Verify against the live system, not the assistant's notes.** Locators and expected results are confirmed by running the test against the real app.
- **Name the missed rule, then make it mechanical.** When the assistant skips a step, I don't just correct it once. I turn the rule into code. Example: every test must declare its ISTQB technique, and `conftest.py` refuses to run a test that doesn't.
- **Same healing rules for AI and humans.** An AI-suggested fix that loosens an assertion is rejected, the same as anyone else's ([HEALING_RULES.md](HEALING_RULES.md)).

## What this looked like here
- The framework structure, page objects, and first tests were drafted with the assistant from my design: POM, data-test locators, config-driven settings, technique tags.
- The first run against the live site checked every assumption the draft made. Anything that had to change went into the [heal log](heal_log.md).
