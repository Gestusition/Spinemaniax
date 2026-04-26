import tkinter as tk
from tkinter import ttk, colorchooser
import random
from typing import Any

class AppearanceTab(tk.Frame):
    def __init__(self, parent: tk.Widget, app_ref: Any) -> None:
        super().__init__(parent)
        self.app = app_ref
        self.create_config_toolbox()

    def create_config_toolbox(self) -> None:
        tdict = self.app._get_current_theme_dict()
        self.configure(bg=tdict["base_bg"])
        
        self.toolbox_frame = tk.Frame(self, bg=tdict["base_bg"])
        self.toolbox_frame.pack(pady=20, padx=20, fill='both', expand=True)

        header_label = ttk.Label(self.toolbox_frame, text="Appearance Settings", style="TitleLabel.TLabel")
        header_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Theme Options Frame
        self.theme_frame = tk.Frame(self.toolbox_frame, bg=tdict["base_bg"])
        self.theme_frame.grid(row=1, column=0, sticky="n", padx=10, pady=10)

        theme_label = ttk.Label(self.theme_frame, text="Theme Options", style="RoundLabel.TLabel")
        theme_label.pack(pady=5)

        btn_toggle_theme = ttk.Button(self.theme_frame, text="Toggle Dark/Light", command=self.app.toggle_theme,
                                      style='Button.TButton')
        btn_toggle_theme.pack(pady=10, padx=10)

        # Button Colors Frame
        self.button_color_frame = tk.Frame(self.toolbox_frame, bg=tdict["base_bg"])
        self.button_color_frame.grid(row=1, column=1, sticky="n", padx=10, pady=10)

        button_label = ttk.Label(self.button_color_frame, text="Button Colors", style="RoundLabel.TLabel")
        button_label.pack(pady=5)

        btn_set_color = ttk.Button(self.button_color_frame, text="Set Button Color",
                                   command=self.set_all_button_color, style='Button.TButton')
        btn_set_color.pack(pady=5, padx=10)

        btn_rand_color = ttk.Button(self.button_color_frame, text="Randomize Button Colors",
                                    command=self.randomize_all_button_colors, style='Button.TButton')
        btn_rand_color.pack(pady=5, padx=10)

        # Wheel Color Options Frame
        self.wheel_color_frame = tk.Frame(self.toolbox_frame, bg=tdict["base_bg"])
        self.wheel_color_frame.grid(row=2, column=0, columnspan=2, sticky="n", padx=10, pady=10)

        wheel_label = ttk.Label(self.wheel_color_frame, text="Wheel Colors", style="RoundLabel.TLabel")
        wheel_label.grid(row=0, column=0, columnspan=2, pady=5)

        btn_vibrant = ttk.Button(self.wheel_color_frame, text="🌈 Vibrant",
                                 command=self.set_vibrant_colors, style='Button.TButton')
        btn_vibrant.grid(row=1, column=0, pady=5, padx=5, sticky='ew')

        btn_pastel = ttk.Button(self.wheel_color_frame, text="🎨 Pastel",
                                command=self.set_pastel_colors, style='Button.TButton')
        btn_pastel.grid(row=1, column=1, pady=5, padx=5, sticky='ew')

        btn_neon = ttk.Button(self.wheel_color_frame, text="✨ Neon",
                              command=self.set_neon_colors, style='Button.TButton')
        btn_neon.grid(row=2, column=0, pady=5, padx=5, sticky='ew')

        btn_random_wheel = ttk.Button(self.wheel_color_frame, text="🎲 Random",
                                      command=self.randomize_wheel_colors, style='Button.TButton')
        btn_random_wheel.grid(row=2, column=1, pady=5, padx=5, sticky='ew')

        self.wheel_color_frame.grid_columnconfigure(0, weight=1)
        self.wheel_color_frame.grid_columnconfigure(1, weight=1)

        # Configure grid to expand properly
        self.toolbox_frame.grid_columnconfigure(0, weight=1)
        self.toolbox_frame.grid_columnconfigure(1, weight=1)
        self.toolbox_frame.grid_rowconfigure(0, weight=0)  # Header row - don't expand
        self.toolbox_frame.grid_rowconfigure(1, weight=0)  # Theme/Button row - don't expand
        self.toolbox_frame.grid_rowconfigure(2, weight=0)  # Wheel colors row - don't expand

    def set_all_button_color(self) -> None:
        chosen = colorchooser.askcolor()[1]
        if chosen:
            for style_name in [
                'Button.TButton', 'AddButton.TButton', 'RemoveButton.TButton',
                'IncreaseButton.TButton', 'DecreaseButton.TButton', 'RandomButton.TButton'
            ]:
                self.app.style.configure(style_name, background=chosen)

    def randomize_all_button_colors(self) -> None:
        for style_name in [
            'Button.TButton', 'AddButton.TButton', 'RemoveButton.TButton',
            'IncreaseButton.TButton', 'DecreaseButton.TButton', 'RandomButton.TButton'
        ]:
            rand_color = f"#{random.randint(0, 0xFFFFFF):06x}"
            self.app.style.configure(style_name, background=rand_color)

    def update_wheel_colors(self, colors: list[str]) -> None:
        self.app.custom_wheel_colors = colors
        self.app.wheel_renderer.invalidate_cache()
        self.app.draw_wheel(self.app.current_wheel_angle)

    def set_vibrant_colors(self) -> None:
        self.update_wheel_colors([
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B739", "#52B788",
            "#FF8FAB", "#6C5CE7", "#FD79A8", "#74B9FF", "#A29BFE"
        ])

    def set_pastel_colors(self) -> None:
        self.update_wheel_colors([
            "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF",
            "#D4A5A5", "#FFCCE5", "#E5CCFF", "#CCE5FF", "#CCFFCC",
            "#FFC8DD", "#BDE0FE", "#CDB4DB", "#FFC6FF", "#A2D2FF"
        ])

    def set_neon_colors(self) -> None:
        self.update_wheel_colors([
            "#FF006E", "#00F5FF", "#FFBE0B", "#8338EC", "#3A86FF",
            "#FB5607", "#FF006E", "#39FF14", "#FFEA00", "#FF10F0",
            "#00FFF0", "#FE4164", "#06FFA5", "#FFFF00", "#FF073A"
        ])

    def randomize_wheel_colors(self) -> None:
        self.update_wheel_colors([f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(15)])

    def apply_theme_colors(self, tdict: dict[str, str]) -> None:
        self.configure(bg=tdict["base_bg"])
        if hasattr(self, 'toolbox_frame'):
            self.toolbox_frame.configure(bg=tdict["base_bg"])
            self.theme_frame.configure(bg=tdict["base_bg"])
            self.button_color_frame.configure(bg=tdict["base_bg"])
            self.wheel_color_frame.configure(bg=tdict["base_bg"])
