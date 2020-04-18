import enum
import os
import tempfile

APP_NAME = "Let'sGO"
APP_VERSION = 'v1.1.6'
TMP_DIR = os.path.join(os.path.abspath(tempfile.gettempdir()), 'LetsGO')

os.makedirs(TMP_DIR, exist_ok=True)


class SalesOrderStatus(enum.Enum):
    Open = 'open'
    Cancelled = 'cancelled'
    Transferred = 'transferred'
