// static/js/effects.js
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) {
        console.error('Particle canvas not found');
        return;
    }
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        particles = []; // Reset particles on resize
        initParticles();
    });

    let particles = [];
    const particleCount = 100;

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 2 + 1;
            this.speedX = Math.random() * 1 - 0.5;
            this.speedY = Math.random() * 1 - 0.5;
            this.color = 'rgba(255, 255, 255, 0.8)';
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.size > 0.1) this.size -= 0.01;

            if (this.x < 0 || this.x > width) this.speedX *= -1;
            if (this.y < 0 || this.y > height) this.speedY *= -1;
        }

        draw() {
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function initParticles() {
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }

    function handleParticles() {
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            if (particles[i].size <= 0.1) {
                particles.splice(i, 1);
                particles.push(new Particle()); // Add a new particle to maintain count
                i--;
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        handleParticles();
        requestAnimationFrame(animate);
    }

    initParticles();
    animate();

    // Theme toggle interaction with particle background
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            if (body.classList.contains('dark-theme')) {
                // If switching to light theme, particles might need adjustment or canvas background
                canvas.style.backgroundColor = '#f0f0f0'; // Example light background for canvas
                 particles.forEach(p => p.color = 'rgba(0, 0, 0, 0.5)'); // Darker particles for light bg
            } else {
                // If switching to dark theme
                canvas.style.backgroundColor = '#1a1a2e'; // Dark background for canvas
                particles.forEach(p => p.color = 'rgba(255, 255, 255, 0.8)'); // Lighter particles for dark bg
            }
            // Re-initialize particles for immediate color change if needed, or let them update naturally
            // For a smoother transition, you might want to fade colors or handle this more gracefully.
        });
    }
     // Ensure particle colors match initial theme
    canvas.style.backgroundColor = '#1a1a2e';
    particles.forEach(p => p.color = 'rgba(255, 255, 255, 0.8)');
});