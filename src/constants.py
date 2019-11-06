import os
import tempfile

APP_NAME = "Let'sGO"
TMP_DIR = os.path.join(os.path.abspath(tempfile.gettempdir()), 'LetsGO')

os.makedirs(TMP_DIR, exist_ok=True)
