import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage, ttk
from PIL import Image, ImageTk
import hashlib
import os
import shutil
import json

import cyber_elf_cost_editor
import ips_patch_applier
import weapon_exp_editor

EXPECTED_MD5 = {
    'Zero 1': 'b24a17d080a01a404cbf018ba42b9803',
    'Zero 2': '182363b0698322e1864ced6e9eed7ead',
    'Zero 3': 'aa1d5eeffcd5e4577db9ee6d9b1100f9',
    'Zero 4': '0d1e88bdb09ff68adf9877a121325f9c'
}

EXPECTED_SIZE = {
    'Zero 1': 8388608,
    'Zero 2': 8388608,
    'Zero 3': 8388608,
    'Zero 4': 16777216
}

ROM_HEADER_SIGNATURES = {
    'Zero 1': b'MEGAMAN ZEROAZCE08',
    'Zero 2': b'MEGAMANZERO2A62E08',
    'Zero 3': b'MEGAMANZERO3BZ3E08',
    'Zero 4': b'MEGAMANZERO4B4ZE08'
}

SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load settings: {e}")
    return {"region": "US"}


def save_settings():
    settings = {"region": region.get()}
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Failed to save settings: {e}")


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def read_gba_rom_header(file_path):
    try:
        with open(file_path, 'rb') as f:
            f.seek(0xA0)
            return f.read(0xB2 - 0xA0)
    except Exception as e:
        print(f"Failed to read ROM header: {e}")
        return None

def check_rom_validity(file_path, game_name):
    file_size = os.path.getsize(file_path)
    expected_size = EXPECTED_SIZE.get(game_name)

    if file_size != expected_size:
        messagebox.showerror("Invalid ROM", f"Invalid file size for {game_name}. Expected size: {expected_size} bytes.")
        return False

    rom_header = read_gba_rom_header(file_path)
    expected_rom_header = ROM_HEADER_SIGNATURES.get(game_name)

    if rom_header != expected_rom_header:
        messagebox.showerror("Invalid ROM", f"Invalid header for {game_name}. Expected header: {expected_rom_header}.")
        return False

    md5_hash = calculate_md5(file_path)
    expected_md5 = EXPECTED_MD5.get(game_name)

    if md5_hash != expected_md5:
        messagebox.showerror("Invalid ROM", f"Invalid MD5 for {game_name}. Expected MD5 hash of: {expected_md5}.")
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
            if ex_skill.get():
                patch_list.append("patches/mmz2_easyexskill.ips")
            if no_elf_penalty.get():
                patch_list.append("patches/mmz2_mission_penalty.ips")
            if blood_restore.get():
                patch_list.append("patches/mmz2_blood.ips")

        elif game_name == 'Zero 3':
            if ex_skill.get():
                patch_list.append("patches/mmz3_easyexskill.ips")
            if bn_viruses.get():
                patch_list.append("patches/mmz3_exevirus.ips")
            if blood_restore.get():
                patch_list.append("patches/mmz3_blood.ips")

        elif game_name == 'Zero 4':
            if vocal_restore.get():
                patch_list.append("patches/mmz4_vocals.ips")
            if blood_restore.get():
                patch_list.append("patches/mmz4_blood.ips")

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

region = tk.StringVar()
region.set(load_settings().get("region", "US"))

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

patcher_tab = tk.Frame(notebook)
settings_tab = tk.Frame(notebook)
notebook.add(patcher_tab, text='Patcher')
notebook.add(settings_tab, text='Settings')


def load_image(image_base):
    suffix = "_jpn" if region.get() == "JPN" else ""
    image_path = f"images/{image_base}{suffix}.png"
    try:
        img = Image.open(image_path)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None



def load_game_buttons():
    for widget in patcher_tab.winfo_children():
        widget.destroy()

    zero1_img = load_image("zero1")
    zero2_img = load_image("zero2")
    zero3_img = load_image("zero3")
    zero4_img = load_image("zero4")

    tk.Button(patcher_tab, image=zero1_img, command=lambda: open_file('Zero 1')).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(patcher_tab, image=zero2_img, command=lambda: open_file('Zero 2')).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(patcher_tab, image=zero3_img, command=lambda: open_file('Zero 3')).grid(row=1, column=0, padx=10, pady=10)
    tk.Button(patcher_tab, image=zero4_img, command=lambda: open_file('Zero 4')).grid(row=1, column=1, padx=10, pady=10)

    patcher_tab.zero1_img = zero1_img
    patcher_tab.zero2_img = zero2_img
    patcher_tab.zero3_img = zero3_img
    patcher_tab.zero4_img = zero4_img


tk.Label(settings_tab, text="Box Art Region:").pack(pady=10)
region_dropdown = ttk.Combobox(settings_tab, textvariable=region, values=["US", "JPN"], state="readonly")
region_dropdown.pack()


def on_region_change(event=None):
    save_settings()
    load_game_buttons()


region_dropdown.bind("<<ComboboxSelected>>", on_region_change)

load_game_buttons()
root.mainloop()