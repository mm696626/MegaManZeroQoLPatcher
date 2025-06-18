import tkinter as tk
from tkinter import messagebox
import fractions

weapon_offsets = {
    'Zero 1': {
        'Buster Shot': (0x2A8168, 4),
        'Z-Saber': (0x2A8184, 8),
        'Triple Rod': (0x2A81BE, 8),
        'Shield Boomerang': (0x2A81D6, 4),
        'Buster 4 Shot Upgrade': (0x188A2, 1),
        'Air Spin Slash': (0x18A60, 1),
        'Dash Spin Slash': (0x18A1C, 1),
    },
    'Zero 2': {
        'Buster Shot': (0x3359B4, 4),
        'Z-Saber': (0x3359C4, 8),
        'Chain Rod': (0x3359DA, 4),
        'Shield Boomerang': (0x3359E8, 4),
    }
}

def open_weapon_exp_editor(rom_path, game_name):
    editor = tk.Toplevel()
    editor.title(f"Modify Weapon EXP - {game_name}")
    entries = {}
    original_values = {}

    def read_values():
        with open(rom_path, 'rb') as f:
            for weapon, (offset, length) in weapon_offsets[game_name].items():
                f.seek(offset)
                data = f.read(length)
                if length > 1:
                    values = [
                        int.from_bytes(data[i:i+2], 'little') for i in range(0, length, 2)
                    ]
                else:
                    values = [data[0]]

                original_values[weapon] = values[:]
                entries[weapon] = [tk.StringVar(value=str(val)) for val in values]

    def write_values():
        try:
            with open(rom_path, 'r+b') as f:
                for weapon, (offset, length) in weapon_offsets[game_name].items():
                    f.seek(offset)
                    for var in entries[weapon]:
                        val_str = var.get().strip()
                        if not val_str.isdigit():
                            raise ValueError(
                                f"Invalid value '{val_str}' for {weapon}. Only non-negative integers are allowed.")
                        val = int(val_str)

                        if length == 1 or (length > 1 and len(entries[weapon]) == 1 and length == 1):
                            if not (1 <= val <= 255):
                                raise ValueError(f"Value {val} for {weapon} must be between 1 and 255.")
                            f.write(bytes([val]))
                        elif length > 1:
                            if not (1 <= val <= 65535):
                                raise ValueError(f"Value {val} for {weapon} must be between 1 and 65535.")
                            f.write(val.to_bytes(2, 'little'))

            messagebox.showinfo("Saved", "Weapon EXP values updated successfully.")
            editor.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")

    def apply_scale(factor):
        for weapon, vars_list in entries.items():
            max_val = 255 if len(vars_list) == 1 and weapon_offsets[game_name][weapon][1] == 1 else 65535
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

    def prompt_custom_scale():
        popup = tk.Toplevel(editor)
        popup.title("Custom Scale Factor")
        popup.grab_set()

        tk.Label(popup, text="Enter custom scale factor (> 0):\n(e.g., 0.5, 3/2, 150%)").pack(padx=10, pady=5)
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
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a valid positive number, fraction (e.g., 2/3), or percent (e.g., 150%)."
                )

        tk.Button(popup, text="Apply", command=apply).pack(pady=10)

    read_values()

    row = 0
    for weapon, vars_list in entries.items():
        tk.Label(editor, text=weapon).grid(row=row, column=0, sticky="w", pady=4)
        for i, var in enumerate(vars_list):
            tk.Entry(editor, textvariable=var, width=6).grid(row=row, column=i+1, padx=2)
        row += 1

    scale_frame = tk.Frame(editor)
    scale_frame.grid(row=row, column=0, columnspan=5, pady=5)

    tk.Label(scale_frame, text="Scale: ").pack(side=tk.LEFT)

    scale_fractions = [
        ("1/6", 1 / 6),
        ("1/4", 1 / 4),
        ("1/3", 1 / 3),
        ("1/2", 1 / 2),
        ("2/3", 2 / 3),
        ("3/4", 3 / 4),
        ("2", 2)
    ]

    for label, scale in scale_fractions:
        tk.Button(scale_frame, text=f"x{label}", command=lambda s=scale: apply_scale(s)).pack(side=tk.LEFT, padx=2)

    tk.Button(scale_frame, text="Custom", command=prompt_custom_scale).pack(side=tk.LEFT, padx=10)
    tk.Button(scale_frame, text="Reset", command=reset_values).pack(side=tk.LEFT, padx=10)

    row += 1
    tk.Button(editor, text="Save and Close", command=write_values).grid(row=row, column=0, columnspan=5, pady=10)

    editor.grab_set()
    editor.wait_window(editor)
