# Showing it: figures and explorables

The user learns best from visual explanations. So when an idea has a shape, a motion or a
dependence on a parameter, show it, in any loop: teaching a concept, cueing a lecture gap,
giving a check on a problem.

Every visual here is **computed, never generated**. A picture produced by an image model looks
plausible and is often wrong, which is the worst property a teaching figure can have. A plot
produced by code that implements the mathematics is right for the same reason the mathematics
is right, and you can check it.

## Pick the form

| The idea is about | Show | Example |
|---|---|---|
| A shape, a configuration, where things sit | **Computed figure** (matplotlib → PNG) | A subspace as a plane through the origin; an arm pose with the Jacobian columns as arrows; a free-body diagram |
| How something changes with a parameter, or over time | **Explorable** (one HTML page with sliders) | Drag the damping and watch the poles cross the axis; move a joint and watch the velocity ellipse collapse |
| Two cases that get confused | **Side-by-side panels** of the same kind of figure | Stable vs marginally stable response; body frame vs space frame |
| Pure algebra, a definition, a proof step | Nothing | Do not force a picture onto an idea that has no shape |

One visual per idea. If you want three figures, you are explaining three things.

Schematic drawings (free-body diagrams, frames, linkages) are also computed: place the bodies
and arrows from coordinates with matplotlib patches and annotations, so lengths and angles mean
something.

## Where they go

Outside the vault, next to the course material: `<materials>/visuals/`, where `<materials>` is
the folder in the course hub's `materials` field. If the course has no materials folder yet,
ask where to keep them. Name files by the idea, prefixed with the lecture or sheet when there is
one: `L02-hidden-mode.html`, `sheet2-p3-arm-pose.png`, `singularity-2R-arm.html`.

Before building one, list that folder; a visual made last week for the same idea can be
reopened instead of rebuilt.

Nothing you draw goes into the vault. If they want a picture in a concept note, that is theirs
to make.

## A computed figure

1. Write a short script that computes the thing from the actual mathematics and plots it.
2. Make it readable at a glance:
   - axis labels with units, and a title that states the point, not the topic ("Tip moves
     sideways when only the elbow turns", not "Arm");
   - label lines and points directly where you can, instead of a legend to decode;
   - equal aspect ratio for anything geometric;
   - at most three colours, used in this order: `#2a78d6` blue, `#eb6834` orange, `#1baf7a`
     green. Grey (`#898781`) for reference lines and anything that is context;
   - `figsize=(7, 4.5)`, `dpi=160`, white background, `bbox_inches="tight"`.
3. **Look at it** before they do: read the PNG back. Overlapping labels, a clipped title, the
   wrong axis range and an arrow pointing the wrong way are all common, and all invisible until
   you look. Fix and re-render.
4. Open it for them (`open <file>` on macOS) and give the path in the reply.

## An explorable

Use one when the understanding comes from moving something. It takes longer to build, so it
has to earn it: there must be a parameter worth dragging.

1. Copy `assets/explorable.html` to the visuals folder. It is a complete working example (the
   poles and step response of a mass-spring-damper). Replace four things: the text at the top,
   `PARAMS` (one entry per slider), `model()` (the mathematics) and `draw()` (the traces). Leave
   the plumbing below them alone; it already provides what geometric pictures need:
   - `layout(c, axes, { equal: true })` for equal scale on both axes;
   - `arrow([x0, y0], [x1, y1], color)` passed as `{ arrows: [...] }` for vectors;
   - colours `c.s1`, `c.s2`, `c.s3` (blue, orange, green, in that order) and `c.muted` for
     reference lines, in both light and dark mode.

   It loads Plotly from a CDN, so it needs a connection once.
2. Keep it small: one to three sliders, one or two plots, a one-line readout that states in
   words what the current setting means ("poles at −0.50 ± 0.87i → asymptotically stable").
   Fix the axis ranges so that moving a slider moves the curve, not the axes. Say which colour
   is which in the text above the plots, and write symbols in plain characters ("q1 rate", not
   a dot over a letter, which renders badly).
3. **Predict first.** The page opens with a prediction question, and you ask the same question
   in the reply. It has to be about a setting your explanation has left open: if the reply
   explains the stretched arm, ask about the folded one. Seeing an answer they committed to
   turn out right or wrong is what makes the picture stick; watching an animation without a
   stake in it is entertainment.
4. Check the mathematics: compute one or two slider settings independently in numpy or sympy
   and compare with what the page shows.
5. **Look at it**: render it headlessly and read the screenshot back, at the default setting
   and at the interesting one. Slider values can be set in the URL.

   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
     --window-size=1200,800 --virtual-time-budget=6000 \
     --screenshot=<scratch>/check.png "file://<page>?q2=0"
   ```

   A blank plot means a script error; fix it before sending them a broken page.
6. Open it for them and give the path.

## In the reply

The visual supports the explanation; it does not replace it. Say in a sentence what to look at
and what it shows ("watch the orange arrow: it stays perpendicular to link 2"), then continue
in words. Afterwards the check still has to make them produce something, and with an explorable
the natural one is a prediction about a setting they have not tried yet.

If a kind of picture clearly worked for them, note it in `meta/Tutor notes.md`.
