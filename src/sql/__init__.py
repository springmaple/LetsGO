from datetime import datetime
from decimal import Decimal

import win32com.client

from sql import util
from sql.master.agent import Agent
from sql.master.customer import Customer
from sql.master.customer_branch import CustomerBranch
from sql.master.stock_item import StockItem
from sql.master.stock_item_group import StockItemGroup
from sql.master.stock_item_uom import StockItemUom


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

    def get_agents(self):
        data_set = self._com.DBManager.NewDataSet("SELECT * FROM AGENT")
        for data in util.loop_data_sets(data_set):
            yield Agent(data)

    def set_sales_order(self, so: dict):
        biz_object = self._com.BizObjects.Find("SL_SO")
        main_data = biz_object.DataSets.Find("MainDataSet")
        detail_data = biz_object.DataSets.Find("cdsDocDetail")

        today = datetime(2018, 2, 22, 13, 0)
        today.strftime('%m/%d/%Y')

        agent = so['agent']
        customer = so['customer']
        bill_to = so['bill_to']
        ship_to = so['ship_to']

        biz_object.New()
        main_data.FindField('DocKey').value = -1
        main_data.FindField('DocNo').AsString = so['code']
        main_data.FindField('DocDate').value = today
        main_data.FindField('PostDate').value = today
        main_data.FindField('Agent').AsString = agent['code']
        main_data.FindField('Description').AsString = "Sales Order"

        # Customer
        main_data.FindField('Code').AsString = customer['code']  # Customer Account
        main_data.FindField('CompanyName').AsString = customer['company_name']
        main_data.FindField('Area').AsString = customer['area']
        main_data.FindField('Terms').AsString = customer['credit_terms']

        # Billing Info
        main_data.FindField('Attention').AsString = bill_to['attention']
        main_data.FindField('Phone1').AsString = bill_to['phone'][0]  # Optional
        main_data.FindField('Fax1').AsString = bill_to['fax'][0]  # Optional
        main_data.FindField('Address1').AsString = bill_to['address'][0]
        main_data.FindField('Address2').AsString = bill_to['address'][1]
        main_data.FindField('Address3').AsString = bill_to['address'][2]
        main_data.FindField('Address4').AsString = bill_to['address'][3]

        # Delivery Info
        main_data.FindField('BranchName').AsString = ship_to['name']
        main_data.FindField('DAttention').AsString = ship_to['attention']
        main_data.FindField('DPhone1').AsString = ship_to['phone'][0]  # Optional
        main_data.FindField('DFax1').AsString = ship_to['fax'][0]  # Optional
        main_data.FindField('DAddress1').AsString = ship_to['address'][0]
        main_data.FindField('DAddress2').AsString = ship_to['address'][1]
        main_data.FindField('DAddress3').AsString = ship_to['address'][2]
        main_data.FindField('DAddress4').AsString = ship_to['address'][3]

        for so_item in so['items']:
            detail_data.Append()
            detail_data.FindField('DtlKey').value = -1
            detail_data.FindField('DocKey').value = -1
            detail_data.FindField('Seq').value = so_item['seq']
            detail_data.FindField('ItemCode').AsString = so_item['item']['code']
            detail_data.FindField('Description').AsString = so_item['description']
            detail_data.FindField('Qty').AsFloat = so_item['quantity']
            detail_data.FindField('UOM').AsString = so_item['uom']['uom']
            detail_data.FindField('Tax').AsString = ""
            detail_data.FindField('TaxRate').AsString = ""
            detail_data.FindField('TaxInclusive').value = 0
            detail_data.FindField('UnitPrice').AsFloat = so_item['price']
            detail_data.FindField('Amount').AsFloat = str(Decimal(so_item['price']) * Decimal(so_item['quantity']))
            detail_data.FindField('TaxAmt').AsFloat = 0
            detail_data.Post()

        biz_object.Save()
        biz_object.Close()
