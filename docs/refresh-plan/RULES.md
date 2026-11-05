# Rules for Every Session

Short and strict. If a rule gets in the way, ask Tim. Don't bend the rule.

## 1. Start of a session

1. `git pull` on `update-sqlcodegen`. The working tree must be clean.
2. Read, in this order:
   1. [README.md](README.md): goal, bugs, decisions
   2. this file
   3. the **previous** session's `HANDOVER.md`, especially "Start here"
   4. your own session's `PLAN.md`
3. Run the tests (from S01 on) before you change anything. If they're red, fix that first or report it.

## 2. During the session

| Rule | Why |
| ---- | --- |
| Stay in the session's scope. Out-of-scope findings go into the handover under "For later". | Sessions stay reviewable |
| The decisions in `README.md` are fixed. Changing one means asking Tim first. | Tim owns the direction |
| Breaking changes only when a bug can't be fixed without them. Each one gets a changelog note. | "The result stays the same" |
| From S03 on, never edit generated model files by hand. Change the generator. | Output must be reproducible |
| The baseline diff is empty, or every difference is in the allowed-differences list with a reason | Proves "same result" |
| Never skip or delete a failing test to get green. Known bugs: `xfail(strict=True)` with the bug ID. | Honest test status |
| Don't upgrade pinned dependencies unless the plan says so | Reproducible output |
| Temp files, downloads and test DBs stay out of the repo | Clean history |
| Docs: short pages, tables and code first, no walls of text | Easy to read |

## 3. End of a session

1. Run the full test suite. Write down the result in the handover. Don't claim green if it isn't.
2. Write `<session-folder>/HANDOVER.md` using the [template](HANDOVER_TEMPLATE.md).
3. Update the status column in the session table in [README.md](README.md).
4. Tick the finished boxes in your `PLAN.md`. Move unfinished ones into the handover.
5. Commit and push (see below).

## 4. Git

- **Branch:** work on `update-sqlcodegen`. Never push to `main`, never force-push. Open no PR unless Tim asks.
- **Author:** use the git user that's already configured. Don't touch the git config.
- **Commit messages** look like the rest of the history:
  - short, lowercase, plain English: `add baseline snapshots and smoke tests`, `fix metadata name clash in tables flavor`, `update readme`
  - no prefixes (`feat:`, `chore:`), no body unless really needed
  - no mention of sessions, plans, AI or tools
  - **no** `Co-Authored-By`, "Generated with …" or any other attribution footer
- **Size:** a few logical commits per session (for example: tests, code, docs). Not one huge commit, not dozens of tiny ones.
- **Never commit:** `.env`, passwords, downloaded OMOP archives, Athena exports, `*.db` / `*.sqlite`.
- **Push** at the end of the session: `git push origin update-sqlcodegen`.
