from tkinter import Toplevel, Checkbutton, TOP, Frame, LEFT, HORIZONTAL, StringVar, Label, DISABLED
from tkinter.messagebox import showinfo
from tkinter.ttk import Progressbar

from constants import APP_NAME
from ui.sync.service import SyncService


class _SyncCheckbox:
    def __init__(self, text_var, var):
        self._text_var = text_var
        self._var = var

    def set_checked(self):
        self._var.set('done')

    def set_text(self, text):
        self._text_var.set(text)


class SyncProgress(Toplevel):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW",
                      lambda: showinfo(APP_NAME, 'Synchronizing cloud data with SQL Account.'))

        main_frame = Frame(self)

        self._progress = progress = Progressbar(
            main_frame, orient=HORIZONTAL, mode='indeterminate', length=400)
        progress.start()
        progress.pack(side=TOP, fill='x')

        self._progress_text = StringVar()
        progress_label = Label(main_frame, textvariable=self._progress_text)
        progress_label.pack(side=TOP, fill='x', pady=(0, 10))

        check_box_frame = Frame(main_frame, width=50)

        def _add_checkbox(text):
            frame = Frame(check_box_frame)
            tv = StringVar()
            tv.set(text)
            v = StringVar()
            v.set('sync')
            checkbox = Checkbutton(frame, textvariable=tv, state=DISABLED, disabledforeground='black',
                                   variable=v, onvalue='done', offvalue='sync')
            checkbox.pack(side=LEFT)
            frame.pack(side=TOP, fill='x')
            return _SyncCheckbox(tv, v)

        self._cb_items = _add_checkbox('Stock Items')
        self._cb_item_groups = _add_checkbox('Stock Item Groups')
        self._cb_customers = _add_checkbox('Customers')
        self._cb_agents = _add_checkbox('Agents')
        self._cb_sales_orders = _add_checkbox('Sales Orders')
        self._cb_aging_report = _add_checkbox('Aging Report')
        self._cb_update_cache = _add_checkbox('Update Item Cache')

        check_box_frame.pack(side=TOP, fill='x')
        main_frame.pack(side=TOP, padx=20, pady=10)

    def start_sync(self, ss: SyncService):
        try:
            self._start_sync(ss)
            self._progress.stop()
            showinfo(APP_NAME, 'Sync Completed')
        finally:
            self.destroy()

    def _start_sync(self, ss: SyncService):
        self._progress_text.set('Preparing to upload stock items')
        self._cb_items.set_text('Stock Items (0)')
        for i, item in enumerate(ss.upload_stock_items(), start=1):
            self._progress_text.set(f'Uploading stock item: {item.code}')
            self._cb_items.set_text(f'Stock Items ({i})')
        self._cb_items.set_checked()

        self._progress_text.set('Preparing to upload stock item groups')
        self._cb_item_groups.set_text('Stock Item Groups (0)')
        for i, item_group in enumerate(ss.upload_item_groups(), start=1):
            self._progress_text.set(f'Uploading stock item group: {item_group.code}')
            self._cb_item_groups.set_text(f'Stock Item Groups ({i})')
        self._cb_item_groups.set_checked()

        self._progress_text.set('Preparing to upload customers')
        self._cb_customers.set_text('Customers (0)')
        for i, customer in enumerate(ss.upload_customers(), start=1):
            self._progress_text.set(f'Uploading customer: {customer.code}')
            self._cb_customers.set_text(f'Customers ({i})')
        self._cb_customers.set_checked()

        self._progress_text.set('Preparing to upload agents')
        self._cb_agents.set_text('Agents (0)')
        for i, agent in enumerate(ss.upload_agents(), start=1):
            self._progress_text.set(f'Uploading agent: {agent.code}')
            self._cb_agents.set_text(f'Agents ({i})')
        self._cb_agents.set_checked()

        self._progress_text.set('Preparing to download sales orders')
        self._cb_sales_orders.set_text('Sales Orders (0)')
        for i, sales_order in enumerate(ss.download_sales_orders(), start=1):
            self._progress_text.set(f'Downloading sales order: {sales_order["code"]}')
            self._cb_sales_orders.set_text(f'Sales Orders ({i})')
        self._cb_sales_orders.set_checked()

        self._progress_text.set('Preparing to upload aging report')
        self._cb_aging_report.set_text('Aging Report (0)')
        for i, aging_report in enumerate(ss.upload_aging_report(), start=1):
            self._progress_text.set(f'Uploading aging report: {aging_report.doc_code}')
            self._cb_aging_report.set_text(f'Aging Report ({i})')
        self._cb_aging_report.set_checked()

        self._progress_text.set('Preparing to update items')
        self._cb_update_cache.set_text('Update Item Cache (0)')
        for i, item in enumerate(ss.update_cache(), start=1):
            self._progress_text.set(f'Updating item: {item["code"]}')
            self._cb_update_cache.set_text(f'Update Item Cache ({i})')
        self._cb_update_cache.set_checked()
