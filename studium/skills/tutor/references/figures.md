# Figures

Well-made, thoughtful, provocative figures are a must, not a nice-to-have. Use existing tools and don't build a graphics library: KaTeX plus hand-written SVG computed from the equations covers almost everything. Matplotlib (in `HOME/.venv`) is fine when a figure calls for it.

## Tools

`S/assets/figures.js` defines `TutorFig`, loaded by every page:

| Helper | Does |
|---|---|
| `rk4(f, s, h)` | One Runge-Kutta step of `s' = f(s)` |
| `trajectory(f, s0, T, h = 0.01)` | Points from `s0` over time `T` |
| `pathD(points, X, Y)` | An SVG path `d` string, with `X`, `Y` mapping state to pixels |
| `arrowHead(x, y, angleDeg)` | An SVG arrowhead at a point |

Put the figure in `<figure><div id="figN"></div><figcaption>...</figcaption></figure>` and fill `figN` with an SVG string in the page's script. Level curves, phase-plane panels and axis helpers are written per figure; turn code into a shared helper in `figures.js` only when a second figure needs the same code.

## Standards

- **Every plotted curve is computed from the actual equations**, never sketched, with the parameters and initial conditions stated in the caption.
- **Labels sit directly on the figure**, next to what they name, not in a legend.
- **The caption says what the figure shows and what it doesn't prove.** For example: "one initial condition only, so neither is a proof".
- Black and white, consistent with the page. No decoration.
- **Provocative means a figure that challenges what he expects**, not one that is visually loud. Examples of the kind: a pendulum and its linearization nearly coinciding near the origin and separating far from it; a system whose energy-like function rises for a while and which still converges.
- **A figure that gives away an answer waits until after his attempt.** List it as sealed on the page until then.

## Interactive figures

Only when he predicts first. Ask for his prediction (one question, in chat), record it, and only then open an interactive figure. Build it from `S/assets/explorable.html` (sliders and plots; replace its text, parameters, `model()` and `draw()`), saved next to the session page in `HOME/pages/<course>/`, and link it from the page.

## Correctness check

Before a figure goes on the page, check the numbers it rests on with code (`HOME/.venv/bin/python`, NumPy or SymPy), for example the equilibria, eigenvalues or a few trajectory points. Then run the page check in `references/notes-page.md`.
