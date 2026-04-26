import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
from typing import Any, Optional, Callable

from constants import BASE_THEME, LIGHT_OVERRIDES
from utils import generate_random_name, distribute_probabilities
from wheel_renderer import WheelRenderer
from appearance_tab import AppearanceTab
from hidden_menu import open_hidden_menu

class SpinChartApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Spin Chart")
        self.minsize(650, 550)

        self.notebook: Optional[ttk.Notebook] = None
        self.main_tab: Optional[tk.Frame] = None
        self._wheel_resize_id: Optional[str] = None
        self._last_wheel_size: int = 0
        
        self.title_frame: Optional[tk.Frame] = None
        self.options_frame: Optional[tk.Frame] = None
        self.selection_frame: Optional[tk.Frame] = None
        self.spin_frame: Optional[tk.Frame] = None
        self.result_frame: Optional[tk.Frame] = None
        self.table_frame: Optional[tk.Frame] = None
        self.options_container: Optional[tk.Frame] = None

        self.title_label: Optional[ttk.Label] = None
        self.round_label: Optional[ttk.Label] = None
        self.result_label: Optional[ttk.Label] = None

        self.decrease_button: Optional[ttk.Button] = None
        self.increase_button: Optional[ttk.Button] = None
        self.spin_button: Optional[ttk.Button] = None
        self.stop_button: Optional[ttk.Button] = None
        self.add_option_button: Optional[ttk.Button] = None
        self.remove_option_button: Optional[ttk.Button] = None
        self.randomize_options_button: Optional[ttk.Button] = None

        self.result_table: Optional[ttk.Treeview] = None
        self.wheel_canvas: Optional[tk.Canvas] = None

        self.option_frames: list[tk.Frame] = []
        self.option_entries: list[ttk.Entry] = []
        self.random_names: list[Optional[str]] = []
        
        self.btn_frame: Optional[tk.Frame] = None
        self.round_btns: Optional[tk.Frame] = None
        self.top_frame: Optional[tk.Frame] = None
        self.bottom_frame: Optional[tk.Frame] = None
        self.btn_bar: Optional[tk.Frame] = None

        self.total_rounds = 1
        self.options: list[str] = []
        self.probabilities: list[float] = []
        self.original_probabilities: list[float] = []
        self.wins: dict[str, int] = {}
        self.round_number = 1
        self.max_options = 10
        self.min_options = 1
        self.current_wheel_angle = 0
        self.animation_job: Optional[str] = None
        self.stop_requested = False
        self.abort_spin = False

        self.wheel_visible: bool = False
        
        self.custom_wheel_colors: list[str] = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B739", "#52B788",
            "#FF8FAB", "#6C5CE7", "#FD79A8", "#74B9FF", "#A29BFE"
        ]

        self.base_font_size = 13
        self.min_font_size = 10
        self.max_font_size = 30
        self.resize_id: Optional[str] = None
        self.last_width = self.winfo_width()
        self.current_font_size = self.base_font_size

        self.is_dark_mode = False

        self.wheel_renderer = WheelRenderer()
        self.canvas_image_id: Optional[int] = None
        self.current_wheel_photo = None

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        tdict = self._get_current_theme_dict()
        self.main_tab = tk.Frame(self.notebook, bg=tdict["base_bg"])
        self.appearance_tab = AppearanceTab(self.notebook, self)
        
        self.notebook.add(self.main_tab, text="Spin Chart")
        self.notebook.add(self.appearance_tab, text="Appearance")

        self.bind("<Configure>", self.on_configure)
        self.bind_all("<Control-Shift-P>", self.open_hidden_menu)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.initialize_styles()
        self.create_widgets()
        self.apply_theme()

    def _get_current_theme_dict(self) -> dict[str, str]:
        theme_dict = BASE_THEME.copy()
        if not self.is_dark_mode:
            for k, v in LIGHT_OVERRIDES.items():
                theme_dict[k] = v
        return theme_dict

    def initialize_styles(self) -> None:
        label_styles = {
            'TitleLabel.TLabel': ('Helvetica Neue', 28, 'bold'),
            'RoundLabel.TLabel': ('Helvetica Neue', 14, None),
            'ResultLabel.TLabel': ('Helvetica Neue', 16, None),
            'WinnerLabel.TLabel': ('Helvetica Neue', 20, 'bold')
        }
        for style_name, font_def in label_styles.items():
            self.style.configure(style_name, font=font_def)

        btn_params = {
            'font': ('Helvetica Neue', 13, 'bold'),
            'foreground': '#FFFFFF',
            'padding': 8,
            'relief': 'flat',
            'borderwidth': 0
        }
        button_styles = [
            'Button.TButton', 'AddButton.TButton', 'RemoveButton.TButton',
            'IncreaseButton.TButton', 'DecreaseButton.TButton', 'RandomButton.TButton'
        ]
        for bs in button_styles:
            self.style.configure(bs, **btn_params)

        self.style.layout('Button.TButton', [
            ('Button.border', {'sticky': 'nswe', 'children': [
                ('Button.padding', {'sticky': 'nswe', 'children': [
                    ('Button.label', {'sticky': 'nswe'})
                ]})
            ]})
        ])

        self.style.configure('Custom.TEntry', font=('Helvetica Neue', 13), padding=4)
        self.style.configure('Treeview.Heading', font=('Helvetica Neue', 12, 'bold'))
        self.style.configure('Treeview', font=('Helvetica Neue', 10))

    def apply_theme(self) -> None:
        tdict = self._get_current_theme_dict()

        self.configure(bg=tdict["base_bg"])
        self.style.configure('.', background=tdict["base_bg"])

        self.style.configure('TNotebook', background=tdict["base_bg"], borderwidth=0, relief='flat', tabmargins=0)
        self.style.layout('TNotebook', [('Notebook.client', {'sticky': 'nswe'})])

        self.style.layout('TNotebook.Tab', [
            ('Notebook.tab', {
                'sticky': 'nswe',
                'children': [
                    ('Notebook.padding', {
                        'side': 'top',
                        'sticky': 'nswe',
                        'children': [
                            ('Notebook.label', {'side': 'top', 'sticky': ''})
                        ]
                    })
                ]
            })
        ])
        self.style.configure('TNotebook.Tab', background=tdict["entry_bg"], foreground=tdict["text_color"], padding=[10, 5], borderwidth=0)
        self.style.map('TNotebook.Tab', background=[('selected', tdict["base_bg"])], foreground=[('selected', tdict["title_color"])])

        self.style.configure('TitleLabel.TLabel', foreground=tdict["title_color"], background=tdict["base_bg"])
        self.style.configure('RoundLabel.TLabel', foreground=tdict["text_color"], background=tdict["base_bg"])
        self.style.configure('ResultLabel.TLabel', foreground=tdict["text_color"], background=tdict["base_bg"])
        self.style.configure('WinnerLabel.TLabel', foreground=tdict["winner_color"], background=tdict["base_bg"])

        self.style.configure('Custom.TEntry', fieldbackground=tdict["entry_bg"], foreground=tdict["text_color"])

        self.style.configure('Vertical.TScrollbar', background=tdict["base_bg"], troughcolor=tdict["base_bg"], borderwidth=0, arrowsize=0)

        self.style.configure('Treeview.Heading', foreground=tdict["text_color"], background=tdict["tree_heading_color"])
        self.style.configure('Treeview', foreground=tdict["text_color"], background=tdict["treeview_bg"], fieldbackground=tdict["treeview_field_bg"])

        self.style.configure('Button.TButton', background=tdict["button_bg"])
        self.style.configure('AddButton.TButton', background=tdict["add_button_bg"])
        self.style.configure('RemoveButton.TButton', background=tdict["remove_button_bg"])
        self.style.configure('IncreaseButton.TButton', background=tdict["increase_button_bg"])
        self.style.configure('DecreaseButton.TButton', background=tdict["decrease_button_bg"])
        self.style.configure('RandomButton.TButton', background=tdict["random_button_bg"])

        frames = [
            self.title_frame, self.options_frame, self.selection_frame,
            self.spin_frame, self.result_frame, self.table_frame,
            self.options_container, self.main_tab,
            self.btn_frame, self.round_btns,
            self.top_frame, self.bottom_frame, self.btn_bar
        ]
        for f in frames:
            if f is not None:
                f.configure(bg=tdict["base_bg"])

        for option_frame in self.option_frames:
            if option_frame is not None:
                option_frame.configure(bg=tdict["base_bg"])

        if self.wheel_canvas is not None:
            self.wheel_canvas.configure(bg=tdict["base_bg"])

        if hasattr(self, 'appearance_tab'):
            self.appearance_tab.apply_theme_colors(tdict)

        if self.wheel_canvas is not None:
            self.wheel_renderer.invalidate_cache()
            self.draw_wheel(self.current_wheel_angle)

    def toggle_theme(self) -> None:
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def create_labeled_frame(self, parent: tk.Widget, text: str, style: str) -> tk.Frame:
        tdict = self._get_current_theme_dict()
        frame = tk.Frame(parent, bg=tdict["base_bg"])
        lbl = ttk.Label(frame, text=text, style=style)
        lbl.pack()
        return frame

    def create_button(self, parent: tk.Widget, text: str, style: str, command: Callable[[], None], width: Optional[int] = None) -> ttk.Button:
        btn = ttk.Button(parent, text=text, style=style, command=command)
        if width is not None:
            btn.config(width=width)
        btn.pack(side='left', padx=5)
        return btn

    def on_configure(self, _event: Any) -> None:
        if self.resize_id:
            self.after_cancel(self.resize_id)
        self.resize_id = self.after(150, self._handle_resize)

    def _handle_resize(self) -> None:
        self.resize_fonts()
        if self.result_label:
            self.result_label.config(wraplength=self.winfo_width() - 40)
        self._update_wheel_size()

    def _update_wheel_size(self) -> None:
        if not self.wheel_canvas:
            return
        cw = self.wheel_canvas.winfo_width()
        ch = self.wheel_canvas.winfo_height()
        size = min(cw, ch)
        if size < 50 or abs(size - self._last_wheel_size) < 10:
            return
        self._last_wheel_size = size
        self.wheel_renderer.invalidate_cache()
        self.canvas_image_id = None
        self.wheel_canvas.delete("all")
        if self.wheel_visible:
            self.draw_wheel(self.current_wheel_angle)

    def create_widgets(self) -> None:
        tdict = self._get_current_theme_dict()
        parent = self.main_tab

        # --- Top bar: title + options + controls ---
        self.top_frame = tk.Frame(parent, bg=tdict["base_bg"])
        self.top_frame.pack(fill='x', padx=10, pady=(5, 2))

        self.title_frame = tk.Frame(self.top_frame, bg=tdict["base_bg"])
        self.title_frame.pack(anchor='center', pady=(5, 2))
        self.title_label = ttk.Label(self.title_frame, text="🏆 Spin Chart 🏆", style='TitleLabel.TLabel')
        self.title_label.pack()

        self.options_frame = tk.Frame(self.top_frame, bg=tdict["base_bg"])
        self.options_frame.pack(anchor='center', padx=10, pady=2)
        self.create_option_controls()

        # --- Middle: wheel (fills available space) ---
        self.spin_frame = tk.Frame(parent, bg=tdict["base_bg"])
        self.spin_frame.pack(fill='both', expand=True, padx=5, pady=2)

        self.wheel_canvas = tk.Canvas(self.spin_frame, highlightthickness=0, bg=tdict["base_bg"])
        self.wheel_canvas.pack(fill='both', expand=True)

        self.btn_bar = tk.Frame(self.spin_frame, bg=tdict["base_bg"])
        self.btn_bar.pack(pady=3)
        self.spin_button = self.create_button(parent=self.btn_bar, text="Spin the Wheel 🎡", style='Button.TButton', command=self.start_spin, width=18)
        self.stop_button = self.create_button(parent=self.btn_bar, text="Stop", style='Button.TButton', command=self.stop_spin, width=18)
        self.stop_button.config(state="disabled")

        # --- Bottom bar: round controls + result + table ---
        self.bottom_frame = tk.Frame(parent, bg=tdict["base_bg"])
        self.bottom_frame.pack(fill='x', padx=10, pady=(2, 5))

        self.selection_frame = tk.Frame(self.bottom_frame, bg=tdict["base_bg"])
        self.selection_frame.pack(anchor='center', pady=2)

        self.round_label = ttk.Label(self.selection_frame, text=f"Number of Rounds: {self.total_rounds}", style='RoundLabel.TLabel')
        self.round_label.pack(side='left', padx=5)

        self.round_btns = tk.Frame(self.selection_frame, bg=tdict["base_bg"])
        self.round_btns.pack(side='left')
        self.decrease_button = self.create_button(self.round_btns, "−", 'DecreaseButton.TButton', command=self.decrease_rounds, width=3)
        self.increase_button = self.create_button(self.round_btns, "+", 'IncreaseButton.TButton', command=self.increase_rounds, width=3)

        self.result_frame = tk.Frame(self.bottom_frame, bg=tdict["base_bg"])
        self.result_frame.pack(anchor='center', pady=2)
        self.result_label = ttk.Label(self.result_frame, text="Result: Not spun yet", style='ResultLabel.TLabel', wraplength=600)
        self.result_label.pack()

        self.table_frame = tk.Frame(self.bottom_frame, bg=tdict["base_bg"])
        self.table_frame.pack(fill='x', pady=(2, 5))
        self.setup_results_table()

    def setup_results_table(self) -> None:
        columns = ("Round", "Winner")
        self.result_table = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=8)
        self.result_table.heading("Round", text="Round")
        self.result_table.heading("Winner", text="Winner")
        self.result_table.column("Round", anchor="center", width=150)
        self.result_table.column("Winner", anchor="center", width=200)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.result_table.yview)
        self.result_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.result_table.pack(side="left", fill="both", expand=True)

    def create_option_controls(self) -> None:
        tdict = self._get_current_theme_dict()
        self.btn_frame = tk.Frame(self.options_frame, bg=tdict["base_bg"])
        self.btn_frame.pack(anchor='center', pady=3)

        consistent_width = 14
        self.add_option_button = self.create_button(self.btn_frame, "Add Option", 'AddButton.TButton', command=self.add_option, width=consistent_width)
        self.remove_option_button = self.create_button(self.btn_frame, "Remove Option", 'RemoveButton.TButton', command=self.remove_option, width=consistent_width)
        self.randomize_options_button = self.create_button(self.btn_frame, "Random", 'RandomButton.TButton', command=self.randomize_options, width=consistent_width)

        self.options_container = tk.Frame(self.options_frame, bg=tdict["base_bg"])
        self.options_container.pack(anchor='center', pady=2)

        self.option_frames.clear()
        self.option_entries.clear()
        self.random_names.clear()

        self.add_option()

    def center_options_grid(self) -> None:
        num_options = len(self.option_entries)
        num_cols = ((num_options - 1) // 2) + 1 if num_options else 1
        for col in range(num_cols):
            self.options_container.grid_columnconfigure(col, weight=1)

    def add_option(self) -> None:
        if len(self.option_entries) >= self.max_options:
            messagebox.showinfo("Maximum Options", f"You can only have up to {self.max_options} options.")
            return

        index = len(self.option_entries)
        tdict = self._get_current_theme_dict()
        option_frame = tk.Frame(self.options_container, bg=tdict["base_bg"])

        label = ttk.Label(option_frame, text=f"Option {index + 1}:", style='RoundLabel.TLabel')
        label.pack()

        entry = ttk.Entry(option_frame, width=18, style='Custom.TEntry')
        entry.pack(pady=1)

        row = index % 2
        col = index // 2
        option_frame.grid(row=row, column=col, padx=5, pady=2)

        self.option_frames.append(option_frame)
        self.option_entries.append(entry)
        self.random_names.append(None)

        if len(self.probabilities) != len(self.option_entries):
            self.probabilities = distribute_probabilities(100.0, len(self.option_entries))

        self.recalculate_probabilities()
        self.center_options_grid()

    def remove_option(self) -> None:
        if len(self.option_entries) <= self.min_options:
            messagebox.showinfo("Minimum Options", f"You must have at least {self.min_options} option.")
            return

        frame = self.option_frames.pop()
        frame.destroy()

        self.option_entries.pop()
        self.random_names.pop()

        for idx, f in enumerate(self.option_frames):
            row = idx % 2
            col = idx // 2
            f.grid_configure(row=row, column=col, padx=5, pady=2)

        if len(self.probabilities) != len(self.option_entries):
            self.probabilities = distribute_probabilities(100.0, len(self.option_entries))
        else:
            self.probabilities.pop()

        self.recalculate_probabilities()
        self.center_options_grid()

    def randomize_options(self) -> None:
        # Collect names that won't change (user-typed, non-random names)
        used_names: set[str] = set()
        indices_to_randomize: list[int] = []

        for i, entry in enumerate(self.option_entries):
            current_text = entry.get().strip()
            if not current_text or (self.random_names[i] is not None and current_text == self.random_names[i]):
                indices_to_randomize.append(i)
            else:
                used_names.add(current_text)

        for i in indices_to_randomize:
            new_name = generate_random_name()
            attempts = 0
            while new_name in used_names and attempts < 100:
                new_name = generate_random_name()
                attempts += 1
            used_names.add(new_name)
            entry = self.option_entries[i]
            entry.delete(0, tk.END)
            entry.insert(0, new_name)
            self.random_names[i] = new_name

    def recalculate_probabilities(self) -> None:
        num_options = len(self.option_entries)
        if num_options == 0:
            return
        if len(self.probabilities) != num_options:
            messagebox.showerror("Internal Error", "Mismatch between options and probabilities. Resetting probabilities.")
            self.probabilities = distribute_probabilities(100.0, num_options)
        else:
            self.probabilities = distribute_probabilities(100.0, num_options)

    def increase_rounds(self) -> None:
        self.total_rounds += 1
        self.round_label.config(text=f"Number of Rounds: {self.total_rounds}")

    def decrease_rounds(self) -> None:
        if self.total_rounds > 1:
            self.total_rounds -= 1
            self.round_label.config(text=f"Number of Rounds: {self.total_rounds}")

    def validate_probabilities(self) -> bool:
        if len(self.probabilities) != len(self.options):
            messagebox.showerror("Internal Error", "Mismatch between options and probabilities.")
            self.recalculate_probabilities()
            return False
        total = sum(self.probabilities)
        if abs(total - 100.0) > 1e-2:
            messagebox.showwarning("Invalid Probabilities", f"Total probabilities sum to {total:.2f}%. Must be 100%.")
            return False
        if any(prob < 0 or prob > 100 for prob in self.probabilities):
            messagebox.showwarning("Invalid Probabilities", "Each probability must be between 0 and 100%.")
            return False
        return True

    def start_spin(self) -> None:
        self.options = [entry.get().strip() for entry in self.option_entries]
        if any(not opt for opt in self.options):
            messagebox.showwarning("Incomplete Options", "Please name all options.")
            return
        if len(set(self.options)) != len(self.options):
            messagebox.showwarning("Duplicate Names", "Each option must be unique.")
            return
        if len(self.options) < 2:
            messagebox.showwarning("Insufficient Options", "Please add at least two options to spin the wheel.")
            return
        if not self.validate_probabilities():
            return

        self.wheel_visible = True
        self.draw_wheel(self.current_wheel_angle)

        winner = self.get_final_result()
        win_index = self.options.index(winner)
        n = len(self.options)

        sector_angle = 360.0 / n
        current_normalized = self.current_wheel_angle % 360
        pointer_angle = 270
        sector_center = 90 + (win_index * sector_angle)

        target_rotation = (sector_center - pointer_angle - current_normalized) % 360
        full_rotations = random.randint(4, 7) * 360
        final_angle = self.current_wheel_angle + full_rotations + target_rotation

        self.stop_requested = False
        self.abort_spin = False
        self.spin_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.result_label.config(text="Spinning...")

        spin_duration = random.randint(6000, 8000)
        self.animate_wheel_with_wobble(final_angle, duration=spin_duration, on_complete=lambda: self.end_spin(winner))

    def end_spin(self, predicted_winner: str) -> None:
        n = len(self.options)
        sector_angle = 360.0 / n
        half_sector = sector_angle / 2.0
        pointer_angle = 270

        normalized_rotation = self.current_wheel_angle % 360
        sector_at_pointer = (pointer_angle + normalized_rotation) % 360
        shift = 90 - half_sector
        adjusted_angle = (sector_at_pointer - shift) % 360
        sector_index = int(adjusted_angle / sector_angle) % n

        actual_winner = self.options[sector_index]

        sector_center = 90 + (sector_index * sector_angle)
        snap_rotation = (sector_center - pointer_angle) % 360
        self.current_wheel_angle = snap_rotation
        self.draw_wheel(self.current_wheel_angle)

        self.result_label.config(text=f"Round {self.round_number} Winner: {actual_winner}", style="ResultLabel.TLabel")
        self.result_table.insert('', 'end', values=(f"Round {self.round_number}", actual_winner))

        self.wins[actual_winner] = self.wins.get(actual_winner, 0) + 1
        self.round_number += 1

        if self.abort_spin or self.round_number > self.total_rounds:
            self.determine_overall_winner()
            self.round_number = 1
            self.wins.clear()
            self.spin_button.config(state="normal")
            self.stop_button.config(state="disabled")
        else:
            self.after(1500, self.start_spin)

    def get_final_result(self) -> str:
        cumulative = []
        total = 0.0
        for prob in self.probabilities:
            total += prob
            cumulative.append(total)
        rand_val = random.uniform(0, total)
        for option, cum_prob in zip(self.options, cumulative):
            if rand_val <= cum_prob:
                return option
        return self.options[-1]

    def stop_spin(self) -> None:
        self.stop_requested = True
        self.abort_spin = True
        self.spin_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def determine_overall_winner(self) -> None:
        if not self.wins:
            return
        max_wins = max(self.wins.values())
        winners = [option for option, w in self.wins.items() if w == max_wins]
        overall_winner = random.choice(winners)
        self.result_label.config(
            text=f"Overall Winner: {overall_winner}\n{overall_winner} has the highest number of wins!",
            style="WinnerLabel.TLabel"
        )
        self.result_label.config(wraplength=self.winfo_width() - 40)

    def animate_wheel_with_wobble(self, final_angle: float, duration: int, on_complete: Optional[Callable[[], None]] = None) -> None:
        import time

        start_time = time.time()
        start_angle = self.current_wheel_angle
        total_rotation = final_angle - start_angle
        duration_sec = duration / 1000.0

        target_fps = 60
        frame_delay = int(1000 / target_fps)

        def animate_step() -> None:
            if self.stop_requested:
                self.current_wheel_angle = final_angle % 360
                self.draw_wheel(self.current_wheel_angle)
                if on_complete:
                    on_complete()
                return

            current_time = time.time()
            elapsed = current_time - start_time

            if elapsed >= duration_sec:
                self.current_wheel_angle = final_angle % 360
                self.draw_wheel(self.current_wheel_angle)
                if on_complete:
                    self.after(50, on_complete)
                return

            progress = elapsed / duration_sec
            eased_progress = 1 - pow(1 - progress, 3)

            wobble_amount = 0
            if progress < 0.85:
                wobble_amount = math.sin(elapsed * 12) * (1 - progress)

            angle = start_angle + (total_rotation * eased_progress) + wobble_amount
            self.current_wheel_angle = angle
            self.draw_wheel(angle)

            self.after(frame_delay, animate_step)

        animate_step()

    def draw_wheel(self, rotation: float) -> None:
        if not self.wheel_canvas:
            return
        if not getattr(self, 'wheel_visible', False):
            return

        canvas_w = self.wheel_canvas.winfo_width()
        canvas_h = self.wheel_canvas.winfo_height()
        size = min(canvas_w, canvas_h)
        if size < 50:
            return

        options = [entry.get().strip() or f"Option {i + 1}" for i, entry in enumerate(self.option_entries)]
        tdict = self._get_current_theme_dict()
        bg_color = tdict["base_bg"]

        photo = self.wheel_renderer.get_rotated_wheel_image(size, size, rotation, options, self.custom_wheel_colors, bg_color)
        if photo is None:
            return

        self.current_wheel_photo = photo

        if self.canvas_image_id is None:
            self.wheel_canvas.delete("all")
            self.canvas_image_id = self.wheel_canvas.create_image(canvas_w // 2, canvas_h // 2, image=photo)
        else:
            self.wheel_canvas.itemconfig(self.canvas_image_id, image=photo)
            self.wheel_canvas.coords(self.canvas_image_id, canvas_w // 2, canvas_h // 2)

    def resize_fonts(self) -> None:
        current_width = self.winfo_width()
        if current_width == self.last_width:
            return
        self.last_width = current_width

        scale_factor = min(max(current_width / 800.0, 0.5), 1.2)
        new_font_size = max(self.min_font_size, min(int(self.base_font_size * scale_factor), self.max_font_size))

        if abs(new_font_size - self.current_font_size) < 1:
            return

        self.current_font_size = new_font_size
        self.update_all_font_styles(new_font_size)

    def update_all_font_styles(self, new_font_size: int) -> None:
        style_mapping = {
            'TitleLabel.TLabel': (2.1, 'bold'),
            'RoundLabel.TLabel': (1, None),
            'Button.TButton': (1, 'bold'),
            'AddButton.TButton': (1, 'bold'),
            'RemoveButton.TButton': (1, 'bold'),
            'IncreaseButton.TButton': (1, 'bold'),
            'DecreaseButton.TButton': (1, 'bold'),
            'RandomButton.TButton': (1, 'bold'),
            'Custom.TEntry': (1, None),
            'ResultLabel.TLabel': (1.2, None),
            'WinnerLabel.TLabel': (1.5, 'bold'),
            'Treeview.Heading': (1, None)
        }
        for style_name, (multiplier, weight) in style_mapping.items():
            computed_size = max(int(new_font_size * multiplier), self.min_font_size)
            font_tuple = ('Helvetica Neue', computed_size)
            if weight:
                font_tuple = (font_tuple[0], font_tuple[1], weight)
            self.style.configure(style_name, font=font_tuple)

    def open_hidden_menu(self, *args: Any) -> None:
        open_hidden_menu(self, *args)
