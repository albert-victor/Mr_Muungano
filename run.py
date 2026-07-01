"""Run Mr. Muungano server."""
import socket
import sys

import uvicorn

HOST = "127.0.0.1"
PORT = 8000


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0


if __name__ == "__main__":
    if _port_in_use(HOST, PORT):
        print()
        print("=" * 50)
        print("  PORT 8000 TAYARI INATUMIKA")
        print("  Server ya zamani bado inaendesha.")
        print()
        print("  Suluhisho 1: Fungua tab ya terminal iliyo na")
        print("  python run.py na ubonyeze Ctrl + C")
        print()
        print("  Suluhisho 2 (PowerShell):")
        print('  Get-NetTCPConnection -LocalPort 8000 |')
        print('    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }')
        print()
        print(f"  Kisha jaribu tena, au fungua: http://{HOST}:{PORT}")
        print("=" * 50)
        print()
        sys.exit(1)

    print()
    print("=" * 50)
    print("  Mr. Muungano — Server inaendesha")
    print("  Inapakia embedding model (sekunde 5-30, mara ya kwanza zaidi)…")
    print(f"  Fungua browser: http://{HOST}:{PORT}")
    print("  Usitumie 0.0.0.0 wala localhost/muunganoGPT (XAMPP)")
    print("  Simamisha: Ctrl + C")
    print("=" * 50)
    print()
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=False,
    )
