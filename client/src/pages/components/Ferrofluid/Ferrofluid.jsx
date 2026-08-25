import { useRef, useEffect } from 'react';
import './style.css';

function FluidFlow({
    className = '',
    colors = ['#2E4E99', '#3E7DFF', '#DBF3FF'],
    speed = 0.4,
    waveCount = 4,
    particleCount = 40,
}) {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let animationFrame;
        let time = 0;
        let width, height, dpr;

        const particles = Array.from({ length: particleCount }, () => ({
            x: Math.random(),
            y: Math.random(),
            r: Math.random() * 2 + 0.5,
            speed: Math.random() * 0.15 + 0.05,
            drift: Math.random() * 0.4 - 0.2,
            alpha: Math.random() * 0.5 + 0.2,
        }));

        function resize() {
            dpr = Math.min(window.devicePixelRatio || 1, 2);
            width = canvas.clientWidth;
            height = canvas.clientHeight;
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }
        resize();
        window.addEventListener('resize', resize);

        function drawGrid() {
            const gridSize = 48;
            ctx.strokeStyle = 'rgba(219, 243, 255, 0.05)';
            ctx.lineWidth = 1;
            const offset = (time * 6) % gridSize;
            for (let x = -gridSize; x < width + gridSize; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x + offset, 0);
                ctx.lineTo(x + offset, height);
                ctx.stroke();
            }
            for (let y = -gridSize; y < height + gridSize; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y + offset * 0.4);
                ctx.lineTo(width, y + offset * 0.4);
                ctx.stroke();
            }
        }

        function drawWave(index) {
            const amplitude = height * (0.05 + index * 0.02);
            const yBase = height * (0.55 + index * 0.11);
            const wavelength = width / (1.4 + index * 0.3);
            const phase = time * speed * (0.6 + index * 0.15) + index * 2;

            const gradient = ctx.createLinearGradient(0, yBase - amplitude, 0, height);
            const c1 = colors[index % colors.length];
            gradient.addColorStop(0, c1 + 'CC');
            gradient.addColorStop(1, c1 + '00');

            ctx.beginPath();
            ctx.moveTo(0, height);
            for (let x = 0; x <= width; x += 8) {
                const y =
                    yBase +
                    Math.sin(x / wavelength + phase) * amplitude +
                    Math.sin(x / (wavelength * 0.5) + phase * 1.7) * (amplitude * 0.3);
                ctx.lineTo(x, y);
            }
            ctx.lineTo(width, height);
            ctx.closePath();
            ctx.fillStyle = gradient;
            ctx.fill();
        }

        function drawParticles() {
            particles.forEach((p) => {
                p.y -= p.speed * 0.002;
                p.x += Math.sin(time * 0.5 + p.y * 10) * 0.0006 * p.drift;
                if (p.y < -0.05) {
                    p.y = 1.05;
                    p.x = Math.random();
                }
                const px = p.x * width;
                const py = p.y * height;
                ctx.beginPath();
                ctx.arc(px, py, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(219, 243, 255, ${p.alpha})`;
                ctx.shadowColor = '#3E7DFF';
                ctx.shadowBlur = 6;
                ctx.fill();
                ctx.shadowBlur = 0;
            });
        }

        function render() {
            ctx.clearRect(0, 0, width, height);

            const bg = ctx.createLinearGradient(0, 0, 0, height);
            bg.addColorStop(0, '#10151B');
            bg.addColorStop(1, '#161D28');
            ctx.fillStyle = bg;
            ctx.fillRect(0, 0, width, height);

            drawGrid();
            for (let i = waveCount - 1; i >= 0; i--) drawWave(i);
            drawParticles();

            time += 0.016;
            animationFrame = requestAnimationFrame(render);
        }
        render();

        return () => {
            cancelAnimationFrame(animationFrame);
            window.removeEventListener('resize', resize);
        };
    }, [colors, speed, waveCount, particleCount]);

    return <canvas ref={canvasRef} className={`fluid-flow-canvas ${className}`} />;
}

export default FluidFlow;