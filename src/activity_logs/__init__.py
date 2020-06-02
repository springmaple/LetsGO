import os
from datetime import datetime

from constants import ACTIVITY_LOGS_DIR


class ActivityLog:
    def __init__(self):
        # Delete older log entries
        entries_to_keep = 10
        file_names = filter(lambda file: os.path.isfile(os.path.join(ACTIVITY_LOGS_DIR, file)),
                            os.listdir(ACTIVITY_LOGS_DIR))
        for file_name in list(file_names)[::-1][entries_to_keep:]:
            log_file = os.path.join(ACTIVITY_LOGS_DIR, file_name)
            try:
                os.unlink(log_file)
            except:
                pass

    def __enter__(self):
        log_name = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = os.path.join(ACTIVITY_LOGS_DIR, log_name + '.txt')
        self._fs = open(log_path, mode='w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fs.flush()
        self._fs.close()

    def i(self, *args):
        dt = datetime.now().strftime('%H%M%S')
        print(f'[{dt}] ', *args, file=self._fs, flush=True)


class ActivityLogMock:
    def i(self, *args):
        pass
