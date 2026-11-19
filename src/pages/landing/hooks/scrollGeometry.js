// Align to the closest section, regardless of the last gesture's direction.
export function nearestSectionTarget(sections, scrollY, viewport, maxScroll) {
    if (!sections.length || viewport <= 0) return null;
    const max = Math.max(0, maxScroll);
    const edgeZone = Math.min(140, viewport * .2);
    const candidates = [];
    for (const { top, bottom } of sections) {
        const lastViewport = bottom - viewport;
        if (bottom - top > viewport + 3) {
            // Keep the middle of long sections readable, especially on phones.
            if (scrollY > top + edgeZone && scrollY < lastViewport - edgeZone) return null;
            candidates.push(lastViewport);
        }
        candidates.push(top);
    }
    return candidates.reduce((nearest, edge) => {
        const target = Math.max(0, Math.min(edge, max));
        return nearest === null || Math.abs(target - scrollY) < Math.abs(nearest - scrollY) ? target : nearest;
    }, null);
}
