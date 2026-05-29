# AGENTS.md

Notes for AI coding agents. This is a docs-and-examples repo (a pain-first cloud native
guide for AI/ML developers), not an application. Human contribution rules are in
CONTRIBUTING.md; explicit user instructions override this file.

## Project layout
- Pains live in `pains/<category>/<ID>-<slug>.md`; each pain's demo in `examples/<category>/<ID>-<slug>/` with `before/` and `after/`.
- Categories are word-named folders: `foundation compute serving operations governance compliance hpc agents`.
- IDs use cluster-letter prefixes: file `F01-slug.md`, displayed `F.01`. Numbering is stable per cluster (next Compute pain is `C06`); never global-renumber.
- Run `git fetch` before counting pains; they are sometimes added directly on `main`.

## Writing a pain
- Copy the shape of `pains/governance/G01-prompt-version.md`: `# Pain X.NN: <problem>`, a blockquote scenario, `## The pattern` (short intro, then two mermaid diagrams captioned `**Without cloud native (...)**` and `**With cloud native (...)**`), `## The primitives`, `## Trade-offs` (`**What you keep**` / `**What you give up**`), `## Try it` (only if a built example exists), footer nav.
- About 150 words per section, concrete over abstract. Keep AI-layer concerns (eval, prompt/retrieval quality) out; route them to `reference/where-cn-doesnt-help.md`.

## Writing an example
- README opens with `**Demonstrates:** Tech A · Tech B · Tech C` (middots). Must run on a local Kind cluster with no GPU; simulate inference if needed.
- Share one Kind cluster across `before/` and `after/`; put Prerequisites and cluster creation in `before/`.
- Mark an example "built" only after verifying it live, then flip three surfaces together: add `## Try it` to the pain, set its `examples/README.md` row to a linked `Available`, and in the README landscape prefix the node with `✓ ` and add its ID to the `class ... avail;` line.
- Recurring gotchas: `kubectl port-forward` binds to one pod and does not follow rollouts (restart it after each `rollout restart`, and say so in the README); name demo env vars defensively (`SYSTEM_PROMPT`, not `PROMPT`, which zsh claims); commit `.env.example`, not the gitignored `.env`; keep tool-specific quirks in that example's README, not here.

## Checks before you commit
- Validate any changed mermaid in both themes: `mmdc -i d.mmd -o out.svg` and the same with `-t dark` (GitHub renders dark; dark fills need an explicit `color:`). README landscape `click` URLs are absolute blob paths and include the category.
- Resolve every relative link you add or move; there is no link-checker. Depth bites: `examples/<cat>/<ID>/after/README.md` is four deep, so pain links are `../../../../pains/...`.
- For examples, run the walkthrough end to end on Kind and paste real command output, not idealized text.
- Style: no em-dashes (comma, period, or parentheses); pain-first; discuss design in prose rather than multiple-choice prompts; match sibling-file voice.

## PR instructions
- Commit or push only when asked. Branch off `main`; never commit to `main` directly or run `gh pr merge`.
- Keep PRs small: one pain or one example.
- End each commit with a `Co-Authored-By:` trailer for your own agent and each PR body with a one-line tool attribution. Claude Code uses `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` and `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
- To squash: soft-reset to `main`, recommit, confirm the tree hash is unchanged, then `git push --force-with-lease`.
