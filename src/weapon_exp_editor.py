import tkinter as tk
from tkinter import messagebox

weapon_offsets = {
    'Zero 1': {
        'buster': (0x2A8168, 4),
        'saber': (0x2A8184, 8),
        'rod': (0x2A81BE, 8),
        'shield': (0x2A81D6, 4),
        'buster_shot_up': (0x188A2, 1),
        'air_saber': (0x18A60, 1),
        'dash_saber': (0x18A1C, 1),
    },
    'Zero 2': {
        'buster': (0x3359B4, 4),
        'saber': (0x3359C4, 8),
        'rod': (0x3359DA, 4),
        'shield': (0x3359E8, 4),
    }
}

def open_weapon_exp_editor(rom_path, game_name):
    editor = tk.Toplevel()
    editor.title(f"Modify Weapon EXP - {game_name}")
    entries = {}

    def read_values():
        with open(rom_path, 'rb') as f:
            for weapon, (offset, length) in weapon_offsets[game_name].items():
                f.seek(offset)
                data = f.read(length)
                if length > 1:
                    entries[weapon] = [
                        tk.StringVar(value=str(int.from_bytes(data[i:i+2], 'little')))
                        for i in range(0, length, 2)
                    ]
                else:
                    entries[weapon] = [tk.StringVar(value=str(data[0]))]

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

    read_values()

    row = 0
    for weapon, vars_list in entries.items():
        tk.Label(editor, text=weapon.capitalize()).grid(row=row, column=0, sticky="w", pady=4)
        for i, var in enumerate(vars_list):
            tk.Entry(editor, textvariable=var, width=6).grid(row=row, column=i+1, padx=2)
        row += 1

    tk.Button(editor, text="Save and Close", command=write_values).grid(row=row, column=0, columnspan=5, pady=10)
    editor.grab_set()
    editor.wait_window(editor)
