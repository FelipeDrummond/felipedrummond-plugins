import sys
from reportlab.lib.pagesizes import landscape, A5
from reportlab.pdfgen import canvas

SLIDES = [
    ("Control Systems — Lecture 2", ["Stability of linear time-invariant systems", "", "Winter semester 2026/27"]),
    ("State-space model", ["x'(t) = A x(t) + B u(t),   y(t) = C x(t) + D u(t)", "x in R^n: state, u: input, y: output", "Free response (u = 0):  x(t) = exp(A t) x(0)"]),
    ("Equilibrium", ["x_e is an equilibrium if A x_e = 0 (with u = 0)", "If A is invertible, the origin is the only equilibrium"]),
    ("Stability definitions", ["Lyapunov stable: for every eps > 0 there is delta > 0 such that", "   |x(0)| < delta  implies  |x(t)| < eps for all t >= 0", "Asymptotically stable: Lyapunov stable AND x(t) -> 0 as t -> infinity", "Stable does not imply asymptotically stable (undamped oscillator)"]),
    ("Eigenvalue criterion", ["Asymptotically stable  <=>  Re(lambda_i) < 0 for ALL eigenvalues of A", "Eigenvalues may be complex: only the real part matters", "Unstable if any eigenvalue has Re(lambda_i) > 0"]),
    ("Marginal stability", ["Eigenvalues with Re = 0 and none with Re > 0:", "  Lyapunov stable only if every such eigenvalue has", "  equal algebraic and geometric multiplicity (no Jordan block > 1)", "Example: double integrator, lambda = 0, 0 -> unstable (x grows like t)"]),
    ("BIBO vs internal stability", ["BIBO stable: bounded input gives bounded output", "  <=> all POLES of G(s) = C (sI - A)^-1 B + D have Re < 0", "Internal (asymptotic) stability implies BIBO stability", "Converse fails: an unstable mode can be hidden by pole-zero cancellation"]),
    ("Routh-Hurwitz criterion", ["Test Re(roots) < 0 without computing the roots", "p(s) = a_n s^n + ... + a_1 s + a_0", "Necessary: all coefficients present and of the same sign", "Necessary and sufficient: no sign change in the first column of the Routh array", "Second order: a_2, a_1, a_0 > 0 is already sufficient"]),
    ("Example: mass-spring-damper", ["m x'' + d x' + k x = F", "Characteristic polynomial: m s^2 + d s + k", "lambda = (-d +/- sqrt(d^2 - 4 m k)) / (2 m)", "d > 0: asymptotically stable.  d = 0: marginally stable.  d < 0: unstable"]),
]
c = canvas.Canvas(sys.argv[1], pagesize=landscape(A5))
w, h = landscape(A5)
for n, (title, lines) in enumerate(SLIDES, 1):
    c.setFont("Helvetica-Bold", 20); c.drawString(40, h - 60, title)
    c.setFont("Helvetica", 13)
    for i, line in enumerate(lines):
        c.drawString(50, h - 110 - 26 * i, line)
    c.setFont("Helvetica", 9); c.drawRightString(w - 30, 20, f"Slide {n}")
    c.showPage()
c.save()
