import { useEffect, useState } from 'react';
import { sectionTarget } from './scrollGeometry.js';

export default function useSectionScroll(rootRef) {
    const [activeSection, setActiveSection] = useState('inicio');
    useEffect(() => {
        const root = rootRef.current;
        if (!root) return;
        const sections = [...root.querySelectorAll(':scope > section[id]')];
        const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
        const coarse = window.matchMedia('(pointer: coarse)');
        let animation = 0, releaseTimer = 0, scrollFrame = 0, settleTimer = 0;
        let nativeGesture = false;
        let locked = false, running = false, lastWheel = 0, accumulated = 0;
        let lastDirection = 0;

        const update = () => {
            scrollFrame = 0;
            const range = document.documentElement.scrollHeight - window.innerHeight;
            root.style.setProperty('--fm-scroll-progress', String(range > 0 ? Math.min(1, Math.max(0, window.scrollY / range)) : 0));
            const probe = Math.min(160, window.innerHeight / 3);
            let active = sections[0];
            sections.forEach(section => {
                if (section.getBoundingClientRect().top <= probe) active = section;
                const rect = section.getBoundingClientRect();
                if (rect.top < window.innerHeight * .92 && rect.bottom > 0) section.classList.add('fm-visible');
            });
            if (active) setActiveSection(active.id);
        };
        const onScroll = () => {
            if (!scrollFrame) scrollFrame = requestAnimationFrame(update);
            if (nativeGesture && !running && !locked) {
                clearTimeout(settleTimer);
                settleTimer = setTimeout(settle, 180);
            }
        };
        const cancel = () => {
            cancelAnimationFrame(animation);
            clearTimeout(releaseTimer);
            clearTimeout(settleTimer);
            nativeGesture = false;
            root.classList.remove('fm-transitioning');
            animation = 0; locked = false; running = false; accumulated = 0;
        };
        const release = () => {
            clearTimeout(releaseTimer);
            releaseTimer = setTimeout(() => {
                if (!running) { locked = false; accumulated = 0; }
                else release();
            }, 220);
        };
        const move = (destination) => {
            cancelAnimationFrame(animation);
            const from = window.scrollY;
            if (reduce.matches) { window.scrollTo(0, destination); return; }
            const started = performance.now();
            const duration = Math.min(1100, Math.max(760, Math.abs(destination - from) * .28));
            nativeGesture = false;
            root.classList.add('fm-transitioning');
            locked = true; running = true;
            const step = now => {
                const progress = Math.min((now - started) / duration, 1);
                const ease = progress < .5 ? 4 * progress ** 3 : 1 - (-2 * progress + 2) ** 3 / 2;
                window.scrollTo(0, from + (destination - from) * ease);
                if (progress < 1) animation = requestAnimationFrame(step);
                else { running = false; animation = 0; root.classList.remove('fm-transitioning'); release(); }
            };
            animation = requestAnimationFrame(step);
        };
        // After a native gesture, softly align a nearby section edge. Never skip
        // the middle of a tall section or move while a menu/control is in use.
        const settle = () => {
            if (!nativeGesture || running || locked || reduce.matches || coarse.matches || root.querySelector('.card-nav.open')) return;
            nativeGesture = false;
            const y = window.scrollY;
            const max = document.documentElement.scrollHeight - window.innerHeight;
            const edges = sections.flatMap(section => {
                const rect = section.getBoundingClientRect();
                const top = rect.top + y;
                return [top, ...(rect.height > window.innerHeight + 3 ? [top + rect.height - window.innerHeight] : [])];
            }).map(edge => Math.max(0, Math.min(edge, max)));
            const ahead = edges.filter(edge => lastDirection > 0 ? edge >= y - 2 : edge <= y + 2);
            const nearest = ahead.sort((a, b) => Math.abs(a - y) - Math.abs(b - y))[0];
            if (nearest !== undefined && Math.abs(nearest - y) > 2 && Math.abs(nearest - y) < Math.min(140, window.innerHeight * .16)) move(nearest);
        };
        const nestedCanScroll = (target, direction) => {
            for (let node = target; node && node !== root; node = node.parentElement) {
                if (/(auto|scroll)/.test(getComputedStyle(node).overflowY) && node.scrollHeight > node.clientHeight + 1) {
                    if (direction > 0 ? node.scrollTop + node.clientHeight < node.scrollHeight - 1 : node.scrollTop > 0) return true;
                }
            }
            return false;
        };
        const wheel = event => {
            if (event.defaultPrevented || event.ctrlKey || event.metaKey || event.shiftKey || coarse.matches || reduce.matches) return;
            if (Math.abs(event.deltaX) > Math.abs(event.deltaY) || !event.deltaY) return;
            const target = event.target instanceof Element ? event.target : null;
            if (!target || target.closest('input, textarea, select, [contenteditable="true"], [role="dialog"], .card-nav')) return;
            if (root.querySelector('.card-nav.open')) return;
            const direction = Math.sign(event.deltaY);
            if (nestedCanScroll(target, direction)) return;
            if (locked) { event.preventDefault(); release(); return; }
            const geometry = sections.map(section => {
                const rect = section.getBoundingClientRect();
                return { top: rect.top + window.scrollY, bottom: rect.bottom + window.scrollY };
            });
            const destination = sectionTarget(geometry, window.scrollY, window.innerHeight, direction, document.documentElement.scrollHeight - window.innerHeight);
            if (destination === null || Math.abs(destination - window.scrollY) < 2) {
                accumulated = 0; lastDirection = direction; nativeGesture = true;
                clearTimeout(settleTimer);
                settleTimer = setTimeout(settle, 220);
                return;
            }
            event.preventDefault();
            const now = performance.now();
            if (now - lastWheel > 180 || direction !== lastDirection) accumulated = 0;
            lastWheel = now; lastDirection = direction;
            accumulated += Math.abs(event.deltaY) * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? window.innerHeight : 1);
            if (accumulated >= 28) { accumulated = 0; move(destination); }
        };
        const click = event => {
            const anchor = event.target instanceof Element ? event.target.closest('a[data-section-link], .logo-container a[href^="#"]') : null;
            if (!anchor || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
            const section = sections.find(item => '#' + item.id === anchor.getAttribute('href'));
            if (!section) return;
            event.preventDefault();
            event.stopPropagation();
            cancel();
            move(Math.min(section.getBoundingClientRect().top + window.scrollY, document.documentElement.scrollHeight - window.innerHeight));
            // Only deliberate navigation moves focus; wheel scrolling never steals it.
            section.focus({ preventScroll: true });
            window.history.replaceState(window.history.state, '', '#' + section.id);
        };
        const keyboard = event => { if (['Escape','Tab','PageDown','PageUp','Home','End','ArrowDown','ArrowUp',' '].includes(event.key)) cancel(); };
        root.classList.add('fm-scroll-ready');
        update();
        root.addEventListener('wheel', wheel, { passive: false });
        root.addEventListener('click', click, true);
        window.addEventListener('scroll', onScroll, { passive: true });
        window.addEventListener('resize', cancel);
        window.addEventListener('keydown', keyboard);
        window.addEventListener('pointerdown', cancel, { passive: true });
        window.addEventListener('touchstart', cancel, { passive: true });
        reduce.addEventListener('change', cancel);
        return () => {
            cancel(); cancelAnimationFrame(scrollFrame);
            root.classList.remove('fm-scroll-ready');
            root.removeEventListener('wheel', wheel);
            root.removeEventListener('click', click, true);
            root.style.removeProperty('--fm-scroll-progress');
            window.removeEventListener('scroll', onScroll);
            window.removeEventListener('resize', cancel);
            window.removeEventListener('keydown', keyboard);
            window.removeEventListener('pointerdown', cancel);
            window.removeEventListener('touchstart', cancel);
            reduce.removeEventListener('change', cancel);
        };
    }, [rootRef]);
    return activeSection;
}
