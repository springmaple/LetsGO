from sql import Sql


def start_query():
    sales_order_code = 'YEN00535'
    with Sql() as sql:
        print(sql.get_sl_so(sales_order_code))
        print(sql.get_outstanding_so(sales_order_code))
        print(sql.get_sl_invoice_dtl(sales_order_code))


if __name__ == '__main__':
    start_query()
