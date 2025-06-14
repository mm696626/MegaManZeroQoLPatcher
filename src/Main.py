import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk
import hashlib
import os
import shutil


EXPECTED_MD5 = {
    'Zero1': ['b24a17d080a01a404cbf018ba42b9803'],
    'Zero2': ['182363b0698322e1864ced6e9eed7ead'],
    'Zero3': ['aa1d5eeffcd5e4577db9ee6d9b1100f9'],
    'Zero4': ['0d1e88bdb09ff68adf9877a121325f9c']
}

EXPECTED_SIZE = {
    'Zero1': 8388608,
    'Zero2': 8388608,
    'Zero3': 8388608,
    'Zero4': 16777216
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
        answer = messagebox.askyesno("Invalid ROM", f"Invalid file size for {game_name}. Expected size: {expected_size} bytes. You should only continue if you know what you're doing. Do you want to continue anyway?")
        if not answer:
            return False

    md5_hash = calculate_md5(file_path)
    expected_md5_list = EXPECTED_MD5.get(game_name)

    if md5_hash not in expected_md5_list:
        answer = messagebox.askyesno("Invalid ROM", f"Invalid MD5 for {game_name}. Expected MD5: {expected_md5_list}. You should only continue if you know what you're doing. Do you want to continue anyway?")
        if not answer:
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
        show_patch_options(game_name, save_path)
    else:
        pass


def show_patch_options(game_name, save_path):
    def apply_patches():
        if game_name == 'Zero1':
            pass

        elif game_name == 'Zero2':
            pass

        elif game_name == 'Zero3':
            pass


        elif game_name == 'Zero4':
            pass

        patch_window.destroy()
        messagebox.showinfo("Done", f"Patching for {game_name} is complete!")

    def on_window_close():
        patch_window.destroy()

    patch_window = tk.Toplevel()
    patch_window.title(f"Select Patches for {game_name}")
    patch_window.protocol("WM_DELETE_WINDOW", on_window_close)

    blood_restore = tk.BooleanVar()
    vocal_restore = tk.BooleanVar()
    ex_skill = tk.BooleanVar()

    tk.Checkbutton(patch_window, text="Blood Restoration", variable=blood_restore).pack(anchor="w")
    if game_name in ['Zero2', 'Zero3']:
        tk.Checkbutton(patch_window, text="Get EX Skill Regardless of Rank", variable=ex_skill).pack(anchor="w")
    if game_name in ['Zero4']:
        tk.Checkbutton(patch_window, text="Vocal Restoration", variable=vocal_restore).pack(anchor="w")

    tk.Button(patch_window, text="Apply Patches", command=apply_patches).pack(pady=10)
    patch_window.wait_window(patch_window)

root = tk.Tk()
root.title("Mega Man Zero Series QoL Patcher")
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

button1 = tk.Button(frame1, image=zero1_img, command=lambda: open_file('Zero1'))
button1.grid(row=0, column=0, padx=10, pady=10)

button2 = tk.Button(frame1, image=zero2_img, command=lambda: open_file('Zero2'))
button2.grid(row=0, column=1, padx=10, pady=10)

button3 = tk.Button(frame1, image=zero3_img, command=lambda: open_file('Zero3'))
button3.grid(row=0, column=2, padx=10, pady=10)

button4 = tk.Button(frame1, image=zero4_img, command=lambda: open_file('Zero4'))
button4.grid(row=0, column=3, padx=10, pady=10)

root.mainloop()