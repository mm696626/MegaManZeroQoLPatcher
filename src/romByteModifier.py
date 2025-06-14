import ips

def modify_byte_in_file(file_path, offset, old_byte, new_byte):
    try:
        with open(file_path, 'r+b') as file:
            file.seek(offset)
            current_byte = file.read(1)
            if current_byte == bytes([old_byte]):
                file.seek(offset)
                file.write(bytes([new_byte]))
    except Exception as e:
        print(f"Error: {e}")


def apply_ips_patch(file_path, save_path, ips_patch_file):
    try:
        with open(ips_patch_file, 'rb') as patch_file:
            patch_data = ips.Patch.load(patch_file)

        with open(file_path, "rb") as old, open(save_path, "wb") as new:
            patch_data.apply(old, new)

    except Exception as e:
        print(f"Error: {e}")