/**
 * Profundidad con el ratón para capas decorativas.
 * Cualquier elemento con [data-depth] dentro de un [data-depth-root] se desplaza
 * según su valor (px por unidad de puntero). Solo con puntero fino y sin reduced-motion.
 */
function initDepth() {
  const els = Array.from(document.querySelectorAll<HTMLElement>('[data-depth-root] [data-depth]'));
  if (!els.length) return;
  if (!matchMedia('(hover: hover) and (pointer: fine)').matches || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const layers = els.map((el) => ({ el, d: parseFloat(el.dataset.depth || '0') }));
  let tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
  const loop = () => {
    cx += (tx - cx) * 0.06; cy += (ty - cy) * 0.06;
    for (const l of layers) l.el.style.transform = `translate3d(${(cx * l.d).toFixed(2)}px, ${(cy * l.d).toFixed(2)}px, 0)`;
    raf = Math.abs(tx - cx) + Math.abs(ty - cy) > 0.0015 ? requestAnimationFrame(loop) : 0;
  };
  const onMove = (e: PointerEvent) => {
    tx = (e.clientX / innerWidth) * 2 - 1; ty = (e.clientY / innerHeight) * 2 - 1;
    if (!raf) raf = requestAnimationFrame(loop);
  };
  window.addEventListener('pointermove', onMove, { passive: true });
  document.addEventListener('astro:before-swap', () => { window.removeEventListener('pointermove', onMove); cancelAnimationFrame(raf); }, { once: true });
}
document.addEventListener('astro:page-load', initDepth);
