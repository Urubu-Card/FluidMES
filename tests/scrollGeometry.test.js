import test from 'node:test';
import assert from 'node:assert/strict';
import { nearestSectionTarget } from '../src/pages/landing/hooks/scrollGeometry.js';

const sections = [{ top: 0, bottom: 800 }, { top: 800, bottom: 1600 }, { top: 1600, bottom: 2400 }];
test('chooses the nearest section on either side without direction bias', () => {
    assert.equal(nearestSectionTarget(sections, 280, 800, 1600), 0);
    assert.equal(nearestSectionTarget(sections, 530, 800, 1600), 800);
    assert.equal(nearestSectionTarget(sections, 1030, 800, 1600), 800);
    assert.equal(nearestSectionTarget(sections, 1390, 800, 1600), 1600);
});
test('clamps the final section to the document scroll range', () => {
    assert.equal(nearestSectionTarget(sections, 1250, 800, 1350), 1350);
    assert.equal(nearestSectionTarget(sections, 0, 800, -100), 0);
});
test('long sections keep their middle readable and align near either edge', () => {
    const tall = [{ top: 0, bottom: 2400 }, { top: 2400, bottom: 3200 }];
    assert.equal(nearestSectionTarget(tall, 80, 800, 2400), 0);
    assert.equal(nearestSectionTarget(tall, 700, 800, 2400), null);
    assert.equal(nearestSectionTarget(tall, 1500, 800, 2400), 1600);
    assert.equal(nearestSectionTarget(tall, 2150, 800, 2400), 2400);
});
test('handles an empty page and an unavailable viewport', () => {
    assert.equal(nearestSectionTarget([], 0, 800, 0), null);
    assert.equal(nearestSectionTarget(sections, 0, 0, 0), null);
});
