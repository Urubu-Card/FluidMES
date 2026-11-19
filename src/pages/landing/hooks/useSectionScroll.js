import { useEffect, useState } from 'react';
import { nearestSectionTarget } from './scrollGeometry.js';

const SCROLL_IDLE_MS = 240;
const SCROLL_KEYS = new Set(['PageDown', 'PageUp', 'Home', 'End', 'ArrowDown', 'ArrowUp', ' ']);

export default function useSectionScroll(rootRef) {
    const [activeSection, setActiveSection] = useState('inicio');
    useEffect(() => {
        const root = rootRef.current;
        if (!root) return;
        const sections = [...root.querySelectorAll(':scope > section[id]')];
        const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
        const pressedKeys = new Set();
        let animation = 0, scrollFrame = 0, settleTimer = 0;
        let running = false, pending = false, pointerHeld = false, touchHeld = false;

        const update = () => {
            scrollFrame = 0;
            const range = document.documentElement.scrollHeight - window.innerHeight;
            root.style.setProperty('--fm-scroll-progress', String(range > 0 ? Math.min(1, Math.max(0, window.scrollY / range)) : 0));
            const probe = Math.min(160, window.innerHeight / 3);
            let active = sections[0];
            for (const section of sections) {
                const rect = section.getBoundingClientRect();
                if (rect.top <= probe) active = section;
                if (rect.top < window.innerHeight * .92 && rect.bottom > 0) section.classList.add('fm-visible');
            }
            if (active) setActiveSection(active.id);
        };
        const cancel = () => {
            cancelAnimationFrame(animation);
            clearTimeout(settleTimer);
            animation = 0; running = false; pending = false;
            root.classList.remove('fm-transitioning');
        };
        const move = destination => {
            cancel();
            const from = window.scrollY;
            if (Math.abs(destination - from) <= 2) return;
            if (reduce.matches) {
                window.scrollTo({ top: destination, behavior: 'instant' });
                return;
            }
            const started = performance.now();
            const duration = Math.min(650, Math.max(320, Math.abs(destination - from) * .45));
            running = true;
            root.classList.add('fm-transitioning');
            const step = now => {
                const progress = Math.min((now - started) / duration, 1);
                const ease = progress < .5 ? 4 * progress ** 3 : 1 - (-2 * progress + 2) ** 3 / 2;
                window.scrollTo({ top: from + (destination - from) * ease, behavior: 'instant' });
                if (progress < 1) animation = requestAnimationFrame(step);
                else { animation = 0; running = false; root.classList.remove('fm-transitioning'); }
            };
            animation = requestAnimationFrame(step);
        };
        const settle = () => {
            if (!pending || running || pointerHeld || touchHeld || pressedKeys.size || reduce.matches) return;
            pending = false;
            if (root.querySelector('.card-nav.open, [role="dialog"]')) return;
            const y = window.scrollY;
            const geometry = sections.map(section => {
                const rect = section.getBoundingClientRect();
                return { top: rect.top + y, bottom: rect.bottom + y };
            });
            const destination = nearestSectionTarget(geometry, y, window.innerHeight, document.documentElement.scrollHeight - window.innerHeight);
            if (destination !== null) move(destination);
        };
        const schedule = () => {
            clearTimeout(settleTimer);
            if (pending && !pointerHeld && !touchHeld && !pressedKeys.size) settleTimer = setTimeout(settle, SCROLL_IDLE_MS);
        };
        const onScroll = () => {
            if (!scrollFrame) scrollFrame = requestAnimationFrame(update);
            if (!running) { pending = true; schedule(); }
        };
        // Passive listeners leave wheel scrolling and trackpad momentum native.
        const wheel = () => cancel();
        const pointerDown = () => { cancel(); pointerHeld = true; };
        const pointerUp = () => { pointerHeld = false; schedule(); };
        const touchStart = () => { cancel(); touchHeld = true; };
        const touchEnd = event => { touchHeld = event.touches.length > 0; schedule(); };
        const keyDown = event => {
            if (SCROLL_KEYS.has(event.key)) { cancel(); pressedKeys.add(event.key); }
            else if (event.key === 'Escape' || event.key === 'Tab') cancel();
        };
        const keyUp = event => { pressedKeys.delete(event.key); schedule(); };
        const resetInput = () => {
            cancel(); pointerHeld = false; touchHeld = false; pressedKeys.clear();
        };
        const resize = () => { resetInput(); update(); };
        const click = event => {
            const anchor = event.target instanceof Element ? event.target.closest('a[data-section-link], .logo-container a[href^="#"]') : null;
            if (!anchor || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
            const section = sections.find(item => '#' + item.id === anchor.getAttribute('href'));
            if (!section) return;
            event.preventDefault();
            event.stopPropagation();
            move(Math.max(0, Math.min(section.getBoundingClientRect().top + window.scrollY, document.documentElement.scrollHeight - window.innerHeight)));
            section.focus({ preventScroll: true });
            window.history.replaceState(window.history.state, '', '#' + section.id);
        };
        const listeners = [
            [window, 'wheel', wheel, { passive: true }],
            [root, 'click', click, true],
            [window, 'scroll', onScroll, { passive: true }],
            [window, 'pointerdown', pointerDown, { passive: true }],
            [window, 'pointerup', pointerUp, { passive: true }],
            [window, 'pointercancel', pointerUp, { passive: true }],
            [window, 'touchstart', touchStart, { passive: true }],
            [window, 'touchend', touchEnd, { passive: true }],
            [window, 'touchcancel', touchEnd, { passive: true }],
            [window, 'keydown', keyDown], [window, 'keyup', keyUp],
            [window, 'blur', resetInput], [window, 'resize', resize],
            [reduce, 'change', resetInput],
        ];
        root.classList.add('fm-scroll-ready');
        update();
        for (const [target, type, listener, options] of listeners) target.addEventListener(type, listener, options);
        return () => {
            cancel(); cancelAnimationFrame(scrollFrame);
            for (const [target, type, listener, options] of listeners) target.removeEventListener(type, listener, options);
            root.classList.remove('fm-scroll-ready');
            root.style.removeProperty('--fm-scroll-progress');
        };
    }, [rootRef]);
    return activeSection;
}
