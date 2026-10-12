import { useEffect } from 'react';
import { gsap } from 'gsap';

// Entrances start after section scrolling ends, so the user actually sees them.
export default function useElementMotion(rootRef) {
    useEffect(() => {
        const root = rootRef.current;
        if (!root || !window.IntersectionObserver) return;
        const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
        const selector = [
            '.fm-eyebrow', '.fm-additions > h2', '.fm-new-section h2',
            '.fm-hero-details h2', '.fm-hero-details > p:not(.fm-eyebrow)',
            '.fm-intro', '.fm-card', '.fm-demo', '.fm-metric',
            '.fm-checklist li', '.fm-badges', '.fm-architecture',
            '.fm-test-note', '.fm-documents', '.fm-faq details',
            '.fm-final', '.fm-footer', '.fm-hero-details .fm-actions',
        ].join(',');
        const elements = [...root.querySelectorAll(selector)];
        const pending = new Set();
        const timelines = new Map();
        const children = [...root.querySelectorAll('.fm-chart polyline, .fm-badges span')];
        let frame = 0;
        const clear = element => gsap.set(element, { clearProps: 'opacity,transform,filter,willChange' });
        const preset = element => {
            if (element.matches('.fm-card, .fm-metric')) return { y: 100, scale: .92, rotationX: 7, transformPerspective: 900 };
            if (element.matches('h2')) return { x: -45, y: 24 };
            if (element.matches('.fm-architecture')) return { x: 70, y: 35, scale: .94 };
            if (element.matches('.fm-demo')) return { y: 80, scale: .94 };
            return { y: 42 };
        };
        const prepare = element => {
            timelines.get(element)?.kill();
            timelines.delete(element);
            pending.add(element);
            gsap.set(element, { opacity: 0, ...preset(element) });
        };
        const reveal = (element, batchDelay) => {
            pending.delete(element);
            const card = element.matches('.fm-card, .fm-metric');
            const siblings = card ? [...element.parentElement.children].filter(item => item.matches('.fm-card, .fm-metric')) : [];
            const delay = card ? Math.min(siblings.indexOf(element) * .2, .6) : Math.min(batchDelay, .35);
            const tl = gsap.timeline({ delay, onComplete: () => {
                clear(element);
                timelines.delete(element);
            } });
            timelines.set(element, tl);
            tl.to(element, {
                opacity: 1, x: 0, y: 0, scale: 1, rotationX: 0,
                duration: card ? 1.2 : 1,
                ease: card ? 'back.out(1.12)' : 'power3.out',
            });
            if (element.matches('.fm-demo')) {
                const line = element.querySelector('polyline');
                if (line) {
                    const length = line.getTotalLength();
                    tl.fromTo(line, { strokeDasharray: length, strokeDashoffset: length }, {
                        strokeDashoffset: 0, duration: 1.65, ease: 'power2.inOut',
                        clearProps: 'strokeDasharray,strokeDashoffset',
                    }, .35);
                }
            }
            if (element.matches('.fm-badges')) {
                tl.fromTo(element.children, { opacity: 0, y: 20, scale: .85 }, {
                    opacity: 1, y: 0, scale: 1, stagger: .1, duration: .55,
                    ease: 'back.out(1.5)', clearProps: 'opacity,transform',
                }, .2);
            }
        };
        const scan = () => {
            frame = 0;
            if (preference.matches) return;
            const moving = root.classList.contains('fm-transitioning');
            let delay = 0;
            for (const element of elements) {
                const rect = element.getBoundingClientRect();
                // Reset only once the element has completely left the viewport.
                if (rect.bottom < -120 || rect.top > window.innerHeight + 140) {
                    if (!pending.has(element)) prepare(element);
                    continue;
                }
                // Ignore entrance transform when checking the natural position.
                const y = Number(gsap.getProperty(element, 'y')) || 0;
                const top = rect.top - y;
                const bottom = rect.bottom - y;
                const visible = Math.min(bottom, window.innerHeight * .93) - Math.max(top, 0);
                const enough = visible >= Math.min(rect.height * .2, 85);
                if (!moving && pending.has(element) && enough) {
                    reveal(element, delay);
                    delay += .075;
                }
            }
        };
        const schedule = () => { if (!frame) frame = requestAnimationFrame(scan); };
        const observer = new IntersectionObserver(schedule, { threshold: [0, .15, .35, .7], rootMargin: '0px 0px -7% 0px' });
        // The scroll hook marks the end of its animated journey with this class.
        const movement = new MutationObserver(schedule);
        const restore = () => {
            timelines.forEach(timeline => timeline.kill());
            timelines.clear(); pending.clear();
            elements.forEach(clear);
            children.forEach(element => gsap.set(element, { clearProps: 'opacity,transform,strokeDasharray,strokeDashoffset' }));
        };
        const refresh = () => {
            restore();
            if (!preference.matches) elements.forEach(prepare);
            schedule();
        };
        const focus = event => {
            for (const element of elements) {
                if (element.contains(event.target)) {
                    timelines.get(element)?.kill(); timelines.delete(element);
                    pending.delete(element); clear(element);
                    element.querySelectorAll('.fm-badges span').forEach(clear);
                }
            }
        };
        root.classList.add('fm-motion-ready');
        refresh();
        elements.forEach(element => observer.observe(element));
        movement.observe(root, { attributes: true, attributeFilter: ['class'] });
        preference.addEventListener('change', refresh);
        root.addEventListener('focusin', focus);
        window.addEventListener('scroll', schedule, { passive: true });
        window.addEventListener('resize', schedule);
        return () => {
            observer.disconnect(); movement.disconnect(); cancelAnimationFrame(frame);
            restore();
            preference.removeEventListener('change', refresh);
            root.removeEventListener('focusin', focus);
            window.removeEventListener('scroll', schedule);
            window.removeEventListener('resize', schedule);
            root.classList.remove('fm-motion-ready');
        };
    }, [rootRef]);
}
