from tkinter import Tk

from firestore import get_firestore_instance, get_firebase_storage
from settings import Settings
from ui import AppMain, ViewModel


def start():
    settings = Settings()
    fs = get_firestore_instance()
    st = get_firebase_storage()
    company_code = settings.list_company_codes()[0]

    vm = ViewModel(fs, st, settings)
    vm.set_company_code(company_code)
    root = Tk()
    AppMain(root, vm)
    root.mainloop()


start()
