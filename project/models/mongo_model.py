from pymongo import MongoClient, ASCENDING, DESCENDING
import os
import json

client = MongoClient(os.environ['MONGODBURL'])
db_mongo = client['associations']
collection = db_mongo['associations_data']


def get_association_rules(user_id, metric=None, order=None, limit=None):
    query = {'user_id': user_id}
    sort = []

    if metric and order:
        sort_key = metric.lower()
        sort_direction = ASCENDING if order.lower() == 'asc' else DESCENDING
        sort.append((sort_key, sort_direction))

    cursor = collection.find(query).sort(sort).limit(limit)
    rules = []

    for rule in cursor:
        rule['_id'] = str(rule['_id'])
        rules.append(rule)

    return json.dumps(rules)


def get_association_rules_by_antecedent(user_id, antecedent, metric=None, order=None, limit=None):
    query = {'user_id': user_id, 'antecedents': {'$all': antecedent}}

    sort = []

    if metric and order:
        sort_key = metric.lower()
        sort_direction = ASCENDING if order.lower() == 'asc' else DESCENDING
        sort.append((sort_key, sort_direction))

    cursor = collection.find(query).sort(sort).limit(limit)
    rules = []

    for rule in cursor:
        rule['_id'] = str(rule['_id'])
        rules.append(rule)

    return json.dumps(rules)
