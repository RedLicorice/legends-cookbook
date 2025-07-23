from pathlib import Path
import shutil
import os
import subprocess
import random
import string

HERE = Path(__file__).parent.absolute()
module_name = HERE.name
exe_name = module_name.replace('_', '-') + '.pyz'
dist_dir = f"shiv-dist-{module_name}"
requirements_path = Path(f"{HERE.parent.absolute()}/requirements.txt")
dist_path = Path(f"{HERE.parent.absolute()}/{dist_dir}")
main_func = f"{module_name}.runner:main"

def build():
    """
    Build the project by exporting requirements, installing dependencies,
    copying source files, and creating a shiv package.
    """
    def export_requirements(filename):
        """
        Export the project dependencies to a requirements.txt file.

        Args:
            filename (str): The name of the file to export the requirements to.
        """
        result = subprocess.run(
            ["poetry", "export", "-f", "requirements.txt", "-o", filename],
            check=True
        )

    def install_dependencies(filename, to_dir):
        """
        Install the project dependencies to the specified directory.

        Args:
            filename (str): The name of the requirements file.
            to_dir (str): The directory to install the dependencies to.
        """
        custom_env = os.environ.copy()
        custom_env['CFLAGS']=''
        custom_env['CPPFLAGS']=''
        custom_env['CXXFLAGS']=''
        result = subprocess.run(
            ["pip", "install", "-r", filename, "--target", to_dir],
            check=True,
            env=custom_env
        )

    def copy_source(to_path: Path):
        """
        Copy the source files to the specified directory.

        Args:
            to_path (Path): The destination directory.
        """
        dst_path = to_path / module_name
        if dst_path.exists() and dst_path.is_dir():
            shutil.rmtree(dst_path)
        shutil.copytree(module_name, dst_path)
    
    def get_git_revision_short_hash() -> str:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

    def randstr(N):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

    def create_shiv_package():
        """
        Create a shiv package from the installed dependencies and source files.
        """
        print(f"Bundling into {exe_name} with shiv")
        result = subprocess.run([
            "poetry", "run", "python", "-m", "shiv",
            "--root", "/tmp",
            "--compile-pyc",
            "--build-id", f"shiv_{module_name}_{get_git_revision_short_hash()}_{randstr(4)}",
            "--site-packages", dist_dir,
            "--compressed",
            "-p", "/usr/bin/env python3",
            "-o", exe_name,
            "-e", main_func
        ], check=True)

    if not requirements_path.exists():
        export_requirements("requirements.txt")
    if not dist_path.exists():
        install_dependencies("requirements.txt", dist_dir)
    copy_source(dist_path)
    create_shiv_package()

def install():
    """
    Install the shiv package and configuration files to the appropriate locations.
    """
    inst_path = Path(f"{HERE.parent.parent.absolute()}/bin")
    exe_path = Path(f"{HERE.parent}/{exe_name}")
    config_path = Path(f"{HERE.parent}/config/")
    config_dest_path = Path(f"{HERE.parent.parent.absolute()}/bin/config")

    # Verifica se il file eseguibile esiste
    if exe_path.exists() and exe_path.is_file():
        # Crea la directory di destinazione se non esiste
        inst_path.mkdir(parents=True, exist_ok=True)
        
        # Copia il file eseguibile nella directory di destinazione
        shutil.copy(exe_path, inst_path)
        print(f"Copied {exe_name} to {inst_path}")

        # Imposta i permessi di esecuzione sul file copiato
        dest_file = Path(f"{inst_path}/{exe_name}")
        dest_file.chmod(dest_file.stat().st_mode | 0o111)
        print(f"Permission +x set on {dest_file}")

        # Crea la directory di destinazione per i file di configurazione se non esiste
        config_dest_path.mkdir(parents=True, exist_ok=True)

        # Copia tutti i file presenti in config_path in config_dest_path, rimuovendo il suffisso .template
        for config_file in config_path.iterdir():
            if config_file.is_file():
                dest_file_path = config_dest_path / config_file.name.replace('.template', '')
                shutil.copy(config_file, dest_file_path)
                print(f"Copied configuration file {config_file.name} to {dest_file_path}")
    else:
        print(f"File {exe_name} does not exist in {exe_path.parent.absolute()}! Please run build command first.")

def clean():
    """
    Clean up the generated files and directories.
    """
    # requirements_path = Path(f"{HERE.parent.absolute()}/requirements.txt")
    exe_path = Path(f"{HERE.parent.absolute()}/{exe_name}")
    # dist_path = Path(f"{HERE.parent.absolute()}/{dist_dir}")

    # Rimuovi il file requirements_path se esiste
    if requirements_path.exists():
        requirements_path.unlink()
        print(f"File {requirements_path} removed.")

    # Rimuovi il file exe_path se esiste
    if exe_path.exists():
        exe_path.unlink()
        print(f"File {exe_path} removed.")

    # Rimuovi la cartella dist_path se esiste
    if dist_path.exists() and dist_path.is_dir():
        shutil.rmtree(dist_path)
        print(f"Directory {dist_path} removed.")