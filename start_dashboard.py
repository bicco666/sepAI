#!/usr/bin/env python3
"""
Solana Trading Organisation Dashboard Startup Script

Dieses Script startet die komplette Applikation:
1. Startet den Backend-Server
2. Öffnet automatisch das Dashboard im Browser
3. Stellt sicher, dass alle Abteilungsdaten verfügbar sind
"""

import os
import sys
import time
import subprocess
import webbrowser
import requests
import signal
import threading
from pathlib import Path

# Konfiguration
HOST = "127.0.0.1"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"
DASHBOARD_URL = f"{BASE_URL}/"

# Pfad zur virtuellen Umgebung
VENV_PATH = Path(__file__).parent / "venv"
ACTIVATE_SCRIPT = VENV_PATH / "bin" / "activate"

def check_venv():
    """Prüft ob die virtuelle Umgebung existiert"""
    if not VENV_PATH.exists():
        print("❌ Virtuelle Umgebung nicht gefunden!")
        print("Bitte führen Sie zuerst 'python3 -m venv venv' aus.")
        return False
    return True

def wait_for_server(timeout=30):
    """Wartet bis der Server bereit ist"""
    print(f"⏳ Warte auf Server unter {BASE_URL}...")

    for i in range(timeout):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server ist bereit!")
                return True
        except requests.exceptions.RequestException:
            pass

        time.sleep(1)
        print(f"   Versuche {i+1}/{timeout}...")

    print("❌ Server konnte nicht erreicht werden!")
    return False

def check_agents_status():
    """Prüft und zeigt den Status der Abteilungen 2-5"""
    print("\n🏢 Prüfe Abteilungsstatus...")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/agents/status", timeout=5)
        if response.status_code == 200:
            agents = response.json()
            print("✅ Agent-Status erfolgreich geladen:")
            for dept, info in agents.items():
                status = info.get('status', 'UNKNOWN')
                version = info.get('version', 'N/A')
                print(f"   • {dept.capitalize()}: {status} (v{version})")
            return True
        else:
            print(f"❌ Agent-Status Fehler: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent-Status Fehler: {e}")
        return False

def check_wallet_status():
    """Prüft den Wallet-Status"""
    print("\n💰 Prüfe Wallet-Status...")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/wallet/status", timeout=5)
        if response.status_code == 200:
            wallet = response.json()
            network = wallet.get('network', 'UNKNOWN')
            address = wallet.get('address', 'N/A')[:20] + "..." if wallet.get('address') else 'N/A'
            print(f"✅ Wallet-Status: Netzwerk={network}, Adresse={address}")
            return True
        else:
            print(f"❌ Wallet-Status Fehler: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Wallet-Status Fehler: {e}")
        return False

def open_dashboard():
    """Öffnet das Dashboard im Browser"""
    print(f"\n🌐 Öffne Dashboard: {DASHBOARD_URL}")
    try:
        webbrowser.open(DASHBOARD_URL)
        print("✅ Dashboard im Browser geöffnet!")
    except Exception as e:
        print(f"❌ Konnte Browser nicht öffnen: {e}")
        print(f"Bitte öffnen Sie manuell: {DASHBOARD_URL}")

def check_server_running():
    """Prüft ob der Server bereits läuft"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Startet den Uvicorn-Server oder verwendet bestehenden"""
    print("🚀 Starte Solana Trading Organisation Dashboard...")
    print(f"📍 Server wird unter {BASE_URL} verfügbar sein")

    # Prüfe ob Server bereits läuft
    if check_server_running():
        print("✅ Server läuft bereits!")
        return "existing"

    # Aktiviere virtuelle Umgebung und starte Server
    cmd = [
        "bash", "-c",
        f"source {ACTIVATE_SCRIPT} && python -m uvicorn backend.main:app --host {HOST} --port {PORT} --reload"
    ]

    try:
        # Server im Hintergrund starten
        process = subprocess.Popen(
            cmd,
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Warte kurz für Server-Start
        time.sleep(3)

        # Prüfe ob Server läuft
        if process.poll() is None:  # Prozess läuft noch
            print("✅ Server erfolgreich gestartet!")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Server konnte nicht gestartet werden!")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return None

    except Exception as e:
        print(f"❌ Fehler beim Server-Start: {e}")
        return None

def main():
    """Hauptfunktion"""
    print("🎯 Solana Trading Organisation Dashboard Starter")
    print("=" * 50)

    # Prüfe virtuelle Umgebung
    if not check_venv():
        sys.exit(1)

    # Starte Server
    server_process = start_server()
    if not server_process:
        sys.exit(1)

    try:
        # Warte auf Server-Bereitschaft (nur wenn neu gestartet)
        if server_process != "existing":
            if not wait_for_server():
                print("❌ Server ist nicht bereit. Beende...")
                if server_process:
                    server_process.terminate()
                sys.exit(1)
        else:
            print("✅ Verwende bestehenden Server!")

        # Prüfe Systemstatus
        agents_ok = check_agents_status()
        wallet_ok = check_wallet_status()

        if agents_ok and wallet_ok:
            print("\n🎉 Alle Systeme bereit!")
        else:
            print("\n⚠️  Einige Systeme haben Probleme, aber Dashboard ist verfügbar.")

        # Öffne Dashboard
        open_dashboard()

        print("\n" + "=" * 50)
        print("📋 Dashboard ist bereit!")
        print(f"🌐 URL: {DASHBOARD_URL}")
        if server_process == "existing":
            print("ℹ️  Server wurde nicht gestartet (lief bereits)")
        else:
            print("🛑 Drücken Sie Ctrl+C zum Beenden")
        print("=" * 50)

        # Halte Script am Laufen (nur wenn Server gestartet wurde)
        if server_process != "existing":
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Beende Dashboard...")
                server_process.terminate()
                server_process.wait()
                print("✅ Dashboard beendet!")
        else:
            print("\n✅ Dashboard ist bereit! (Server läuft im Hintergrund)")
            print("ℹ️  Drücken Sie Enter zum Beenden...")
            input()

    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        if server_process and server_process != "existing":
            server_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()