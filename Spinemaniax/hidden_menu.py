import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any

def open_hidden_menu(app_ref: Any, *args: Any) -> None:
    _ = args  # ignore event data
    app = app_ref

    app.options = [entry.get().strip() for entry in app.option_entries]
    if any(not option for option in app.options):
        messagebox.showwarning("Incomplete Options", "Please name all options before editing probabilities.")
        return
    if len(app.options) < 1:
        messagebox.showwarning("No Options", "Please add at least one option before setting probabilities.")
        return

    app.original_probabilities = app.probabilities.copy()
    dlg = tk.Toplevel(app)
    dlg.title("Set Winning Probabilities")
    dlg.grab_set()

    header = tk.Label(dlg, text="Set Winning Probabilities (0-100)",
                      font=('Helvetica Neue', 16, 'bold'))
    header.pack(pady=10)

    note = tk.Label(dlg, text=("Note: The numbers you see are rounded for clarity. "
                               "When you click 'Save', the full-precision values will be used "
                               "and adjusted to sum to 100%."),
                    font=('Helvetica Neue', 12), wraplength=400)
    note.pack(pady=5, padx=10)

    total_label_var = tk.StringVar()
    total_label = tk.Label(dlg, textvariable=total_label_var, font=('Helvetica Neue', 12))
    total_label.pack(pady=5)

    def update_total(*_ignored: Any) -> None:
        try:
            total_val = sum(float(pv.get().strip() or "0") for pv in prob_vars)
            if abs(total_val - 100) < 0.02:
                total_val = 100.0
            total_label_var.set(f"Total Probability: {round(total_val, 2):.2f}%")
        except ValueError:
            total_label_var.set("Total Probability: Invalid input")

    def validate_float(new_value: str) -> bool:
        if not new_value.strip():
            return True
        try:
            val = float(new_value)
            return 0.0 <= val <= 100.0
        except ValueError:
            return False

    vcmd = (dlg.register(validate_float), '%P')
    prob_vars = []
    for idx, option in enumerate(app.options):
        frame = tk.Frame(dlg)
        frame.pack(pady=5, padx=10, fill='x')

        lbl = tk.Label(frame, text=option, font=('Helvetica Neue', 12))
        lbl.pack(side='left')

        init_val = f"{app.probabilities[idx]:.2f}" if idx < len(app.probabilities) else "0.00"
        prob_var = tk.StringVar(value=init_val)
        prob_var.trace_add('write', update_total)
        prob_vars.append(prob_var)

        entry = ttk.Entry(frame, textvariable=prob_var, width=7, validate='key', validatecommand=vcmd)
        entry.pack(side='right', padx=5)

    update_total()

    def save_probabilities() -> None:
        entered_probs = []
        for i, pvar in enumerate(prob_vars):
            text_val = pvar.get().strip()
            if text_val == f"{app.original_probabilities[i]:.2f}":
                entered_probs.append(app.original_probabilities[i])
            else:
                try:
                    entered_probs.append(float(text_val))
                except ValueError:
                    messagebox.showerror("Invalid Input",
                                         "All probabilities must be valid numbers between 0 and 100.")
                    return

        modified_indices = [
            i for i, (new, orig) in enumerate(zip(entered_probs, app.original_probabilities))
            if abs(new - orig) > 1e-6
        ]
        set_sum = sum(entered_probs[i] for i in modified_indices)
        remaining_prob = 100.0 - set_sum
        if remaining_prob < 0:
            messagebox.showerror("Invalid Probabilities", "Total set probabilities exceed 100%.")
            return

        unset_indices = [i for i in range(len(app.options)) if i not in modified_indices]
        original_unset_sum = sum(app.original_probabilities[i] for i in unset_indices)

        if unset_indices:
            for idx2 in unset_indices:
                if original_unset_sum > 0:
                    new_prob = (app.original_probabilities[idx2] / original_unset_sum) * remaining_prob
                else:
                    new_prob = remaining_prob / len(unset_indices)
                entered_probs[idx2] = new_prob
        else:
            if abs(remaining_prob) > 1e-6:
                messagebox.showerror("Invalid Probabilities",
                                     f"No options left to distribute remaining {remaining_prob:.2f}%.")
                return

        # Round & fix float drift
        entered_probs = [round(p, 2) for p in entered_probs]
        diff = round(100.00 - sum(entered_probs), 2)
        if abs(diff) >= 0.01:
            max_index = max(range(len(entered_probs)), key=lambda i: entered_probs[i])
            entered_probs[max_index] = round(entered_probs[max_index] + diff, 2)

        final_total = sum(entered_probs)
        if abs(final_total - 100.0) > 1e-2:
            messagebox.showerror("Invalid Probabilities", f"Total probabilities sum to {final_total:.2f}%.")
            return
        if any(prob < 0.0 or prob > 100.0 for prob in entered_probs):
            messagebox.showerror("Invalid Probabilities", "Each probability must be between 0 and 100%.")
            return
        if len(set(app.options)) != len(app.options):
            messagebox.showerror("Duplicate Names", "Each option must be unique.")
            return

        app.probabilities = entered_probs
        dlg.destroy()

    save_button = ttk.Button(dlg, text="Save", command=save_probabilities, style='Button.TButton')
    save_button.pack(pady=10)
