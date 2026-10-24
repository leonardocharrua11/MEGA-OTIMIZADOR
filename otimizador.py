#!/usr/bin/env python3
"""
OTIMIZADOR PREMIUM - Windows System Optimizer
by: Leonardo
"""

import os
import sys
import shutil
import subprocess
import tempfile
import ctypes
import platform
import time
from pathlib import Path

# ============================================================
#  DEPENDENCIES (auto-install)
# ============================================================
try:
    from colorama import init, Fore, Style
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "colorama"])
    from colorama import init, Fore, Style

init(autoreset=True)

CYAN = Fore.CYAN + Style.BRIGHT
BLUE = Fore.BLUE + Style.BRIGHT
WHITE = Fore.WHITE + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
GREY = Fore.LIGHTBLACK_EX
RESET = Style.RESET_ALL

IS_WINDOWS = platform.system() == "Windows"


# ============================================================
#  UI HELPERS
# ============================================================
def clear():
    os.system("cls" if IS_WINDOWS else "clear")


def banner():
    art = r"""
   ██████╗ ████████╗██╗███╗   ███╗██╗███████╗ █████╗ ██████╗  ██████╗ ██████╗
  ██╔═══██╗╚══██╔══╝██║████╗ ████║██║╚══███╔╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
  ██║   ██║   ██║   ██║██╔████╔██║██║  ███╔╝ ███████║██║  ██║██║   ██║██████╔╝
  ██║   ██║   ██║   ██║██║╚██╔╝██║██║ ███╔╝  ██╔══██║██║  ██║██║   ██║██╔══██╗
  ╚██████╔╝   ██║   ██║██║ ╚═╝ ██║██║███████╗██║  ██║██████╔╝╚██████╔╝██║  ██║
   ╚═════╝    ╚═╝   ╚═╝╚═╝     ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
"""
    print(CYAN + art)
    print(BLUE + "═" * 78)
    print(WHITE + "P R E M I U M   S Y S T E M   O P T I M I Z E R".center(78))
    print(GREY + f"Sistema: {platform.system()} {platform.release()}".center(78))
    print(BLUE + "═" * 78 + RESET)
    print()


def footer():
    print()
    print(GREY + "─" * 60)
    print(CYAN + "by: Leonardo".rjust(58))
    print(GREY + "─" * 60 + RESET)


def is_admin():
    if not IS_WINDOWS:
        return os.geteuid() == 0
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def pause():
    input(GREY + "\n  Pressiona ENTER para continuar..." + RESET)


def get_size(path):
    total = 0
    try:
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
    except Exception:
        pass
    return total


def human_size(num):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num) < 1024:
            return f"{num:.2f} {unit}"
        num /= 1024
    return f"{num:.2f} PB"


def spinner_step(label):
    print(CYAN + f"  [>] {label}..." + RESET)


# ============================================================
#  CORE OPTIMIZATIONS
# ============================================================
def clean_temp_files():
    print(CYAN + "\n  ╔═══ LIMPEZA DE FICHEIROS TEMPORARIOS ═══╗\n" + RESET)
    targets = []
    if IS_WINDOWS:
        targets = [
            os.environ.get("TEMP", tempfile.gettempdir()),
            os.environ.get("TMP", tempfile.gettempdir()),
            r"C:\Windows\Temp",
            os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
        ]
    else:
        targets = [tempfile.gettempdir()]

    targets = list(dict.fromkeys([t for t in targets if t and os.path.isdir(t)]))

    total_freed = 0
    total_files = 0

    for folder in targets:
        spinner_step(f"A analisar {folder}")
        before = get_size(folder)
        freed_here = 0
        files_here = 0
        try:
            for entry in os.scandir(folder):
                try:
                    if entry.is_file() or entry.is_symlink():
                        size = entry.stat(follow_symlinks=False).st_size
                        os.remove(entry.path)
                        freed_here += size
                        files_here += 1
                    elif entry.is_dir():
                        size = get_size(entry.path)
                        shutil.rmtree(entry.path, ignore_errors=True)
                        freed_here += size
                        files_here += 1
                except Exception:
                    continue
        except Exception:
            continue

        total_freed += freed_here
        total_files += files_here
        print(GREEN + f"      -> {human_size(freed_here)} libertados ({files_here} itens)" + RESET)

    print()
    print(WHITE + f"  TOTAL LIBERTADO: " + GREEN + human_size(total_freed) + RESET)
    print(WHITE + f"  ITENS REMOVIDOS: " + GREEN + str(total_files) + RESET)


