import ips
import io

def apply_ips_patches(file_path, save_path, ips_patch_files):
    try:
        with open(file_path, "rb") as f:
            rom_stream = io.BytesIO(f.read())

        for patch_file_path in ips_patch_files:
            with open(patch_file_path, 'rb') as patch_file:
                patch_data = ips.Patch.load(patch_file)

                patched_stream = io.BytesIO()
                patch_data.apply(rom_stream, patched_stream)

                patched_stream.seek(0)
                rom_stream = patched_stream

        with open(save_path, "wb") as f:
            f.write(rom_stream.read())

    except Exception as e:
        print(f"Error: {e}")