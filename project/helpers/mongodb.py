from pymongo import MongoClient

client = MongoClient(os.environ['MONGODBURL'])
db_mongo = client['associations']
collection = db_mongo['associations_data']


def get_association_rules(user_id, metric=None, order=None, limit=None):
    query = {'user_id': user_id}

    if metric and order:
        sort_key = metric.lower()
        query['$orderby'] = {sort_key: order}

    if limit:
        query['$limit'] = limit

    return list(collection.find(query))


def get_association_rules_by_antecedent(user_id, antecedent, metric=None, order=None, limit=None):
    query = {'user_id': user_id, 'antecedent': antecedent}

    if metric and order:
        sort_key = metric.lower()
        query['$orderby'] = {sort_key: order}

    if limit:
        query['$limit'] = limit

    return list(collection.find(query))
