import os

# 1. Define the files
input_file = "polymorphic_shell.exe"
output_file = "stealth_shell.exe"

# 2. Read the working small file
with open(input_file, "rb") as f:
    original_binary = f.read()

# 3. Create 101 MB of "Null Bytes" (Zeros)
# 1024 * 1024 = 1 MB. We multiply by 101.
padding_size = 101 * 1024 * 1024
padding = b'\x00' * padding_size

# 4. Write the original code FIRST, then the padding
with open(output_file, "wb") as f:
    f.write(original_binary)
    f.write(padding)

print(f"[+] Successfully created {output_file}")
print(f"[+] Final Size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")