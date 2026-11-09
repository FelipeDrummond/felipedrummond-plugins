# The notes page

A plain academic working paper, built up during the session beside the chat. Chat holds the dialogue; the page holds the full mathematics. It is not a handout and not a slide deck: no headline claims without derivations, no slogans, no decoration.

## Where it lives and how it is shown

Do these steps at the start of the block, before the first reply, not when the first formula appears. A page that opens only once there is mathematics depends on what the opening message happens to contain, and he is left without one.

1. Sync the assets once per session: `rsync -a S/assets/ HOME/pages/assets/`.
2. Create the page at `HOME/pages/<course>/session-<n>.html` (next unused `n` for that course) by copying `S/assets/template.html` and filling its placeholders (`<!-- TITLE -->`, `<!-- SUBTITLE -->`, `<!-- SECTIONS -->`, `<!-- SEALED -->`, `<!-- EVIDENCE -->`). It links `../assets/notes.css` and `../assets/figures.js`, so it must sit one folder below `pages/`.
3. Show it in the app's browser pane with `preview_start` and the name `tutor-pages` (from `HOME/.claude/launch.json`, serving `HOME/pages` at `http://localhost:8765`), then open `http://localhost:8765/<course>/session-<n>.html`. Starting by name works only when the session's folder is `HOME`. Otherwise run `python3 -m http.server 8765 --directory HOME/pages` in the background and open the URL with `preview_start`.
4. Update the page as the session goes, and reload it after each change.

## Form

- One column, serif math typeface, KaTeX for every formula: `\( ... \)` inline, `\[ ... \]` display. Number equations that are referred to later (`\tag{1}`).
- Formal environments: `<div class="env"><span class="head">Definition 1.</span> <span class="body">...</span></div>`, likewise Theorem, Remark, Example. Theorems state every hypothesis. Notation follows the course's own material.
- Exercises go in `<div class="exercise"><span class="head">Exercise 2.</span> ...</div>`. His attempt is written down inside it, in a `<div class="reply">`, next to your assessment (verdict first, as in chat).
- **Sealed sections:** a list (`.sealed li`) of what opens after what, for example "Proof of Theorem 1 — opens after Exercise 2". A section that gives away an answer stays sealed until he has attempted it. Move it from the list into the page only then.
- Figures: black and white, built per `references/figures.md`.
- **Evidence line** (`.record`) at the end: what the tests show, plainly ("Exercise 1 correct unhinted; Exercise 2 wrong, patched, not mastered; retest owed"). Add the confidence line from `tutorlog.py summary SLUG` for each topic tested. A short summary, never a growing table: the full record stays in the log.
- Your own mistakes are corrected on the page too, visibly ("Correction: ..."), not silently.
- A summary he asked for may go on the page in full, but in chat it always comes with a question on it.
- Nothing from the page is ever copied into the vault.

## Check after every update

After every change to the page, with the pane visible, run in the page (`javascript_tool`):

```js
({katexErrors: document.querySelectorAll('.katex-error, .katex [style*="#cc0000"], [mathcolor="#cc0000"]').length,
  rawDelims: (document.body.innerText.match(/\\[(\[]/g) || []).length,
  sideways: innerWidth > 0 && document.documentElement.scrollWidth > innerWidth})
```

All three must be `0`, `0`, `false`. If any isn't, fix the page before you send the next message.

- `katexErrors` counts KaTeX error elements and formulas KaTeX rendered in red because of an unknown command.
- `rawDelims` counts `\(` or `\[` left as raw text, which means a formula never rendered (often an unbalanced brace).
- `sideways` means the page scrolls sideways; a wide display formula or figure needs breaking or shrinking.
- `innerWidth` of 0 means the pane is hidden and the check proves nothing: show the pane and run it again.

## Reference standards

Aim at these, don't copy from them:
- Khalil, *Nonlinear Systems*, for rigor (from memory).
- Tedrake, *Underactuated Robotics*, for robot examples (checked: its Lyapunov chapter covers LaSalle and neural Lyapunov functions, but states theorems without proof).
- Arnold, *Ordinary Differential Equations*, for geometric intuition (from memory).

When you mention any of them to him, say "from memory" unless you have just read the passage.
