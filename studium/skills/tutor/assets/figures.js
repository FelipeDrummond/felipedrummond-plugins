(function (root) {
  function rk4(f, s, h) {
    const k1 = f(s), k2 = f(s.map((v, i) => v + h / 2 * k1[i])),
          k3 = f(s.map((v, i) => v + h / 2 * k2[i])), k4 = f(s.map((v, i) => v + h * k3[i]));
    return s.map((v, i) => v + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
  }

  function trajectory(f, s0, T, h = 0.01) {
    const n = Math.round(T / h), pts = [s0];
    let s = s0;
    for (let i = 0; i < n; i++) { s = rk4(f, s, h); pts.push(s); }
    return pts;
  }

  function pathD(points, X, Y) {
    return points.map((p, i) => (i ? 'L' : 'M') + X(p[0]).toFixed(1) + ' ' + Y(p[1]).toFixed(1)).join('');
  }

  function arrowHead(x, y, angleDeg) {
    return `<path d="M6 0 L-6 -4.5 L-3.5 0 L-6 4.5 Z" fill="#111" transform="translate(${x},${y}) rotate(${angleDeg})"/>`;
  }

  root.TutorFig = { rk4, trajectory, pathD, arrowHead };
})(globalThis);
