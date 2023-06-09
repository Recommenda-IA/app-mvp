from pymongo import MongoClient, ASCENDING, DESCENDING, IndexModel
import os
import json


class Mongo:
    def __init__(self, db, collection):
        self.client = MongoClient(os.environ['MONGODBURL'])
        self.db = self.client[db]
        self.collection = self.db[collection]

    def get_association_rules(self, user_id, metric=None, order=None, limit=None):
        query = {'user_id': user_id}
        sort = []

        if metric and order:
            sort_key = metric.lower()
            sort_direction = ASCENDING if order.lower() == 'asc' else DESCENDING
            sort.append((sort_key, sort_direction))

        cursor = self.collection.find(query).sort(sort).limit(limit)
        rules = []

        for rule in cursor:
            rule['_id'] = str(rule['_id'])
            rules.append(rule)

        return json.dumps(rules)

    def get_association_rules_by_antecedent(self, user_id, antecedent, metric=None, order=None, limit=None):
        query = {'user_id': user_id, 'antecedents': {'$all': antecedent}}

        sort = []

        if metric and order:
            sort_key = metric.lower()
            sort_direction = ASCENDING if order.lower() == 'asc' else DESCENDING
            sort.append((sort_key, sort_direction))

        cursor = self.collection.find(query).sort(sort).limit(limit)
        rules = []

        for rule in cursor:
            rule['_id'] = str(rule['_id'])
            rules.append(rule)

        return json.dumps(rules)

    def search_mongodb(self, user_id, search_item_id, sort_option, sort_order):
        query = {'user_id': user_id, 'antecedents': {'$all': search_item_id}}
        sort_key = sort_option if sort_order == 'asc' else '-' + sort_option
        results = self.collection.find(query).sort(sort_key).limit(30)
        return results

    def create_indexes(self):
        self.collection.create_indexes([
            IndexModel([('user_id', DESCENDING)]),
            IndexModel([('antecedents', DESCENDING)]),
            IndexModel([('support', DESCENDING)]),
            IndexModel([('confidence', DESCENDING)]),
            IndexModel([('lift', DESCENDING)]),
            IndexModel([('consequent', DESCENDING)])
        ])

        return True
