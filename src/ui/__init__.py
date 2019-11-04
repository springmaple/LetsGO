from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from tkinter import Tk, Listbox, END, LEFT, Label, PhotoImage, StringVar, Button, Frame, TOP, OptionMenu, Scrollbar, \
    BOTTOM, Entry, RIGHT
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showwarning
from typing import Any

import util
from constants import APP_NAME
from ui.view_model import ViewModel, Item, Profile

_photo_executor = ThreadPoolExecutor(max_workers=1)


class AppMain:
    def __init__(self, master: Tk, vm: ViewModel):
        def _on_close():
            _photo_executor.shutdown()
            master.destroy()

        master.protocol("WM_DELETE_WINDOW", _on_close)
        master.title(APP_NAME)

        main_frame = Frame()

        def _on_profile_changed(profile: Profile):
            if vm.current_profile.company_code == profile.company_code:
                return
            vm.set_current_profile(profile)
            upload_photo_frame.refresh()

        main_top_frame = Frame(main_frame)

        company_frame = ProfileFrame(main_top_frame, vm, _on_profile_changed)
        company_frame.pack(side=LEFT, fill='x', pady=(0, 10))

        sync_frame = SyncFrame(main_top_frame, None)
        sync_frame.pack(side=RIGHT)

        main_top_frame.pack(side=TOP, fill='x', pady=(0, 10))

        upload_photo_frame = UploadPhotoFrame(main_frame, vm)
        upload_photo_frame.pack(side=TOP, fill='x')

        main_frame.pack(padx=20, pady=10)

        upload_photo_frame.refresh()


class ProfileFrame(Frame):
    def __init__(self, parent, vm: ViewModel, on_profile_changed, **kw):
        super().__init__(parent, **kw)

        label = Label(self, text='Company')
        label.pack(side=LEFT)

        companies = []
        value = ''
        for profile in vm.profiles:
            if not value:
                value = profile.company_name
            else:
                companies.append(profile.company_name)

        s = StringVar()
        s.set(value)

        def _on_changed(*_):
            company_name = s.get()
            for _profile in vm.profiles:
                if _profile.company_name == company_name:
                    on_profile_changed(_profile)
                    break

        s.trace('w', _on_changed)
        option = OptionMenu(self, s, value, *companies)
        option.pack(side=LEFT, fill='x')


class SyncFrame(Frame):
    def __init__(self, parent, on_click, **kw):
        super().__init__(parent, **kw)
        text = Label(self, text='Sync Now', fg='blue', cursor='hand2')
        text.bind("<Button-1>", lambda e: on_click())
        text.pack()


