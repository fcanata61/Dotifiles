import asyncio
from colorama import init, Fore, Style
from config import Config
from recipe import RecipeManager
from install import Installer
from remove import Remover
from download import Downloader
from extract import Extractor
from upgrade import UpgraderV3
from update import Updater
from sync import SyncManager
from patch import PatchApplier
from hooks import HooksManager
from uses import UseManager

# Inicializa colorama
init(autoreset=True)

# Funções de log colorido
def log_info(msg): print(Fore.GREEN + msg)
def log_warning(msg): print(Fore.YELLOW + msg)
def log_error(msg): print(Fore.RED + msg)
def log_title(msg): print(Fore.CYAN + Style.BRIGHT + msg)

# Inicializa módulos
installer = Installer()
remover = Remover()
downloader = Downloader(Config.BUILD_DIR, sandbox=None, hooks=HooksManager())
extractor = Extractor(sandbox=None, hooks=HooksManager())
upgrader = UpgraderV3()
updater = Updater()
sync_manager = SyncManager.from_config(Config.REPO_FILE)
patcher = PatchApplier(Config.BUILD_DIR)
hooks = HooksManager()
use_manager = UseManager()
recipe_manager = RecipeManager()

# Função para verificar status de pacote
def pacote_status(recipe_name):
    try:
        installed = recipe_manager.get_installed(recipe_name)
        return "INSTALADO", Fore.GREEN
    except Exception:
        return "NÃO INSTALADO", Fore.RED

# Listar pacotes com cores e status
def listar_receitas_dinamico():
    log_title("Receitas disponíveis:")
    for recipe in recipe_manager.list_recipes():
        status_text, color = pacote_status(recipe.name)
        print(Fore.MAGENTA + f" - {recipe.name} ({recipe.version}) [{color}{status_text}{Fore.MAGENTA}]")

# Instalar pacote com fluxo completo
def instalar_pacote():
    pkg = input("Digite o nome do pacote para instalar: ")
    log_info(f"Instalando {pkg}...")
    installer.install(pkg)
    log_info(f"Baixando {pkg}...")
    downloader.download(pkg)
    log_info(f"Extraindo {pkg}...")
    extractor.extract_all_parallel(pkg)
    log_info(f"Aplicando patches em {pkg}...")
    asyncio.run(patcher.apply_recipe_patches(pkg, ["./build_dir"]))
    log_info(f"Executando hooks para {pkg}...")
    asyncio.run(hooks.run_all_hooks(pkg))
    flags = asyncio.run(use_manager.get_flags(pkg))
    log_info(f"Flags USE para {pkg}: {flags}")
    log_info(f"Pacote {pkg} instalado com sucesso!")

def remover_pacote():
    pkg = input("Digite o nome do pacote para remover: ")
    remover.remove(pkg)
    log_info(f"Pacote {pkg} removido com sucesso!")

def sincronizar_repos():
    log_info("Sincronizando repositórios...")
    asyncio.run(sync_manager.sync_all())
    log_info("Sincronização concluída!")

def atualizar_sistema():
    log_info("Atualizando sistema...")
    updater.update(world=True)
    log_info("Atualização concluída!")

def fazer_upgrade():
    log_info("Fazendo upgrade do sistema...")
    asyncio.run(upgrader.upgrade_packages())
    log_info("Upgrade concluído!")

def aplicar_hooks():
    pkg = input("Digite o nome do pacote para rodar hooks: ")
    asyncio.run(hooks.run_all_hooks(pkg))
    log_info(f"Hooks de {pkg} executados!")

def mostrar_flags():
    pkg = input("Digite o nome do pacote para mostrar flags USE: ")
    flags = asyncio.run(use_manager.get_flags(pkg))
    log_info(f"Flags USE para {pkg}: {flags}")

def gerenciar_flags():
    pkg = input("Digite o nome do pacote para gerenciar flags USE: ")
    flags = asyncio.run(use_manager.get_flags(pkg))
    log_info(f"Flags atuais de {pkg}: {flags}")
    print("Digite a flag para ativar/desativar (ou 'sair' para voltar):")
    while True:
        f = input("Flag: ").strip()
        if f.lower() == "sair":
            break
        if f in flags:
            asyncio.run(use_manager.disable_flag(pkg, f))
            log_info(f"Flag {f} desativada.")
        else:
            asyncio.run(use_manager.enable_flag(pkg, f))
            log_info(f"Flag {f} ativada.")
        flags = asyncio.run(use_manager.get_flags(pkg))
        log_info(f"Flags atuais: {flags}")

# Menu principal dinâmico
def main_menu():
    while True:
        log_title("\n=== Merge Program Manager (Avançado) ===")
        listar_receitas_dinamico()
        print(Fore.CYAN + "\nOperações:")
        print(Fore.CYAN + "1) Instalar pacote")
        print(Fore.CYAN + "2) Remover pacote")
        print(Fore.CYAN + "3) Sincronizar repositórios")
        print(Fore.CYAN + "4) Atualizar sistema")
        print(Fore.CYAN + "5) Upgrade do sistema")
        print(Fore.CYAN + "6) Aplicar hooks em pacote")
        print(Fore.CYAN + "7) Mostrar flags USE")
        print(Fore.CYAN + "8) Gerenciar flags USE")
        print(Fore.CYAN + "0) Sair")

        escolha = input(Fore.YELLOW + "Escolha uma opção: ")
        if escolha == "1":
            instalar_pacote()
        elif escolha == "2":
            remover_pacote()
        elif escolha == "3":
            sincronizar_repos()
        elif escolha == "4":
            atualizar_sistema()
        elif escolha == "5":
            fazer_upgrade()
        elif escolha == "6":
            aplicar_hooks()
        elif escolha == "7":
            mostrar_flags()
        elif escolha == "8":
            gerenciar_flags()
        elif escolha == "0":
            log_info("Saindo do gerenciador...")
            break
        else:
            log_warning("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main_menu()