def flush_dns():
    print(CYAN + "\n  ╔═══ LIMPAR CACHE DNS ═══╗\n" + RESET)
    if IS_WINDOWS:
        spinner_step("A limpar cache DNS (ipconfig /flushdns)")
        subprocess.run(["ipconfig", "/flushdns"], shell=True)
        spinner_step("A renovar configuracao Winsock")
        subprocess.run(["netsh", "winsock", "reset"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(GREEN + "  [OK] Cache DNS limpa com sucesso." + RESET)
    else:
        print(YELLOW + "  [!] Funcao disponivel apenas em Windows." + RESET)


def empty_recycle_bin():
    print(CYAN + "\n  ╔═══ ESVAZIAR RECICLAGEM ═══╗\n" + RESET)
    if IS_WINDOWS:
        try:
            spinner_step("A esvaziar a Reciclagem")
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000001 | 0x00000002)
            print(GREEN + "  [OK] Reciclagem esvaziada." + RESET)
        except Exception as e:
            print(RED + f"  [X] Erro: {e}" + RESET)
    else:
        print(YELLOW + "  [!] Funcao disponivel apenas em Windows." + RESET)


def clean_browser_cache():
    print(CYAN + "\n  ╔═══ LIMPEZA DE CACHE DE BROWSERS ═══╗\n" + RESET)
    local = os.environ.get("LOCALAPPDATA", "")
    paths = {
        "Chrome": os.path.join(local, r"Google\Chrome\User Data\Default\Cache"),
        "Edge": os.path.join(local, r"Microsoft\Edge\User Data\Default\Cache"),
        "Firefox (profiles)": os.path.join(local, r"Mozilla\Firefox\Profiles"),
    }
    total = 0
    for name, path in paths.items():
        if os.path.isdir(path):
            spinner_step(f"A limpar cache do {name}")
            size = get_size(path)
            shutil.rmtree(path, ignore_errors=True)
            os.makedirs(path, exist_ok=True)
            total += size
            print(GREEN + f"      -> {human_size(size)} libertados" + RESET)
        else:
            print(GREY + f"      {name}: nao encontrado" + RESET)
    print()
    print(WHITE + f"  TOTAL LIBERTADO: " + GREEN + human_size(total) + RESET)


def optimize_services():
    print(CYAN + "\n  ╔═══ OTIMIZAR SERVICOS EM SEGUNDO PLANO ═══╗\n" + RESET)
    if not IS_WINDOWS:
        print(YELLOW + "  [!] Funcao disponivel apenas em Windows." + RESET)
        return
    if not is_admin():
        print(YELLOW + "  [!] Recomenda-se correr como Administrador para efeito total." + RESET)

    # Serviços seguros de parar temporariamente (não desativa permanentemente)
    services = ["SysMain", "DiagTrack", "WSearch"]
    for svc in services:
        spinner_step(f"A verificar servico {svc}")
        result = subprocess.run(
            ["sc", "query", svc], shell=True, capture_output=True, text=True
        )
        if "RUNNING" in result.stdout:
            print(GREY + f"      {svc} esta ativo (deixado como esta, usa [6] para parar manualmente)" + RESET)
        else:
            print(GREY + f"      {svc} ja nao esta em execucao" + RESET)
    print()
    print(GREEN + "  [OK] Verificacao concluida. Usa a opcao [6] para parar servicos especificos." + RESET)


def stop_service_menu():
    print(CYAN + "\n  ╔═══ PARAR SERVICO ESPECIFICO ═══╗\n" + RESET)
    if not IS_WINDOWS:
        print(YELLOW + "  [!] Funcao disponivel apenas em Windows." + RESET)
        return
    print(WHITE + "  Servicos conhecidos por consumir recursos:")
    print(GREY + "   1) SysMain (Superfetch)")
    print(GREY + "   2) DiagTrack (Telemetria)")
    print(GREY + "   3) WSearch (Indexacao de pesquisa)")
    print(GREY + "   0) Cancelar")
    choice = input(CYAN + "\n  > Escolha: " + RESET).strip()
    mapping = {"1": "SysMain", "2": "DiagTrack", "3": "WSearch"}
    svc = mapping.get(choice)
    if not svc:
        print(YELLOW + "  Cancelado." + RESET)
        return
    spinner_step(f"A parar servico {svc}")
    subprocess.run(["net", "stop", svc], shell=True)
    print(GREEN + f"  [OK] Comando enviado para parar {svc}." + RESET)


def show_startup_programs():
    print(CYAN + "\n  ╔═══ PROGRAMAS DE ARRANQUE ═══╗\n" + RESET)
    if not IS_WINDOWS:
        print(YELLOW + "  [!] Funcao disponivel apenas em Windows." + RESET)
        return
    spinner_step("A ler registo de arranque")
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        for hive, hive_name in [(winreg.HKEY_CURRENT_USER, "HKCU"), (winreg.HKEY_LOCAL_MACHINE, "HKLM")]:
            try:
                key = winreg.OpenKey(hive, key_path)
                i = 0
                print(WHITE + f"\n  [{hive_name}]" + RESET)
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        print(GREY + f"   - {name}: {value}" + RESET)
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except FileNotFoundError:
                continue
    except Exception as e:
        print(RED + f"  [X] Erro ao ler: {e}" + RESET)


def ram_info():
    print(CYAN + "\n  ╔═══ INFORMACAO DE MEMORIA (RAM) ═══╗\n" + RESET)
    try:
        import psutil
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "psutil"])
        import psutil

    vm = psutil.virtual_memory()
    print(WHITE + f"  Total:      " + CYAN + human_size(vm.total))
    print(WHITE + f"  Usada:      " + YELLOW + human_size(vm.used) + f"  ({vm.percent}%)")
    print(WHITE + f"  Disponivel: " + GREEN + human_size(vm.available))

    bar_len = 40
    filled = int(bar_len * vm.percent / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    color = GREEN if vm.percent < 60 else (YELLOW if vm.percent < 85 else RED)
    print("\n  [" + color + bar + RESET + "] " + f"{vm.percent}%")

    if IS_WINDOWS:
        print()
        confirm = input(CYAN + "  Tentar libertar memoria em cache agora? (s/n): " + RESET).strip().lower()
        if confirm == "s":
            spinner_step("A libertar working sets dos processos")
            try:
                ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
                print(GREEN + "  [OK] Comando de otimizacao de memoria enviado." + RESET)
            except Exception as e:
                print(RED + f"  [X] Erro: {e}" + RESET)


def disk_report():
    print(CYAN + "\n  ╔═══ RELATORIO DE DISCO ═══╗\n" + RESET)
    try:
        import psutil
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "psutil"])
        import psutil

    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        pct = usage.percent
        color = GREEN if pct < 70 else (YELLOW if pct < 90 else RED)
        bar_len = 30
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(WHITE + f"  {part.device:10s}" + RESET)
        print("   [" + color + bar + RESET + f"] {pct}%  " +
              GREY + f"({human_size(usage.used)} / {human_size(usage.total)})" + RESET)
        print()


