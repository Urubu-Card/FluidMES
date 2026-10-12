// Pure geometry: long sections retain natural scrolling until their boundary.
export function sectionTarget(sections, scrollY, viewport, direction, maxScroll) {
    if (!sections.length) return null;
    const probe = scrollY + Math.min(120, viewport / 4);
    let index = 0;
    sections.forEach((section, i) => { if (section.top <= probe) index = i; });
    const current = sections[index];
    if (direction > 0) {
        if (current.bottom > scrollY + viewport + 3) return null;
        if (index === sections.length - 1) return null;
        return Math.min(sections[index + 1].top, maxScroll);
    }
    if (scrollY > current.top + 3) return null;
    if (!index) return null;
    const previous = sections[index - 1];
    return Math.max(previous.top, previous.bottom - viewport, 0);
}
