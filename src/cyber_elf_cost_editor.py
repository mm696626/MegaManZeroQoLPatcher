import os
import tkinter as tk
from tkinter import messagebox, filedialog
import fractions
import random
import json

cyber_elf_cost_offsets = {
    'Zero 1': (0x2B727C, 0x2B729A),
    'Zero 2': (0x34A5C8, 0x34A5E5),
    'Zero 3': (0x36E2C4, 0x36E30B),
    'Zero 4': (0x886198, 0x8861A5)
}

DEFAULT_CONFIG_DIR = "default_configs"
os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)

def open_cyber_elf_cost_editor(rom_path, game_name):
    editor = tk.Toplevel()
    editor.title("Edit Croire Levels - Zero 4" if game_name == 'Zero 4' else f"Edit Cyber-Elf Costs - {game_name}")

    entries = []
    original_values = []

    start_offset, end_offset = cyber_elf_cost_offsets[game_name]
    num_entries = (end_offset - start_offset) // 2 + 1

    def read_values():
        with open(rom_path, 'rb') as f:
            f.seek(start_offset)
            for i in range(num_entries):
                data = f.read(2)
                val = int.from_bytes(data, 'little')
                if val != 0:
                    var = tk.StringVar(value=str(val))
                    entries.append((i, var))
                    original_values.append(val)

    def write_values():
        try:
            with open(rom_path, 'r+b') as f:
                for index, var in entries:
                    val_str = var.get().strip()
                    if not val_str.isdigit():
                        raise ValueError(f"Invalid input at entry {index + 1}. Must be a non-negative integer.")
                    val = int(val_str)
                    if not (1 <= val <= 65535):
                        raise ValueError(f"Value at entry {index + 1} out of range (1–65535).")
                    f.seek(start_offset + index * 2)
                    f.write(val.to_bytes(2, 'little'))
            editor.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")

    def apply_scale(factor):
        for _, var in entries:
            try:
                val = int(var.get())
                scaled = min(65535, max(1, int(val * factor)))
                var.set(str(scaled))
            except ValueError:
                pass

    def reset_values():
        for i, (_, var) in enumerate(entries):
            var.set(str(original_values[i]))

    def randomize_values():
        for _, var in entries:
            val = random.randint(1, 4000)
            var.set(str(val))

    def shuffle_values():
        values = [int(var.get()) for _, var in entries]
        random.shuffle(values)
        for (_, var), val in zip(entries, values):
            var.set(str(val))

    def prompt_custom_scale():
        popup = tk.Toplevel(editor)
        popup.title("Custom Cost Scale Factor")
        popup.grab_set()
        tk.Label(popup, text="Enter custom cost scale factor (> 0):\n(e.g., 0.5, 3/2, 150%)").pack(padx=10, pady=5)
        entry = tk.Entry(popup)
        entry.pack(padx=10, pady=5)

        def apply():
            try:
                input_str = entry.get().strip().replace(" ", "")
                if input_str.endswith('%'):
                    value = float(input_str.rstrip('%')) / 100
                else:
                    value = float(fractions.Fraction(input_str))
                if value <= 0:
                    raise ValueError
                apply_scale(value)
                popup.destroy()
            except (ValueError, ZeroDivisionError):
                messagebox.showerror("Invalid Input", "Enter a valid positive number, fraction (e.g., 2/3), or percent (e.g., 150%).")

        tk.Button(popup, text="Apply", command=apply).pack(pady=10)

    def export_config():
        data = {
            "game": game_name,
            "values": [var.get() for _, var in entries]
        }
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if path:
            try:
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                messagebox.showerror("Error", f"Could not export config:\n{e}")

    def import_config():
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            if data.get("game") != game_name:
                messagebox.showerror("Invalid Config", f"This config is for {data.get('game')}, not {game_name}.")
                return
            values = data.get("values", [])
            if len(values) != len(entries):
                messagebox.showerror("Invalid Config", "Number of entries does not match.")
                return
            for (_, var), val in zip(entries, values):
                var.set(str(val))
        except Exception as e:
            messagebox.showerror("Error", f"Could not import config:\n{e}")

    def save_as_default_config():
        data = {
            "game": game_name,
            "values": [var.get() for _, var in entries]
        }
        path = os.path.join(DEFAULT_CONFIG_DIR, f"default_cyberelf_{game_name.replace(' ', '')}.json")
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved", f"Default config saved for {game_name}.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save default config:\n{e}")

    read_values()

    default_config_path = os.path.join(DEFAULT_CONFIG_DIR, f"default_cyberelf_{game_name.replace(' ', '')}.json")
    if os.path.exists(default_config_path):
        try:
            with open(default_config_path, 'r') as f:
                data = json.load(f)
            if data.get("game") == game_name:
                values = data.get("values", [])
                if len(values) == len(entries):
                    for (_, var), val in zip(entries, values):
                        var.set(str(val))
        except Exception as e:
            print(f"Failed to load default cyber-elf config for {game_name}: {e}")

    for i, (index, var) in enumerate(entries):
        row = i // 3
        col = (i % 3) * 2
        label_text = f"Croire Level {i + 1}" if game_name == 'Zero 4' else f"Elf Cost {i + 1}"
        tk.Label(editor, text=label_text).grid(row=row, column=col, sticky="e", padx=2, pady=2)
        tk.Entry(editor, textvariable=var, width=8).grid(row=row, column=col + 1, padx=2)

    last_row = (len(entries) - 1) // 3 + 1
    scale_frame = tk.Frame(editor)
    scale_frame.grid(row=last_row + 1, column=0, columnspan=10, pady=10)
    tk.Label(scale_frame, text="Scale Costs: ").pack(side=tk.LEFT)

    for label, scale in [("1/6", 1/6), ("1/4", 1/4), ("1/2", 1/2), ("3/4", 3/4), ("2", 2)]:
        tk.Button(scale_frame, text=f"x{label}", command=lambda s=scale: apply_scale(s)).pack(side=tk.LEFT, padx=2)

    tk.Button(scale_frame, text="Custom", command=prompt_custom_scale).pack(side=tk.LEFT, padx=10)
    tk.Button(scale_frame, text="Reset", command=reset_values).pack(side=tk.LEFT, padx=10)
    tk.Button(scale_frame, text="Randomize", command=randomize_values).pack(side=tk.LEFT, padx=10)
    tk.Button(scale_frame, text="Shuffle", command=shuffle_values).pack(side=tk.LEFT, padx=10)

    button_frame = tk.Frame(editor)
    button_frame.grid(row=last_row + 2, column=0, columnspan=10, pady=10)
    tk.Button(button_frame, text="Import Config", command=import_config).pack(side="left", padx=5)
    tk.Button(button_frame, text="Export Config", command=export_config).pack(side="left", padx=5)
    tk.Button(button_frame, text="Save As Default Config", command=save_as_default_config).pack(side="left", padx=5)
    tk.Button(button_frame, text="Save and Close", command=write_values).pack(side="left", padx=5)

    editor.grab_set()
    editor.wait_window(editor)
