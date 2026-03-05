import os

def inflate_binary(input_file, output_file, target_size_mb=101):
    # Read the original binary
    with open(input_file, 'rb') as f:
        original_data = f.read()
    
    # Calculate how much padding we need
    current_size = len(original_data)
    target_size_bytes = target_size_mb * 1024 * 1024
    padding_needed = target_size_bytes - current_size
    
    if padding_needed <= 0:
        print("File is already larger than the target size.")
        return

    # Create the inflated file
    with open(output_file, 'wb') as f:
        f.write(original_data)
        # Add "Null Bytes" (\x00) to the end of the file
        f.write(b'\x00' * padding_needed)
        
    print(f"Success! {output_file} is now {os.path.getsize(output_file) / (1024*1024):.2f} MB")

# Test it with a dummy file or a copy of notepad.exe
# inflate_binary("test.exe", "obfuscated.exe")