import win32com.client

from sql import util
from sql.entity.customer import Customer
from sql.entity.customer_branch import CustomerBranch
from sql.entity.stock_item import StockItem
from sql.entity.stock_item_group import StockItemGroup
from sql.entity.stock_item_uom import StockItemUom


class Sql:
    def __init__(self,
                 acc_id='ADMIN',
                 acc_password='ADMIN',
                 acc_dcf=r'C:\eStream\SQLAccounting\Share\Default.DCF',
                 acc_fdb='ACC-0001.FDB'):
        self._com = win32com.client.Dispatch("SQLAcc.BizApp")

        # Use this for util.print_members
        # self._com = win32com.client.gencache.EnsureDispatch("SQLAcc.BizApp")

        self._credential = (acc_id, acc_password, acc_dcf, acc_fdb)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._com

    def login(self):
        if self._com.IsLogin:
            self._com.Logout()
        self._com.Login(*self._credential)

    def get_stock_groups(self):
        data_set = self._com.DBManager.NewDataSet('SELECT * FROM ST_GROUP')
        for data in util.loop_data_sets(data_set):
            yield StockItemGroup(data)

    def get_stock_items(self):
        data_set = self._com.DBManager.NewDataSet("SELECT * FROM ST_ITEM")
        for data in util.loop_data_sets(data_set):
            yield StockItem(data)

    def get_stock_item_uom(self):
        data_set = self._com.DBManager.NewDataSet("SELECT * FROM ST_ITEM_UOM")
        for data in util.loop_data_sets(data_set):
            yield StockItemUom(data)

    def get_customers(self):
        data_set = self._com.DBManager.NewDataSet("SELECT * FROM AR_CUSTOMER")
        for data in util.loop_data_sets(data_set):
            yield Customer(data)

    def get_customer_branch(self):
        data_set = self._com.DBManager.NewDataSet("SELECT * FROM AR_CUSTOMERBRANCH")
        for data in util.loop_data_sets(data_set):
            yield CustomerBranch(data)
