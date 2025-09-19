import asyncio
from colorama import init, Fore, Style

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
from config import Config
from recipe import RecipeManager

# Inicializa colorama
init(autoreset=True)

# Funções auxiliares para cores
def log_info(msg):
    print(Fore.GREEN + msg)

def log_warning(msg):
    print(Fore.YELLOW + msg)

def log_error(msg):
    print(Fore.RED + msg)

def log_title(msg):
    print(Fore.CYAN + Style.BRIGHT + msg)

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

# Menu de operações (exemplo)
def main():
    log_title("=== Merge Program Manager ===")

    # Exemplo de sincronização
    log_info("Sincronizando repositórios...")
    asyncio.run(sync_manager.sync_all())

    # Listar receitas disponíveis
    log_info("Receitas disponíveis:")
    for recipe in recipe_manager.list_recipes():
        print(Fore.MAGENTA + f" - {recipe.name} ({recipe.version})")

    # Instalar uma receita de exemplo
    pkg = "mypackage"
    log_info(f"Instalando {pkg}...")
    installer.install(pkg)

    # Download e extração
    log_info(f"Baixando {pkg}...")
    downloader.download(pkg)
    log_info(f"Extraindo {pkg}...")
    extractor.extract_all_parallel(pkg)

    # Aplicar patches
    log_info(f"Aplicando patches em {pkg}...")
    asyncio.run(patcher.apply_recipe_patches(pkg, ["./build_dir"]))

    # Rodar hooks
    log_info(f"Executando hooks para {pkg}...")
    asyncio.run(hooks.run_all_hooks(pkg))

    # Mostrar flags USE
    log_info(f"Flags USE para {pkg}:")
    flags = asyncio.run(use_manager.get_flags(pkg))
    print(Fore.BLUE + str(flags))

    # Atualizar e fazer upgrade do sistema
    log_info("Atualizando sistema...")
    updater.update(world=True)
    log_info("Upgrade do sistema...")
    asyncio.run(upgrader.upgrade_packages())

    log_info("Operações concluídas!")

if __name__ == "__main__":
    main()
