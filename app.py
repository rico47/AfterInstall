#!/usr/bin/env python3

import subprocess

# Domyślna lista programów do zainstalowania
PROGRAMY_DO_INSTALACJI = [
    "sane",
    "sane-airscan",
]

# Domyślna lista usług (daemonów) do włączenia i uruchomienia
USLUGI_DO_ZARZADZANIA = [
    "avahi-daemon",
]

def sprawdz_uprawnienia(log_callback):
    """Sprawdza, czy skrypt jest uruchomiony z uprawnieniami roota."""
    if subprocess.run(["id", "-u"], capture_output=True, text=True).stdout.strip() != "0":
        log_callback("Błąd: Skrypt musi być uruchomiony jako root (użyj 'sudo').")
        return False
    return True

def wykonaj_polecenie(komenda, log_callback):
    """Wykonuje polecenie systemowe i obsługuje błędy."""
    try:
        process = subprocess.Popen(komenda, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ''):
            log_callback(line.strip())
        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            log_callback(f"❌ Polecenie zakończone z kodem błędu: {return_code}")
            return False
            
        log_callback(f"✅ Pomyślnie wykonano: {' '.join(komenda)}")
        return True
    except FileNotFoundError:
        log_callback(f"❌ Błąd: Polecenie '{komenda[0]}' nie zostało znalezione.")
        return False

def get_install_commands(package_manager):
    """Zwraca komendy instalacyjne dla danego menedżera pakietów."""
    if package_manager == "pacman":
        return ["pacman", "-Syu", "--noconfirm"], ["pacman", "-S", "--noconfirm"]
    elif package_manager == "apt":
        return ["apt-get", "update"], ["apt-get", "install", "-y"]
    elif package_manager == "dnf":
        return ["dnf", "update", "-y"], ["dnf", "install", "-y"]
    else:
        return None, None

def instaluj_programy(lista_programow, log_callback, package_manager):
    """Instaluje listę programów za pomocą wybranego menedżera pakietów."""
    if not lista_programow:
        log_callback("Nie wybrano żadnych programów do instalacji.")
        return True

    log_callback(f"🚀 Rozpoczynam instalację programów przy użyciu: {package_manager}...")
    
    cmd_update, cmd_install = get_install_commands(package_manager)
    if not cmd_update:
        log_callback(f"❌ Nieobsługiwany menedżer pakietów: {package_manager}")
        return False

    # Aktualizacja systemu
    if not wykonaj_polecenie(cmd_update, log_callback):
        log_callback("❌ Aktualizacja systemu nie powiodła się.")
        return False
        
    # Instalacja programów
    komenda_instalacji = cmd_install + lista_programow
    if not wykonaj_polecenie(komenda_instalacji, log_callback):
        log_callback("❌ Instalacja programów nie powiodła się.")
        return False
        
    log_callback("✅ Instalacja zakończona pomyślnie!")
    return True

def zarzadzaj_uslugami(lista_uslug, log_callback):
    """Zarządza usługami systemowymi za pomocą systemctl."""
    if not lista_uslug:
        log_callback("Nie wybrano żadnych usług do zarządzania.")
        return True
        
    log_callback("⚙️ Rozpoczynam zarządzanie usługami...")
    for usluga in lista_uslug:
        log_callback(f"➡️ Włączam i uruchamiam usługę: {usluga}")
        komenda_enable = ["systemctl", "enable", "--now", usluga]
        if not wykonaj_polecenie(komenda_enable, log_callback):
            log_callback(f"❌ Nie udało się włączyć usługi {usluga}.")
            # Można zdecydować, czy kontynuować w razie błędu jednej usługi

    log_callback("✅ Zarządzanie usługami zakończone pomyślnie!")
    return True

def run_installation_process(programs_to_install, services_to_manage, log_callback, package_manager):
    """Główna funkcja uruchamiająca cały proces."""
    if not sprawdz_uprawnienia(log_callback):
        return

    if instaluj_programy(programs_to_install, log_callback, package_manager):
        if zarzadzaj_uslugami(services_to_manage, log_callback):
            log_callback("\n🎉 Skrypt zakończony pomyślnie! 🎉")
        else:
            log_callback("\n❌ Wystąpił błąd podczas zarządzania usługami.")
    else:
        log_callback("\n❌ Wystąpił błąd podczas instalacji programów.")
