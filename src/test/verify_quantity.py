from firestore import get_firestore_instance

fs = get_firestore_instance()

company_code = 'yotime'
item_code = 'SR626SW-M'

document_path = f'data/{company_code}/itemQuantities/{item_code}'
item_quantities = fs.document(document_path)
print(item_quantities.get().to_dict())

collection = f'data/{company_code}/salesOrders'
total = 0
for doc in fs.collection(collection).stream():
    data = doc.to_dict()
    if data['status'] != 'open':
        continue

    subtotal = 0
    for item in data['items']:
        if item['item']['code'] == item_code:
            total += item['quantity']
            subtotal += item['quantity']

    if subtotal > 0:
        print(data['code'], subtotal)

print('total', total)