def cpu_info():
    print(CYAN + "\n  ╔═══ INFORMACAO DE CPU ═══╗\n" + RESET)
    try:
        import psutil
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "psutil"])
        import psutil

    print(WHITE + f"  Nucleos fisicos:  " + CYAN + str(psutil.cpu_count(logical=False)))
    print(WHITE + f"  Nucleos logicos:  " + CYAN + str(psutil.cpu_count(logical=True)))
    spinner_step("A medir utilizacao (3 segundos)")
    pct = psutil.cpu_percent(interval=3)
    color = GREEN if pct < 50 else (YELLOW if pct < 85 else RED)
    bar_len = 40
    filled = int(bar_len * pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    print("\n  [" + color + bar + RESET + "] " + f"{pct}%")


def top_processes():
    print(CYAN + "\n  ╔═══ TOP PROCESSOS (CPU) ═══╗\n" + RESET)
    try:
        import psutil
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "psutil"])
        import psutil

    spinner_step("A recolher dados de processos")
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
        try:
            procs.append(p.info)
        except Exception:
            continue

    time.sleep(1)
    for p in procs:
        try:
            p["cpu_percent"] = psutil.Process(p["pid"]).cpu_percent(interval=0)
        except Exception:
            pass

    procs = sorted(procs, key=lambda x: x.get("cpu_percent") or 0, reverse=True)[:10]
    print(WHITE + f"\n  {'PID':<8}{'PROCESSO':<30}{'CPU%':<8}{'RAM'}" + RESET)
    print(GREY + "  " + "-" * 56 + RESET)
    for p in procs:
        mem = human_size(p["memory_info"].rss) if p.get("memory_info") else "-"
        print(f"  {str(p['pid']):<8}{str(p['name'])[:28]:<30}{str(p.get('cpu_percent', 0)):<8}{mem}")


