from sql import Sql

if __name__ == '__main__':
    def convert(data):
        from sql import StockItem
        return StockItem(data)


    with Sql() as s:
        # table_name = 'ST_ITEM'
        # last_modified = 1593424831
        # total = s.count_master_data(table_name, last_modified)
        # for stock in s.get_master_data(table_name, total, convert, last_modified):
        #     if stock.code == 'SKP28307L':
        #         print(stock.to_dict())

        last_trans_no = 0
        for stock_trans in s.get_st_trans(last_trans_no):
            if stock_trans.item_code == 'SKP28307L':
                print(stock_trans.to_dict())
