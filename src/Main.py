import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk
import hashlib
import os
import shutil
import json

import cyber_elf_cost_editor
import ips_patch_applier
import weapon_exp_editor

EXPECTED_MD5 = {
    'Zero 1': ['b24a17d080a01a404cbf018ba42b9803'],
    'Zero 2': ['182363b0698322e1864ced6e9eed7ead'],
    'Zero 3': ['aa1d5eeffcd5e4577db9ee6d9b1100f9'],
    'Zero 4': ['0d1e88bdb09ff68adf9877a121325f9c']
}

EXPECTED_SIZE = {
    'Zero 1': 8388608,
    'Zero 2': 8388608,
    'Zero 3': 8388608,
    'Zero 4': 16777216
}


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def check_rom_validity(file_path, game_name):
    file_size = os.path.getsize(file_path)
    expected_size = EXPECTED_SIZE.get(game_name)

    if file_size != expected_size:
        messagebox.showerror("Invalid ROM", f"Invalid file size for {game_name}. Expected size: {expected_size} bytes.")
        return False

    md5_hash = calculate_md5(file_path)
    expected_md5_list = EXPECTED_MD5.get(game_name)

    if md5_hash not in expected_md5_list:
        messagebox.showerror("Invalid ROM", f"Invalid MD5 for {game_name}. Expected one of: {expected_md5_list}.")
        return False

    return True


def copy_file(file_path, save_path):
    shutil.copy2(file_path, save_path)

def open_file(game_name):

    filetypes = [("GBA Files", "*.gba")]

    file_path = filedialog.askopenfilename(
        title=f"Open {game_name} ROM File",
        filetypes=filetypes
    )

    if file_path:
        if not check_rom_validity(file_path, game_name):
            return

        save_path = filedialog.asksaveasfilename(
            title=f"Save Modified {game_name} ROM File",
            defaultextension=".gba",
            filetypes=filetypes
        )

        if not save_path:
            return

        copy_file(file_path, save_path)
        show_patch_options(game_name, file_path, save_path)
    else:
        pass


