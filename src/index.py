import os
import traceback
from threading import Thread
from tkinter import Tk
from tkinter.messagebox import showwarning

import util
from constants import APP_NAME
from firestore import get_firestore_instance, get_firebase_storage
from settings import Settings
from sql import Sql
from ui import AppMain, ViewModel, Profile
from ui.sync import SyncProgress, SyncService
from ui.sync.service import is_sql_running


def _center_window(top_level, w, h):
    # Get Windows screen width and height
    ws = top_level.winfo_screenwidth()
    hs = top_level.winfo_screenheight()

    # Calculate position x, y
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    top_level.geometry('+%d+%d' % (x, y))


def start_gui():
    settings = Settings()
    fs = get_firestore_instance()
    st = get_firebase_storage()

    def _on_sync(profile: Profile):
        try:
            if not is_sql_running():
                raise Exception('Please start SQL Account and login first.')

            top = SyncProgress(root)
            top.title('Sync')
            top.transient(root)
            top.grab_set()

            def _sync_service_in_bg():
                with Sql() as sql:
                    ss = SyncService(fs, profile, settings, sql)
                    try:
                        ss.check_login()
                        top.start_sync(ss)
                        app_main.refresh()
                    except Exception as _ex:
                        top.destroy()
                        showwarning(APP_NAME, _ex)

            Thread(target=_sync_service_in_bg).start()

            _center_window(top, 400, 300)
            root.wait_window(top)
        except Exception as ex:
            showwarning(APP_NAME, ex)

    vm = ViewModel(fs, st, settings)
    root = Tk()

    root.wm_iconbitmap(util.find_file(os.path.join('res', 'img', 'logo.ico')))
    app_main = AppMain(root, vm, _on_sync)
    root.resizable(False, False)
    _center_window(root, 800, 640)
    root.mainloop()


if __name__ == '__main__':
    try:
        start_gui()
        print('OK...')
    except:
        traceback.print_exc()
        print('ERROR...')