class UploadPhotoFrame(Frame):
    def __init__(self, parent, vm: ViewModel, **kw):
        super().__init__(parent, **kw)
        self._vm = vm

        item_list_frame = Frame(self)
        parent_photo_frame = Frame(self)
        photo_label_frame = Frame(parent_photo_frame)

        selected_item = None  # type: Any[Item]
        item_title, item_desc, set_item_title = self._setup_item_label(photo_label_frame)
        photo, set_photo = self._setup_photo(parent_photo_frame)

        def wrap(fn):
            def wrapper(*args, **kwargs):
                def run():
                    set_photo_button_active(False)
                    fn(*args, **kwargs)
                    set_photo_button_active(True)

                Thread(target=run).start()

            return wrapper

        @wrap
        def on_set_photo():
            if not selected_item:
                return

            filename = askopenfilename()
            if not filename:
                return

            set_listbox_active(False)
            try:
                self._vm.save_image(selected_item.code, filename)
                set_photo(vm.get_image(selected_item.code))
            except:
                showwarning(APP_NAME, 'Unsupported image format')
            finally:
                set_listbox_active(True)

        @wrap
        def on_item_selected(item):
            nonlocal selected_item
            selected_item = item

            def _on_item_selected(_item):
                if not _item:
                    set_item_title('', '')
                    set_photo(None)
                else:
                    set_item_title(_item.code, _item.desc)
                    set_photo(vm.get_image(_item.code))

            waiter = _photo_executor.submit(_on_item_selected, item)
            waiter.result()

        photo_button, set_photo_button_active = self._setup_set_photo_button(photo_label_frame, on_set_photo)
        item_list, refresh_item_list, set_listbox_active = self._setup_item_listbox(
            item_list_frame, on_item_selected)
        search_box, get_search_box_text = self._setup_item_search(
            item_list_frame, lambda s: refresh_item_list(s))

        set_photo_button_active(False)

        item_list.pack(side=BOTTOM, fill='y', expand=1)
        search_box.pack(side=BOTTOM, pady=(0, 10), fill='x')
        item_list_frame.pack(side=LEFT, fill='y', expand=1)

        photo_button.pack(side=LEFT, padx=(0, 10), pady=(0, 10))
        item_title.pack(side=LEFT, padx=(0, 10))
        item_desc.pack(side=LEFT, fill='x')
        photo_label_frame.pack(side=TOP, fill='x')

        photo.pack(side=TOP)
        parent_photo_frame.pack(side=LEFT, padx=(10, 0))

        def _refresh():
            search_box_text = get_search_box_text()
            refresh_item_list(search_box_text)

        self.refresh = _refresh

    def _setup_item_search(self, parent, on_change):
        s = StringVar()
        search = Entry(parent, textvariable=s)
        s.trace_variable('w', lambda *_: on_change(s.get()))
        return search, lambda: s.get()

    def _setup_item_listbox(self, parent, on_select):
        listbox_frame = Frame(parent)
        listbox = Listbox(listbox_frame, width=50)

        def _on_select(evt):
            w = evt.widget
            selections = w.curselection()
            if len(selections) > 0:
                index = int(selections[0])
                on_select(filtered_items[index])
            else:
                on_select(None)

        filtered_items = []

        def _refresh(_filter_text):
            nonlocal filtered_items
            filter_text = (_filter_text or '').lower()
            filtered_items = [item for item in self._vm.items
                              if (not filter_text) or filter_text in item.keywords]

            listbox.delete(0, END)
            for item in filtered_items:
                listbox.insert(END, f'[{item.code}] {item.desc}')
            if len(filtered_items) > 0:
                listbox.activate(0)
                listbox.select_set(0)
                on_select(filtered_items[0])
            else:
                on_select(None)

        def _set_active(is_active):
            listbox['state'] = 'normal' if is_active else 'disabled'

        scrollbar = Scrollbar(listbox_frame, orient="vertical")

        listbox.bind('<<ListboxSelect>>', _on_select)
        listbox.pack(side=LEFT, fill='y')
        scrollbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=LEFT, fill='y')
        return listbox_frame, _refresh, _set_active

    def _setup_item_label(self, parent):
        title_str = StringVar()
        title = Label(parent, textvariable=title_str)
        desc_str = StringVar()
        desc = Label(parent, textvariable=desc_str)

        def _update(new_title, new_desc):
            title_str.set(new_title)
            desc_str.set(new_desc)
            title.update()
            desc.update()

        return title, desc, _update

    def _setup_set_photo_button(self, parent, on_click):
        button = Button(parent, text='Set Photo', command=on_click)

        def _set_button_active(is_active):
            button['state'] = 'normal' if is_active else 'disabled'

        return button, _set_button_active

    def _setup_photo(self, parent):
        default_img = util.find_file('res/img/default_img.png')
        photo = PhotoImage(file=default_img)
        image = Label(parent, image=photo, width=480, height=480, borderwidth=2, relief='groove')
        image.image = photo

        def _set_photo(filename: str):
            nonlocal photo, image
            _photo = PhotoImage(file=filename) if filename else photo
            image.configure(image=_photo)
            image.image = _photo

        _set_photo('')
        return image, _set_photo
