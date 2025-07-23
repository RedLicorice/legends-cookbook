import os
from dynaconf import Dynaconf

config_path = os.getenv('CONFIG_PATH', '.')
settings = Dynaconf(settings_files=[
    f'{config_path}/legends-cookbook.toml', 
    f'{config_path}/legends-cookbook.secrets.toml'
])
