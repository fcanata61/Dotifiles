import re
import requests
import asyncio
from urllib.parse import urlparse
from recipe import RecipeManager
from logs import stage, info, success, warn, error

class AutoUpdater:
    def __init__(self, recipe_manager: RecipeManager):
        self.recipe_manager = recipe_manager

    def get_latest_version_tarball(self, url: str):
        """
        Verifica a última versão disponível em um diretório HTTP.
        Exemplo: https://ftp.mozilla.org/pub/firefox/releases/
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            # Busca padrões de versão no HTML
            versions = re.findall(r'(\d+\.\d+(\.\d+)*)', response.text)
            versions = sorted(set(versions), key=lambda v: list(map(int, v.split('.'))))
            if versions:
                return versions[-1]
            return None
        except Exception as e:
            warn(f"Não foi possível verificar versão em {url}: {e}")
            return None

    def get_latest_version_git(self, git_url: str):
        """
        Para repositórios Git, pega a tag mais recente.
        Exemplo: git+https://github.com/mozilla/gecko-dev.git@mozilla-release
        """
        try:
            # Remove prefixo git+
            url = git_url.replace("git+", "")
            # Usa a API do GitHub se for github
            if "github.com" in url:
                repo_path = urlparse(url).path.strip("/")
                api_url = f"https://api.github.com/repos/{repo_path}/tags"
                r = requests.get(api_url)
                r.raise_for_status()
                tags = [t["name"] for t in r.json()]
                # Ordena versões numéricas simples
                tags = sorted(tags, key=lambda v: [int(x) for x in re.findall(r'\d+', v)])
                if tags:
                    return tags[-1]
            # Para outros Git, retorna None
            return None
        except Exception as e:
            warn(f"Não foi possível verificar Git {git_url}: {e}")
            return None

    def check_updates(self):
        """
        Verifica todas as receitas e compara com a versão instalada/local.
        """
        stage("Verificando novas versões dos pacotes do repositório oficial...")
        for recipe in self.recipe_manager.list_recipes():
            latest_version = None
            for src in recipe.src_uri:
                if src.startswith("git+"):
                    latest_version = self.get_latest_version_git(src)
                else:
                    # Assume tarball
                    url_base = "/".join(src.split("/")[:-1]) + "/"
                    latest_version = self.get_latest_version_tarball(url_base)
                if latest_version:
                    break  # Para no primeiro que encontrar
            if latest_version and latest_version != recipe.version:
                info(f"Nova versão disponível: {recipe.name} {latest_version} (instalada: {recipe.version})")
            else:
                info(f"{recipe.name} está atualizado ({recipe.version})")

# --------------------
# Exemplo de uso
# --------------------
if __name__ == "__main__":
    recipe_manager = RecipeManager()
    updater = AutoUpdater(recipe_manager)
    updater.check_updates()
