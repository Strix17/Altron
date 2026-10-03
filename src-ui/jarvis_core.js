/**
 * ALTRON // JARVIS 3D HOLOGRAPHIC NEURAL CORE
 * Canvas rendering locked to 30 FPS with true 3D spherical orbital rotation.
 */

class JarvisNeuralCore {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.phase = 0;
    
    // Strict 30 FPS Throttling
    this.fps = 30;
    this.fpsInterval = 1000 / this.fps;
    this.lastDrawTime = performance.now();

    // Core state
    this.state = 'IDLE'; // 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING'
    this.pulseSpeed = 0.035;

    // Generate 3D Spherical Particle Cloud (inspired by JARVIS holographic sphere)
    this.particleCount = 140;
    this.particles = [];
    this.initParticles();

    // Handle Window Resize
    this.resize();
    window.addEventListener('resize', () => this.resize());

    // Start 30 FPS Animation Loop
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.width = rect.width;
    this.height = rect.height;
  }

  initParticles() {
    this.particles = [];
    for (let i = 0; i < this.particleCount; i++) {
      // Uniform point distribution on a sphere
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const r = 0.85 + (Math.random() * 0.3 - 0.15); // Slight depth variance

      this.particles.push({
        x: r * Math.sin(phi) * Math.cos(theta),
        y: r * Math.sin(phi) * Math.sin(theta),
        z: r * Math.cos(phi),
        baseSize: Math.random() * 2 + 1,
        speed: (Math.random() * 0.4 + 0.8),
        seed: Math.random() * Math.PI * 2
      });
    }
  }

  setState(newState) {
    this.state = newState.toUpperCase();
    const modeLabel = document.getElementById('core-mode-text');
    if (modeLabel) {
      modeLabel.textContent = `${this.state} // ACTIVE`;
    }
  }

  animate(currentTime) {
    requestAnimationFrame(this.animate);

    // Frame rate throttle to strictly 30 FPS
    const elapsed = currentTime - this.lastDrawTime;
    if (elapsed < this.fpsInterval) return;
    this.lastDrawTime = currentTime - (elapsed % this.fpsInterval);

    // Speed up rotation when processing or listening
    let rotSpeed = 0.025;
    if (this.state === 'LISTENING') rotSpeed = 0.055;
    if (this.state === 'THINKING') rotSpeed = 0.085;

    this.phase += rotSpeed;
    this.draw();
  }

  draw() {
    const { ctx, width, height, phase } = this;
    if (!width || !height) return;

    ctx.clearRect(0, 0, width, height);

    const cx = width / 2;
    const cy = height / 2;
    const baseRadius = Math.min(width, height) * 0.33;

    // --- 1. Outer 2D HUD Measurement Arcs & Tech Ticks ---
    this.drawHudRings(cx, cy, baseRadius);

    // --- 2. 3D Rotating Holographic Spherical Rings ---
    this.draw3DSphericalRings(cx, cy, baseRadius);

    // --- 3. 3D Spherical Particle Cloud with Depth Projection ---
    this.draw3DParticleCloud(cx, cy, baseRadius);

    // --- 4. Central Radiant Energy Core Vortex ---
    this.drawCentralVortex(cx, cy, baseRadius);
  }

  drawHudRings(cx, cy, radius) {
    const { ctx, phase } = this;

    // Outer faint boundary
    ctx.strokeStyle = '#07172B';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 1.25, 0, Math.PI * 2);
    ctx.stroke();

    // Rotating segment arcs
    const arcs = [
      { r: radius * 1.15, start: phase * 0.8, extent: 1.2, color: '#00A8FF', w: 1.5 },
      { r: radius * 1.15, start: phase * 0.8 + Math.PI, extent: 0.8, color: '#0077FF', w: 1.5 },
      { r: radius * 1.05, start: -phase * 1.2, extent: 1.6, color: '#00F0FF', w: 2 },
      { r: radius * 0.95, start: phase * 0.5, extent: 2.2, color: '#09223D', w: 1 }
    ];

    arcs.forEach(a => {
      ctx.strokeStyle = a.color;
      ctx.lineWidth = a.w;
      ctx.beginPath();
      ctx.arc(cx, cy, a.r, a.start, a.start + a.extent);
      ctx.stroke();
    });

    // Radial tick markers
    const ticks = 32;
    for (let i = 0; i < ticks; i++) {
      const angle = (i / ticks) * (Math.PI * 2) + phase * 0.1;
      const r1 = radius * 1.02;
      const r2 = radius * (i % 4 === 0 ? 1.08 : 1.04);
      ctx.strokeStyle = (i % 4 === 0) ? '#00A8FF' : '#09223D';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(angle) * r1, cy + Math.sin(angle) * r1);
      ctx.lineTo(cx + Math.cos(angle) * r2, cy + Math.sin(angle) * r2);
      ctx.stroke();
    }
  }

  draw3DSphericalRings(cx, cy, radius) {
    const { ctx, phase } = this;

    // Multiple 3D tilted planes rotating along X, Y, and Z
    const rings = [
      { rotX: 0.8, rotY: phase * 0.7, color: '#00F0FF', w: 1.5, scale: 0.95 },
      { rotX: -0.6, rotY: -phase * 0.9, color: '#00A8FF', w: 1.2, scale: 0.9 },
      { rotX: 0.2, rotY: phase * 1.1, color: '#0077FF', w: 1, scale: 0.85 },
      { rotX: 1.2, rotY: phase * 0.5, color: '#09223D', w: 1, scale: 0.75 }
    ];

    rings.forEach(ring => {
      const steps = 40;
      ctx.strokeStyle = ring.color;
      ctx.lineWidth = ring.w;
      ctx.beginPath();

      for (let i = 0; i <= steps; i++) {
        const theta = (i / steps) * Math.PI * 2;
        // Point on unit circle in XZ plane
        let x = Math.cos(theta) * radius * ring.scale;
        let y = 0;
        let z = Math.sin(theta) * radius * ring.scale;

        // Rotate 3D (Y axis then X axis)
        const cosY = Math.cos(ring.rotY), sinY = Math.sin(ring.rotY);
        const x1 = x * cosY + z * sinY;
        const z1 = -x * sinY + z * cosY;

        const cosX = Math.cos(ring.rotX), sinX = Math.sin(ring.rotX);
        const y2 = y * cosX - z1 * sinX;
        const z2 = y * sinX + z1 * cosX;

        // Perspective 3D projection
        const fov = 400;
        const scale = fov / (fov + z2);
        const px = cx + x1 * scale;
        const py = cy + y2 * scale;

        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();
    });
  }

  draw3DParticleCloud(cx, cy, radius) {
    const { ctx, phase, particles } = this;
    const fov = 420;

    // Rotation angles
    const rotY = phase * 0.6;
    const rotX = Math.sin(phase * 0.3) * 0.4;

    const cosY = Math.cos(rotY), sinY = Math.sin(rotY);
    const cosX = Math.cos(rotX), sinX = Math.sin(rotX);

    // Transform and sort particles by depth (Z-buffer for realism)
    const projected = particles.map(p => {
      const px = p.x * radius;
      const py = p.y * radius;
      const pz = p.z * radius;

      // 3D Rotate Y
      const x1 = px * cosY + pz * sinY;
      const z1 = -px * sinY + pz * cosY;

      // 3D Rotate X
      const y2 = py * cosX - z1 * sinX;
      const z2 = py * sinX + z1 * cosX;

      const scale = fov / (fov + z2);
      return {
        screenX: cx + x1 * scale,
        screenY: cy + y2 * scale,
        z: z2,
        scale: scale,
        baseSize: p.baseSize
      };
    });

    projected.sort((a, b) => a.z - b.z);

    // Draw glowing nodes and connective filaments
    projected.forEach((p, idx) => {
      const alpha = Math.max(0.15, Math.min(1.0, (p.z + radius) / (radius * 2)));
      const size = Math.max(1, p.baseSize * p.scale);

      ctx.fillStyle = idx % 5 === 0 ? `rgba(0, 240, 255, ${alpha})` : `rgba(0, 168, 255, ${alpha * 0.8})`;
      ctx.beginPath();
      ctx.arc(p.screenX, p.screenY, size, 0, Math.PI * 2);
      ctx.fill();

      // Connect nearby nodes with energy filaments
      if (idx % 6 === 0 && idx < projected.length - 1) {
        const next = projected[idx + 1];
        ctx.strokeStyle = `rgba(0, 168, 255, ${alpha * 0.3})`;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(p.screenX, p.screenY);
        ctx.lineTo(next.screenX, next.screenY);
        ctx.stroke();
      }
    });
  }

  drawCentralVortex(cx, cy, radius) {
    const { ctx, phase } = this;
    const pulse = 18 + Math.sin(phase * 4) * 4;

    // Glowing Radial Halo
    const grad = ctx.createRadialGradient(cx, cy, 2, cx, cy, pulse * 2.2);
    grad.addColorStop(0, 'rgba(0, 240, 255, 0.9)');
    grad.addColorStop(0.4, 'rgba(0, 168, 255, 0.4)');
    grad.addColorStop(1, 'rgba(0, 119, 255, 0)');

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, pulse * 2.2, 0, Math.PI * 2);
    ctx.fill();

    // Solid core and rings
    ctx.strokeStyle = '#00F0FF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, pulse * 0.9, 0, Math.PI * 2);
    ctx.stroke();

    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, Math.PI * 2);
    ctx.fill();
  }
}

// Instantiate on DOM load
window.addEventListener('DOMContentLoaded', () => {
  window.jarvisCore = new JarvisNeuralCore('jarvis-canvas');
});
