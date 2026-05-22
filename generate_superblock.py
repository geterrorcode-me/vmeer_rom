import os
import struct
import sys

def generate_vmeer_rom(rootfs_dir, output_rom_path, output_sb_path):
    """
    Membuat arsip datar readonly.bin dan berkas indeks superblock.bin
    yang kompatibel dengan VirtualFileSystem vMeerOS.
    """
    print("=========================================================")
    # Format biner C++: char file_path[256] (256 bytes), uint64_t offset (8 bytes), uint64_t size (8 bytes)
    # Total ukuran satu baris data struct = 272 bytes
    STRUCT_FORMAT = "<256sQQ" 
    
    files_to_pack = []
    
    # 1. Pindai seluruh direktori system secara rekursif
    system_path = os.path.join(rootfs_dir, "system")
    if not os.path.exists(system_path):
        print(f"ERROR: Direktori sistem {system_path} tidak ditemukan!")
        sys.exit(1)
        
    print(f"[*] Memindai berkas di dalam: {system_path}")
    for root, _, filenames in os.walk(system_path):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            # Dapatkan jalur virtual relatif untuk guest OS (misal /system/framework/framework.jar)
            rel_path = os.path.relpath(full_path, rootfs_dir)
            virtual_path = "/" + rel_path.replace("\\", "/")
            files_to_pack.append((full_path, virtual_path))

    # 2. Kemas seluruh berkas ke dalam readonly.bin secara berurutan
    print(f"[*] Mulai mengemas {len(files_to_pack)} berkas...")
    current_offset = 0
    
    with open(output_rom_path, "wb") as rom_file, open(output_sb_path, "wb") as sb_file:
        for full_path, virtual_path in files_to_pack:
            try:
                # Dapatkan ukuran berkas fisik
                file_size = os.path.getsize(full_path)
                
                # Baca dan tulis data mentah berkas ke readonly.bin
                with open(full_path, "rb") as f:
                    data = f.read()
                    rom_file.write(data)
                
                # Encode jalur virtual maksimal 255 karakter + null terminator
                encoded_path = virtual_path.encode('utf-8')[:255]
                
                # Kemas ke dalam biner struct C++
                sb_entry = struct.pack(STRUCT_FORMAT, encoded_path, current_offset, file_size)
                sb_file.write(sb_entry)
                
                # Geser offset penulisan berikutnya
                current_offset += file_size
                
            except Exception as e:
                print(f"[!] Gagal memproses berkas {virtual_path}: {str(e)}")
                
    print("[+] SUCCESS: Berkas readonly.bin dan superblock.bin berhasil dibangun!")
    print(f"    - Total ukuran ROM: {current_offset} bytes")
    print(f"    - Lokasi Superblock: {output_sb_path}")
    print("=========================================================")

if __name__ == "__main__":
    # Direktori kerja di GitHub Actions
    root_dir = "final_rootfs"
    rom_out = "readonly.bin"
    sb_out = "superblock.bin"
    
    generate_vmeer_rom(root_dir, rom_out, sb_out)
