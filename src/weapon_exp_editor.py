import os
import tkinter as tk
from tkinter import messagebox, filedialog
import fractions
import random
import json

weapon_offsets = {
    'Zero 1': {
        'Buster Shot': (0x2A8168, 4, ["Charged Buster", "Faster Charge"]),
        'Z-Saber': (0x2A8184, 8, ["Second Slash", "Third Slash", "Charged Saber", "Faster Charge"]),
        'Triple Rod': (0x2A81BE, 8, ["Second Stab", "Third Stab", "Charged Rod", "Faster Charge"]),
        'Shield Boomerang': (0x2A81D6, 4, ["Farther Attack Range", "Farthest Attack Range"]),
        'Buster 4 Shot Upgrade': (0x188A2, 1),
        'Air Spin Slash': (0x18A60, 1),
        'Dash Spin Slash': (0x18A1C, 1),
    },
    'Zero 2': {
        'Buster Shot': (0x3359B4, 4, ["Charged Buster", "Faster Charge"]),
        'Z-Saber': (0x3359C4, 8, ["Second Slash", "Third Slash", "Charged Saber", "Faster Charge"]),
        'Chain Rod': (0x3359DA, 4, ["Charged Rod", "Faster Charge"]),
        'Shield Boomerang': (0x3359E8, 4, ["Farther Attack Range", "Farthest Attack Range"]),
    }
}

DEFAULT_CONFIG_DIR = "default_configs"
os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)

