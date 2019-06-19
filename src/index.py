from collections import namedtuple

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from sql_script import SqlScript

SqlData = namedtuple('SqlData', ('items', 'companies', 'company_branches'))


def _get_sql_data() -> SqlData:
    sql_data = SqlData([], [], [])
    for i in SqlScript('get_stock_items'):
        line = i.decode()
        if line.startswith('i='):
            code, desc, balance, uom, ref_cost, ref_price, _ = line[2:].split('|')
            sql_data.items.append({
                'code': code,
                'desc': desc,
                'balance': balance,
                'uom': uom,
                'ref_cost': ref_cost,
                'ref_price': ref_price
            })
        elif line.startswith('c='):
            company_code, company_name, _ = line[2:].split('|')
            sql_data.companies.append({
                'code': company_code,
                'name': company_name
            })
        elif line.startswith('b='):
            (company_code, branch_name, attention,
             addr1, addr2, addr3, addr4,
             phone1, phone2, fax1, fax2, email, _) = line[2:].split('|')
            sql_data.company_branches.append({
                'company_code': company_code,
                'name': branch_name,
                'attention': attention,
                'address': [addr1, addr2, addr3, addr4],
                'phone': [phone1, phone2],
                'fax': [fax1, fax2],
                'email': email
            })

    return sql_data


def _escape_key(key: str):
    return key.replace('/', '_')


def start():
    cred = credentials.Certificate('../res/serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    sql_data = _get_sql_data()

    for item in sql_data.items:
        print('Uploading item ' + item['code'])
        item_code = _escape_key(item['code'])
        doc_ref = db.document('items/' + item_code)
        doc_ref.set(item)

    for company in sql_data.companies:
        print('Uploading company ' + company['code'])
        company_code = _escape_key(company['code'])
        doc_ref = db.document('companies/' + company_code)
        doc_ref.set(company)

    for branch in sql_data.company_branches:
        print('Uploading company branch ' + branch['name'])
        company_code = _escape_key(branch['company_code'])
        branch_key = _escape_key(branch['name'])
        doc_ref = db.document('companies/' + company_code + '/branches/' + branch_key)
        doc_ref.set(branch)


if __name__ == '__main__':
    start()
