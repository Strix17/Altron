"""Minimalist electric-blue HUD interface with animated JARVIS holographic neural core."""

from __future__ import annotations

import math
import time
import tkinter as tk
from collections.abc import Callable

import customtkinter as ctk


# --- Minimalist Cyber Blue Palette ---
BG_DARK = "#04070D"
PANEL_BG = "#080F18"
PANEL_CARD = "#0D1826"
BORDER_COLOR = "#12263F"
BORDER_BRIGHT = "#1E3D66"

BLUE_GLOW = "#00F0FF"
BLUE_PRIMARY = "#00A8FF"
BLUE_ACCENT = "#0077FF"
BLUE_DARK = "#09223D"
BLUE_DIM = "#07172B"

TEXT_PRIMARY = "#E6F4FF"
TEXT_SECONDARY = "#88A6C4"
TEXT_MUTED = "#486581"


class JarvisHologramCore(tk.Canvas):
    """Animated 3D holographic JARVIS neural sphere construct drawn on Canvas."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, bg=BG_DARK, highlightthickness=0, height=450)
        self.phase = 0.0
        self.bind("<Configure>", lambda _event: self._draw())
        self.after(25, self._animate)

    def _animate(self) -> None:
        self.phase += 0.035
        self._draw()
        self.after(25, self._animate)

    def _draw(self) -> None:
        self.delete("all")
        width, height = max(self.winfo_width(), 2), max(self.winfo_height(), 2)
        cx, cy = width / 2, height / 2
        radius = min(width, height) * 0.32

        # 1. Subtle Outer HUD Framing Brackets (Minimalist Tech Accents)
        bracket_pad = radius * 1.32
        b_len = 24
        # Top-left
        self.create_line(cx - bracket_pad, cy - bracket_pad + b_len, cx - bracket_pad, cy - bracket_pad, cx - bracket_pad + b_len, cy - bracket_pad, fill=BORDER_BRIGHT, width=1)
        # Top-right
        self.create_line(cx + bracket_pad - b_len, cy - bracket_pad, cx + bracket_pad, cy - bracket_pad, cx + bracket_pad, cy - bracket_pad + b_len, fill=BORDER_BRIGHT, width=1)
        # Bottom-left
        self.create_line(cx - bracket_pad, cy + bracket_pad - b_len, cx - bracket_pad, cy + bracket_pad, cx - bracket_pad + b_len, cy + bracket_pad, fill=BORDER_BRIGHT, width=1)
        # Bottom-right
        self.create_line(cx + bracket_pad - b_len, cy + bracket_pad, cx + bracket_pad, cy + bracket_pad, cx + bracket_pad, cy + bracket_pad - b_len, fill=BORDER_BRIGHT, width=1)

        # Top/Bottom telemetry slider bars
        self.create_line(cx - radius * 0.9, cy - bracket_pad, cx + radius * 0.9, cy - bracket_pad, fill=BLUE_DARK, width=1)
        self.create_line(cx - radius * 0.9, cy + bracket_pad, cx + radius * 0.9, cy + bracket_pad, fill=BLUE_DARK, width=1)
        
        # 2. Concentric Outer Orbit Arcs & Ring Ticks
        for idx, (scale, speed, width_val, col) in enumerate([
            (1.15, 0.4, 1, BLUE_DIM),
            (1.05, -0.6, 2, BLUE_DARK),
            (0.95, 0.8, 1, BLUE_ACCENT),
            (0.85, -0.5, 1, BLUE_DARK),
            (0.55, 1.2, 2, BLUE_PRIMARY),
        ]):
            r = radius * scale
            start_ang = (self.phase * speed * 50 + idx * 72) % 360
            self.create_oval(cx - r, cy - r, cx + r, cy + r, outline=BLUE_DIM, width=1)
            self.create_arc(cx - r, cy - r, cx + r, cy + r, start=start_ang, extent=65, outline=col, style="arc", width=width_val)
            self.create_arc(cx - r, cy - r, cx + r, cy + r, start=(start_ang + 180) % 360, extent=45, outline=col, style="arc", width=width_val)

        # 3. Outer Radial Tick Ring
        num_ticks = 36
        for i in range(num_ticks):
            angle = i * (math.tau / num_ticks) + (self.phase * 0.15)
            r_inner = radius * 0.98
            r_outer = radius * (1.04 if i % 4 == 0 else 1.01)
            t_col = BLUE_PRIMARY if i % 4 == 0 else BLUE_DARK
            x1, y1 = cx + math.cos(angle) * r_inner, cy + math.sin(angle) * r_inner
            x2, y2 = cx + math.cos(angle) * r_outer, cy + math.sin(angle) * r_outer
            self.create_line(x1, y1, x2, y2, fill=t_col, width=1)

        # 4. Multi-Axis 3D Tilted Elliptical Spherical Shells (JARVIS Neural Sphere)
        ellipses = [
            (0.0, 1.0, 0.45, BLUE_PRIMARY, 2),
            (math.pi / 4, 0.9, 0.55, BLUE_ACCENT, 1),
            (-math.pi / 4, 0.9, 0.55, BLUE_ACCENT, 1),
            (math.pi / 3, 0.8, 0.65, BLUE_DARK, 1),
            (-math.pi / 3, 0.8, 0.65, BLUE_DARK, 1),
            (math.pi / 2, 0.95, 0.35, BLUE_GLOW, 1),
        ]

        for base_rot, s_x, s_y, color, w in ellipses:
            rot = base_rot + self.phase * 0.4
            rx = radius * s_x
            ry = radius * s_y * abs(math.cos(self.phase * 0.3 + base_rot) * 0.6 + 0.4)
            
            # Draw wireframe orbit points
            pts = []
            steps = 28
            for s in range(steps):
                t = s * (math.tau / steps)
                # 3D unrotated coords
                px = rx * math.cos(t)
                py = ry * math.sin(t)
                # Rotate around center
                rx_rot = px * math.cos(rot) - py * math.sin(rot)
                ry_rot = px * math.sin(rot) + py * math.cos(rot)
                pts.append((cx + rx_rot, cy + ry_rot))

            for j in range(len(pts)):
                p1 = pts[j]
                p2 = pts[(j + 1) % len(pts)]
                self.create_line(p1[0], p1[1], p2[0], p2[1], fill=color, width=w)

        # 5. Swirling Neural Synapse Filaments & Particles
        num_synapses = 22
        for n in range(num_synapses):
            t_angle = n * (math.tau / num_synapses) + self.phase * (0.3 if n % 2 == 0 else -0.25)
            wobble = math.sin(self.phase * 2 + n) * 0.2
            dist_near = radius * (0.15 + 0.05 * math.cos(self.phase + n))
            dist_far = radius * (0.85 + wobble)

            x1 = cx + math.cos(t_angle) * dist_near
            y1 = cy + math.sin(t_angle) * dist_near
            x2 = cx + math.cos(t_angle + 0.4) * dist_far
            y2 = cy + math.sin(t_angle + 0.4) * dist_far

            # Filament line
            f_col = BLUE_DARK if n % 3 != 0 else BLUE_ACCENT
            self.create_line(x1, y1, x2, y2, fill=f_col, width=1)

            # Orbiting node
            progress = (math.sin(self.phase * 2.2 + n * 0.8) + 1.0) / 2.0
            nx = x1 + (x2 - x1) * progress
            ny = y1 + (y2 - y1) * progress
            node_r = 3 if n % 4 == 0 else 2
            node_color = BLUE_GLOW if n % 4 == 0 else BLUE_PRIMARY
            self.create_oval(nx - node_r, ny - node_r, nx + node_r, ny + node_r, fill=node_color, outline="")

        # 6. High-Energy Central Core Vortex
        core_pulse = 16 + 5 * math.sin(self.phase * 3.5)
        self.create_oval(cx - core_pulse * 1.8, cy - core_pulse * 1.8, cx + core_pulse * 1.8, cy + core_pulse * 1.8, fill="", outline=BLUE_DARK, width=1)
        self.create_oval(cx - core_pulse, cy - core_pulse, cx + core_pulse, cy + core_pulse, fill=BLUE_DARK, outline=BLUE_ACCENT, width=2)
        self.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill=BLUE_GLOW, outline="")
        self.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="#FFFFFF", outline="")

        # Core Label
        self.create_text(cx, cy + radius + 32, text="JARVIS NEURAL CORE // ACTIVE", fill=BLUE_PRIMARY, font=("Consolas", 10, "bold"))


class AppWindow(ctk.CTk):
    """Minimalist, modern electric-blue desktop UI shell."""

    def __init__(
        self,
        on_submit: Callable[[str], None],
        on_microphone: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        super().__init__()
        self.on_submit = on_submit
        self.on_microphone = on_microphone
        self.on_close_callback = on_close

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("ALTRON // AI DESKTOP ASSISTANT")
        self.geometry("1280x780")
        self.minsize(1050, 680)
        self.configure(fg_color=BG_DARK)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._build()

    def _build(self) -> None:
        # Minimalist Top Navbar
        navbar = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=10, height=64, border_width=1, border_color=BORDER_COLOR)
        navbar.pack(fill="x", padx=16, pady=(16, 10))
        navbar.pack_propagate(False)

        # Brand / Title
        brand_frame = ctk.CTkFrame(navbar, fg_color="transparent")
        brand_frame.pack(side="left", padx=20)
        ctk.CTkLabel(brand_frame, text="ALTRON", text_color=BLUE_GLOW, font=("Arial", 22, "bold")).pack(side="left")
        ctk.CTkLabel(brand_frame, text=" // NEURAL WORKSPACE", text_color=TEXT_MUTED, font=("Consolas", 11)).pack(side="left", padx=(4, 0))

        # Status Badge (Right aligned)
        self.status_label = ctk.CTkLabel(
            navbar,
            text="●  ONLINE",
            text_color=BLUE_GLOW,
            fg_color=BLUE_DIM,
            corner_radius=20,
            font=("Consolas", 11, "bold"),
            padx=16,
            pady=6,
        )
        self.status_label.pack(side="right", padx=20)

        # Main Content Grid (3 Columns)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=4)
        body.grid_columnconfigure(0, weight=1, minsize=260)
        body.grid_columnconfigure(1, weight=2, minsize=480)
        body.grid_columnconfigure(2, weight=1, minsize=300)
        body.grid_rowconfigure(0, weight=1)

        self._build_telemetry_panel(body)
        self._build_hologram_panel(body)
        self._build_chat_panel(body)
        self._build_input_bar()

    def _build_panel_header(self, parent: ctk.CTkFrame, title: str, subtitle: str) -> None:
        header_box = ctk.CTkFrame(parent, fg_color="transparent")
        header_box.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(header_box, text=title, text_color=TEXT_PRIMARY, font=("Consolas", 11, "bold")).pack(anchor="w")
        ctk.CTkLabel(header_box, text=subtitle, text_color=TEXT_MUTED, font=("Consolas", 9)).pack(anchor="w")

    def _build_telemetry_panel(self, parent: ctk.CTkFrame) -> None:
        panel = ctk.CTkFrame(parent, fg_color=PANEL_BG, border_width=1, border_color=BORDER_COLOR, corner_radius=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        self._build_panel_header(panel, "SYSTEM TELEMETRY", "OFFLINE LOGS & DIAGNOSTICS")

        self.system_log = ctk.CTkTextbox(
            panel,
            fg_color=PANEL_CARD,
            text_color=TEXT_SECONDARY,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_COLOR,
            font=("Consolas", 10),
            wrap="word",
        )
        self.system_log.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.system_log.insert("end", "[SYS] Altron core initialized.\n[WAKE] Listener active. Say 'Hey Jarvis'\n")
        self.system_log.configure(state="disabled")

    def _build_hologram_panel(self, parent: ctk.CTkFrame) -> None:
        panel = ctk.CTkFrame(parent, fg_color=PANEL_BG, border_width=1, border_color=BORDER_COLOR, corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew", padx=4)

        # Clean title over hologram
        ctk.CTkLabel(panel, text="NEURAL INTERFACE CONSTRUCT", text_color=TEXT_PRIMARY, font=("Consolas", 11, "bold")).pack(pady=(16, 2))
        ctk.CTkLabel(panel, text="JARVIS HOLOGRAPHIC QUANTUM CORE", text_color=TEXT_MUTED, font=("Consolas", 9)).pack(pady=(0, 4))

        # Animated Core Canvas
        self.core = JarvisHologramCore(panel)
        self.core.pack(fill="both", expand=True, padx=12, pady=4)

        # Quick Status Tip Pill
        info_pill = ctk.CTkFrame(panel, fg_color=PANEL_CARD, corner_radius=20, border_width=1, border_color=BORDER_COLOR)
        info_pill.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(
            info_pill,
            text="COMMAND READY  •  VOICE / PROMPT INPUT ENABLED",
            text_color=BLUE_PRIMARY,
            font=("Consolas", 9, "bold"),
        ).pack(pady=8)

    def _build_chat_panel(self, parent: ctk.CTkFrame) -> None:
        panel = ctk.CTkFrame(parent, fg_color=PANEL_BG, border_width=1, border_color=BORDER_COLOR, corner_radius=12)
        panel.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        self._build_panel_header(panel, "CONVERSATION STREAM", "INTENT ROUTER // GROQ")

        self.chat_log = ctk.CTkTextbox(
            panel,
            fg_color=PANEL_CARD,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_COLOR,
            font=("Segoe UI", 11),
            wrap="word",
        )
        self.chat_log.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.chat_log.insert("end", "◆ ALTRON: Systems online. How can I assist you today?\n\n")
        self.chat_log.configure(state="disabled")

    def _build_input_bar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color=PANEL_BG, border_width=1, border_color=BORDER_COLOR, corner_radius=12)
        bar.pack(fill="x", padx=16, pady=(10, 16))

        self.input_box = ctk.CTkEntry(
            bar,
            placeholder_text="Enter prompt or query (e.g., 'research quantum computing', 'volume up')...",
            fg_color=PANEL_CARD,
            border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            height=46,
            corner_radius=8,
            font=("Segoe UI", 12),
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(14, 8), pady=12)
        self.input_box.bind("<Return>", lambda _event: self._submit())

        # Minimalist Mic Button
        ctk.CTkButton(
            bar,
            text="MIC",
            width=70,
            height=46,
            fg_color=BLUE_DIM,
            hover_color=BLUE_DARK,
            text_color=BLUE_GLOW,
            border_width=1,
            border_color=BORDER_BRIGHT,
            corner_radius=8,
            command=self.on_microphone,
            font=("Consolas", 11, "bold"),
        ).pack(side="left", padx=4, pady=12)

        # Minimalist Send Button
        ctk.CTkButton(
            bar,
            text="SEND",
            width=84,
            height=46,
            fg_color=BLUE_ACCENT,
            hover_color=BLUE_PRIMARY,
            text_color="#FFFFFF",
            corner_radius=8,
            command=self._submit,
            font=("Consolas", 11, "bold"),
        ).pack(side="left", padx=(4, 14), pady=12)

    def _submit(self) -> None:
        text = self.input_box.get().strip()
        if text:
            self.input_box.delete(0, "end")
            self.on_submit(text)

    def set_status(self, status: str) -> None:
        """Safely update visible status from a background worker."""
        self.after(0, lambda: self.status_label.configure(text=f"●  {status.upper()}"))

    def add_chat(self, speaker: str, message: str) -> None:
        def append() -> None:
            self.chat_log.configure(state="normal")
            marker = "◆" if speaker == "ALTRON" else "›"
            self.chat_log.insert("end", f"{marker} {speaker}: {message}\n\n")
            self.chat_log.see("end")
            self.chat_log.configure(state="disabled")
        self.after(0, append)

    def add_system_log(self, message: str, success: bool = True) -> None:
        def append() -> None:
            tag = "OK" if success else "ERR"
            self.system_log.configure(state="normal")
            self.system_log.insert("end", f"[{time.strftime('%H:%M:%S')}] {tag}: {message}\n")
            self.system_log.see("end")
            self.system_log.configure(state="disabled")
        self.after(0, append)

    def _close(self) -> None:
        self.on_close_callback()
        self.destroy()

