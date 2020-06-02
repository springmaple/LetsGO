import enum
import os
import tempfile

APP_NAME = "Let'sGO"
APP_VERSION = 'v1.1.7'
TMP_DIR = os.path.join(os.path.abspath(tempfile.gettempdir()), 'LetsGO')

ACTIVITY_LOGS_DIR = os.path.join(TMP_DIR, 'logs')

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(ACTIVITY_LOGS_DIR, exist_ok=True)


class SalesOrderStatus(enum.Enum):
    Open = 'open'
    Cancelled = 'cancelled'
    Transferred = 'transferred'