def open_weapon_exp_editor(rom_path, game_name):
    editor = tk.Toplevel()
    editor.title(f"Modify Weapon EXP - {game_name}")
    entries = {}
    original_values = {}

    def read_values():
        with open(rom_path, 'rb') as f:
            for weapon, data in weapon_offsets[game_name].items():
                offset, length = data[0], data[1]
                f.seek(offset)
                raw_data = f.read(length)
                if length > 1:
                    values = [
                        int.from_bytes(raw_data[i:i + 2], 'little') for i in range(0, length, 2)
                    ]
                else:
                    values = [raw_data[0]]
                original_values[weapon] = values[:]
                entries[weapon] = [tk.StringVar(value=str(val)) for val in values]

    def write_values():
        try:
            with open(rom_path, 'r+b') as f:
                for weapon, data in weapon_offsets[game_name].items():
                    offset, length = data[0], data[1]
                    f.seek(offset)
                    values = []
                    for var in entries[weapon]:
                        val_str = var.get().strip()
                        if not val_str.isdigit():
                            raise ValueError(
                                f"Invalid value '{val_str}' for {weapon}. Only non-negative integers are allowed.")
                        val = int(val_str)
                        values.append(val)

                    if len(values) > 1:
                        for i in range(1, len(values)):
                            if values[i] < values[i - 1]:
                                raise ValueError(
                                    f"EXP for {weapon} must not decrease (level {i + 1} < level {i}).")

                    for val in values:
                        if length == 1:
                            if not (1 <= val <= 255):
                                raise ValueError(f"Value {val} for {weapon} must be between 1 and 255.")
                            f.write(bytes([val]))
                        elif length > 1:
                            if not (1 <= val <= 65535):
                                raise ValueError(f"Value {val} for {weapon} must be between 1 and 65535.")
                            f.write(val.to_bytes(2, 'little'))
            editor.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")

    def apply_scale(factor):
        for weapon, vars_list in entries.items():
            offset, length = weapon_offsets[game_name][weapon][0], weapon_offsets[game_name][weapon][1]
            max_val = 255 if len(vars_list) == 1 and length == 1 else 65535
            for i, var in enumerate(vars_list):
                try:
                    val = int(var.get())
                    scaled = min(max_val, max(1, int(val * factor)))
                    var.set(str(scaled))
                except ValueError:
                    pass

    def reset_values():
        for weapon, original in original_values.items():
            for i, val in enumerate(original):
                entries[weapon][i].set(str(val))

    def randomize_values():
        for weapon, vars_list in entries.items():
            offset, length = weapon_offsets[game_name][weapon][0], weapon_offsets[game_name][weapon][1]
            max_val = 255 if length == 1 else 2000
            num_levels = len(vars_list)
            base = random.randint(1, max(1, max_val // (num_levels + 1)))
            values = [base]
            for _ in range(1, num_levels):
                increment = random.randint(1, max(1, (max_val - values[-1]) // (num_levels)))
                values.append(min(max_val, values[-1] + increment))
            for i, val in enumerate(values):
                vars_list[i].set(str(val))

    def prompt_custom_scale():
        popup = tk.Toplevel(editor)
        popup.title("Custom EXP Scale Factor")
        popup.grab_set()
        tk.Label(popup, text="Enter custom EXP scale factor (> 0):\n(e.g., 0.5, 3/2, 150%)").pack(padx=10, pady=5)
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
                messagebox.showerror("Invalid Input", "Please enter a valid positive number, fraction (e.g., 2/3), or percent (e.g., 150%).")

        tk.Button(popup, text="Apply", command=apply).pack(pady=10)

    def export_config():
        data = {
            "game": game_name,
            "values": {
                weapon: [var.get() for var in vars_list]
                for weapon, vars_list in entries.items()
            }
        }
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if path:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

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
            for weapon, values in data.get("values", {}).items():
                if weapon in entries:
                    for i, val in enumerate(values):
                        entries[weapon][i].set(val)
        except Exception as e:
            messagebox.showerror("Error", f"Could not import config:\n{e}")

    def save_as_default_config():
        data = {
            "game": game_name,
            "values": {
                weapon: [var.get() for var in vars_list]
                for weapon, vars_list in entries.items()
            }
        }
        path = os.path.join(DEFAULT_CONFIG_DIR, f"default_weaponexp_{game_name.replace(' ', '')}.json")
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save default config:\n{e}")

    read_values()

    default_config_path = os.path.join(DEFAULT_CONFIG_DIR, f"default_weaponexp_{game_name.replace(' ', '')}.json")
    if os.path.exists(default_config_path):
        try:
            with open(default_config_path, 'r') as f:
                data = json.load(f)
            if data.get("game") == game_name:
                for weapon, values in data.get("values", {}).items():
                    if weapon in entries:
                        for i, val in enumerate(values):
                            entries[weapon][i].set(val)
        except Exception as e:
            print(f"Failed to load default weapon EXP config for {game_name}: {e}")

    row = 0
    for weapon, vars_list in entries.items():
        data = weapon_offsets[game_name][weapon]
        labels = data[2] if len(data) == 3 else None

        tk.Label(editor, text=weapon).grid(row=row, column=0, sticky="w", pady=4)

        if labels:
            for i, label in enumerate(labels):
                tk.Label(editor, text=label).grid(row=row, column=i + 1)
            row += 1

        for i, var in enumerate(vars_list):
            tk.Entry(editor, textvariable=var, width=6).grid(row=row, column=i + 1, padx=2)

        row += 1

    scale_frame = tk.Frame(editor)
    scale_frame.grid(row=row, column=0, columnspan=5, pady=5)
    tk.Label(scale_frame, text="Scale EXP: ").pack(side=tk.LEFT)

    scale_fractions = [
        ("1/6", 1 / 6),
        ("1/4", 1 / 4),
        ("1/2", 1 / 2),
        ("3/4", 3 / 4),
        ("2", 2)
    ]
    for label, scale in scale_fractions:
        tk.Button(scale_frame, text=f"x{label}", command=lambda s=scale: apply_scale(s)).pack(side=tk.LEFT, padx=2)

    tk.Button(scale_frame, text="Custom", command=prompt_custom_scale).pack(side=tk.LEFT, padx=10)
    tk.Button(scale_frame, text="Reset", command=reset_values).pack(side=tk.LEFT, padx=10)
    tk.Button(scale_frame, text="Randomize", command=randomize_values).pack(side=tk.LEFT, padx=10)

    row += 1
    btn_frame = tk.Frame(editor)
    btn_frame.grid(row=row, column=0, columnspan=5, pady=10)
    tk.Button(btn_frame, text="Import Config", command=import_config).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export Config", command=export_config).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Save As Default Config", command=save_as_default_config).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Save and Close", command=write_values).pack(side="left", padx=5)

    editor.grab_set()
    editor.wait_window(editor)
