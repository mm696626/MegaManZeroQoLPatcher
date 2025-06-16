import tkinter as tk
from tkinter import messagebox

cyber_elf_cost_offsets = {
    'Zero 1': (0x2B727C, 0x2B729A),
    'Zero 2': (0x34A5C8, 0x34A5E5),
    'Zero 3': (0x36E2C4, 0x36E30B),
    'Zero 4': (0x886198, 0x8861A5)
}

def open_cyber_elf_cost_editor(rom_path, game_name):

    editor = tk.Toplevel()
    editor.title(f"Edit Cyber-Elf Costs - {game_name}")
    entries = []

    start_offset, end_offset = cyber_elf_cost_offsets[game_name]
    num_entries = (end_offset - start_offset) // 2 + 1

    display_indices = []

    def read_values():
        with open(rom_path, 'rb') as f:
            f.seek(start_offset)
            for i in range(num_entries):
                data = f.read(2)
                val = int.from_bytes(data, 'little')
                if val != 0:
                    var = tk.StringVar(value=str(val))
                    entries.append((i, var))
                    display_indices.append(i)

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

            messagebox.showinfo("Saved", "Cyber-Elf cost values updated successfully.")
            editor.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")

    read_values()

    for display_row, (index, var) in enumerate(entries):
        tk.Label(editor, text=f"Elf {display_row + 1}").grid(row=display_row, column=0, sticky="w", pady=2)
        tk.Entry(editor, textvariable=var, width=8).grid(row=display_row, column=1, padx=4)

    tk.Button(editor, text="Save and Close", command=write_values).grid(row=len(entries) + 1, column=0, columnspan=2, pady=10)
    editor.grab_set()
    editor.wait_window(editor)
