from constants import SalesOrderStatus
from firestore import get_firestore_instance

fs = get_firestore_instance()

collection = f'data/yotime/salesOrders'
all = []
for doc in fs.collection(collection) \
        .where('status', '==', SalesOrderStatus.Open.value) \
        .order_by('created_on').stream():
    all.append(doc.to_dict())

for a in all:
    print(a['code'])