def full_optimization():
    print(CYAN + "\n  ╔═══ OTIMIZACAO COMPLETA (ALL-IN-ONE) ═══╗\n" + RESET)
    steps = [
        ("Limpeza de ficheiros temporarios", clean_temp_files),
        ("Limpeza de cache de browsers", clean_browser_cache),
        ("Esvaziar reciclagem", empty_recycle_bin),
        ("Limpar cache DNS", flush_dns),
    ]
    for label, func in steps:
        print(BLUE + f"\n  >>> {label}" + RESET)
        try:
            func()
        except Exception as e:
            print(RED + f"  [X] Erro em '{label}': {e}" + RESET)
    print(GREEN + "\n  [OK] OTIMIZACAO COMPLETA CONCLUIDA." + RESET)


# ============================================================
#  MENU
# ============================================================
MENU_ITEMS = [
    ("1", "Limpar ficheiros temporarios", clean_temp_files),
    ("2", "Limpar cache DNS + Winsock", flush_dns),
    ("3", "Esvaziar Reciclagem", empty_recycle_bin),
    ("4", "Limpar cache de Browsers (Chrome/Edge/Firefox)", clean_browser_cache),
    ("5", "Verificar servicos em segundo plano", optimize_services),
    ("6", "Parar servico especifico", stop_service_menu),
    ("7", "Ver programas de arranque", show_startup_programs),
    ("8", "Informacao + limpeza de RAM", ram_info),
    ("9", "Relatorio de espaco em disco", disk_report),
    ("10", "Informacao de CPU (uso em tempo real)", cpu_info),
    ("11", "Top 10 processos a consumir CPU", top_processes),
    ("12", "OTIMIZACAO COMPLETA (executa tudo)", full_optimization),
]


def print_menu():
    print(WHITE + "  Escolha uma opcao:\n" + RESET)
    for key, label, _ in MENU_ITEMS:
        print(f"   {CYAN}[{key}]{RESET}  {label}")
    print(f"   {RED}[0]{RESET}  Sair")
    print()


def main():
    while True:
        clear()
        banner()
        admin_tag = (GREEN + "ADMIN" + RESET) if is_admin() else (YELLOW + "SEM PRIVILEGIOS ADMIN" + RESET)
        print(f"  Estado: {admin_tag}\n")
        print_menu()
        choice = input(CYAN + "  > Escolha: " + RESET).strip()

        if choice == "0":
            clear()
            banner()
            print(GREEN + "  Obrigado por usares o Otimizador Premium!" + RESET)
            footer()
            break

        match = next((item for item in MENU_ITEMS if item[0] == choice), None)
        if match:
            clear()
            banner()
            try:
                match[2]()
            except Exception as e:
                print(RED + f"\n  [X] Erro inesperado: {e}" + RESET)
            footer()
            pause()
        else:
            print(RED + "\n  Opcao invalida." + RESET)
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(RED + "\n\n  Encerrado pelo utilizador." + RESET)
        sys.exit(0)