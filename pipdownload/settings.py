import os

from appdirs import user_data_dir

SETTINGS_FILE = os.path.join(user_data_dir("pipdownload", ""), "settings.json")