def show_patch_options(game_name, file_path, save_path):
    def apply_patches():
        patch_list = []

        if game_name == 'Zero 1':
            if no_elf_penalty.get():
                patch_list.append("patches/mmz1_mission_penalty.ips")
            if retry_chips.get():
                patch_list.append("patches/mmz1_9_retries.ips")
            if blood_restore.get():
                patch_list.append("patches/mmz1_blood.ips")

        elif game_name == 'Zero 2':
            if blood_restore.get():
                patch_list.append("patches/mmz2_blood.ips")
            if ex_skill.get():
                patch_list.append("patches/mmz2_easyexskill.ips")
            if no_elf_penalty.get():
                patch_list.append("patches/mmz2_mission_penalty.ips")

        elif game_name == 'Zero 3':
            if blood_restore.get():
                patch_list.append("patches/mmz3_blood.ips")
            if ex_skill.get():
                patch_list.append("patches/mmz3_easyexskill.ips")
            if bn_viruses.get():
                patch_list.append("patches/mmz3_exevirus.ips")

        elif game_name == 'Zero 4':
            if blood_restore.get():
                patch_list.append("patches/mmz4_blood.ips")
            if vocal_restore.get():
                patch_list.append("patches/mmz4_vocals.ips")

        ips_patch_applier.apply_ips_patches(file_path, save_path, patch_list)
        patch_window.destroy()

        if modify_weapon_exp.get():
            weapon_exp_editor.open_weapon_exp_editor(save_path, game_name)

        if modify_cyber_elf_costs.get():
            cyber_elf_cost_editor.open_cyber_elf_cost_editor(save_path, game_name)

        messagebox.showinfo("Done", f"Patching for {game_name} is complete!")

    def export_patch_config():
        config = {
            'game': game_name,
            'options': {
                'blood_restore': blood_restore.get(),
                'vocal_restore': vocal_restore.get(),
                'ex_skill': ex_skill.get(),
                'bn_viruses': bn_viruses.get(),
                'retry_chips': retry_chips.get(),
                'no_elf_penalty': no_elf_penalty.get(),
                'modify_weapon_exp': modify_weapon_exp.get(),
                'modify_cyber_elf_costs': modify_cyber_elf_costs.get()
            }
        }
        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if save_path:
            try:
                with open(save_path, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Export Complete", "Patch configuration exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export patch config:\n{e}")

    def import_patch_config():
        load_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not load_path:
            return
        try:
            with open(load_path, 'r') as f:
                config = json.load(f)
            if config.get('game') != game_name:
                messagebox.showerror("Error", f"This config is for {config.get('game')}, not {game_name}.")
                return
            options = config.get('options', {})
            blood_restore.set(options.get('blood_restore', False))
            vocal_restore.set(options.get('vocal_restore', False))
            ex_skill.set(options.get('ex_skill', False))
            bn_viruses.set(options.get('bn_viruses', False))
            retry_chips.set(options.get('retry_chips', False))
            no_elf_penalty.set(options.get('no_elf_penalty', False))
            modify_weapon_exp.set(options.get('modify_weapon_exp', False))
            modify_cyber_elf_costs.set(options.get('modify_cyber_elf_costs', False))
            messagebox.showinfo("Import Complete", "Patch configuration imported successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not import patch config:\n{e}")

    def on_window_close():
        patch_window.destroy()

    patch_window = tk.Toplevel()
    patch_window.title(f"Select Patches for {game_name}")
    patch_window.protocol("WM_DELETE_WINDOW", on_window_close)

    blood_restore = tk.BooleanVar()
    vocal_restore = tk.BooleanVar()
    ex_skill = tk.BooleanVar()
    bn_viruses = tk.BooleanVar()
    retry_chips = tk.BooleanVar()
    no_elf_penalty = tk.BooleanVar()
    modify_weapon_exp = tk.BooleanVar()
    modify_cyber_elf_costs = tk.BooleanVar()

    if game_name in ['Zero 1']:
        tk.Checkbutton(patch_window, text="9 Retry Chips at Start of Game", variable=retry_chips).pack(anchor="w")
    if game_name in ['Zero 3']:
        tk.Checkbutton(patch_window, text="Battle Network Viruses Without Game Link", variable=bn_viruses).pack(anchor="w")
    tk.Checkbutton(patch_window, text="Blood Restoration", variable=blood_restore).pack(anchor="w")
    if game_name in ['Zero 2', 'Zero 3']:
        tk.Checkbutton(patch_window, text="Get EX Skill Regardless of Rank", variable=ex_skill).pack(anchor="w")
    if game_name in ['Zero 4']:
        tk.Checkbutton(patch_window, text="Japanese Vocal Restoration", variable=vocal_restore).pack(anchor="w")
    if game_name in ['Zero 1', 'Zero 2', 'Zero 3']:
        tk.Checkbutton(patch_window, text="Modify Cyber-Elf Costs", variable=modify_cyber_elf_costs).pack(anchor="w")
    if game_name in ['Zero 4']:
        tk.Checkbutton(patch_window, text="Modify Croire Costs", variable=modify_cyber_elf_costs).pack(anchor="w")
    if game_name in ['Zero 1', 'Zero 2']:
        tk.Checkbutton(patch_window, text="Modify Weapon EXP", variable=modify_weapon_exp).pack(anchor="w")
        tk.Checkbutton(patch_window, text="Remove Cyber-Elf Penalty on Rank", variable=no_elf_penalty).pack(anchor="w")

    btn_frame = tk.Frame(patch_window)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Import Config", command=import_patch_config).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export Config", command=export_patch_config).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Apply Patches", command=apply_patches).pack(side="left", padx=5)
    patch_window.wait_window(patch_window)

root = tk.Tk()
root.title("Mega Man Zero Series Quality of Life Patcher")
icon = PhotoImage(file='images/zero-icon.png')
root.iconphoto(True, icon)

frame1 = tk.Frame(root)
frame1.pack(padx=10, pady=10)

def load_image(image_path, size=(200, 200)):
    try:
        img = Image.open(image_path)
        img = img.resize(size)
        img_tk = ImageTk.PhotoImage(img)
        return img_tk
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

zero1_img = load_image("images/zero1.png")
zero2_img = load_image("images/zero2.png")
zero3_img = load_image("images/zero3.png")
zero4_img = load_image("images/zero4.png")

button1 = tk.Button(frame1, image=zero1_img, command=lambda: open_file('Zero 1'))
button1.grid(row=0, column=0, padx=10, pady=10)

button2 = tk.Button(frame1, image=zero2_img, command=lambda: open_file('Zero 2'))
button2.grid(row=0, column=1, padx=10, pady=10)

button3 = tk.Button(frame1, image=zero3_img, command=lambda: open_file('Zero 3'))
button3.grid(row=1, column=0, padx=10, pady=10)

button4 = tk.Button(frame1, image=zero4_img, command=lambda: open_file('Zero 4'))
button4.grid(row=1, column=1, padx=10, pady=10)

root.mainloop()