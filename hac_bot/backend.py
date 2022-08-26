import json
import certifi
import requests
import pymongo
from . import config


class AtlasAPI:
    """
    Atlas API functions
    """

    def __init__(self) -> None:
        self._base_url = config.MONGODB_API_URL
        self._api_key = config.MONGODB_API_KEY
        self._data_source = config.MONGODB_DATA_SOURCE

    def _make_request(self, endpoint, db_name, table_name, payload: dict):

        url = f"{self._base_url}{endpoint}"

        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key
        }

        data = {
            "dataSource": self._data_source,
            "database": db_name,
            "collection": table_name
        }
        # Add information for specific actions
        data.update(payload)

        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        return response

    def insert(self, db_name, table_name, data):

        if isinstance(data, dict):
            endpoint = "/action/insertOne"
            payload = {"document": data}
        elif isinstance(data, list):
            endpoint = "/action/insertMany"
            payload = {"documents": data}
        response = self._make_request(endpoint, db_name, table_name, payload)
        return response

    def find_one(self, db_name, table_name, data):
        endpoint = '/action/findOne'
        payload = {
            "filter" : data
        }
        response = self._make_request(endpoint, db_name, table_name, payload)
        return response.json()['document']

    def find_all(self, db_name, table_name, filters=None, projection=None):
        endpoint = "/action/find"
        if filters is None:
            filters = {}
        if projection is None:
            projection = {}
        payload = {
            "filter": filters,
            "projection": projection
        }
        response = self._make_request(endpoint, db_name, table_name, payload)
        return response.json()['documents']

    def delete_one(self, db_name, table_name, data):
        endpoint = "/action/deleteOne"
        payload = {"filter": data}
        response = self._make_request(endpoint, db_name, table_name, payload)
        return response

    def update_one(self, db_name, table_name, primary_key: dict, update_query: dict):
        endpoint = "/action/updateOne"
        payload = {
            "filter": primary_key,
            "update": update_query
        }
        response = self._make_request(endpoint, db_name, table_name, payload)
        return response


class PyMongo:

    def __init__(self) -> None:
        self.client = pymongo.MongoClient(
            host=config.MONGODB_HOST,
            port=int(config.MONGODB_PORT),
            tlsCAFile = certifi.where()
        )

    def insert(self, db_name, table_name, data):
        table = self.client[db_name][table_name]
        if isinstance(data, dict):
            response = table.insert_one(data)
        elif isinstance(data, list):
            response = table.insert_many(data)
        return response

    def find_one(self, db_name, table_name, data):
        table = self.client[db_name][table_name]
        response = table.find_one(data)
        return response

    def delete_one(self, db_name, table_name, data):
        table = self.client[db_name][table_name]
        response = table.delete_one(data)
        if response.deleted_count == 0:
            raise ValueError
        return response

    def find_all(self, db_name, table_name, filters=None, projection=None):    
        table = self.client[db_name][table_name]
        if filters is None:
            filters = {}
        if projection is None:
            projection = {}
        response = table.find(filters, projection)
        return response

    def update_one(self, db_name, table_name, primary_key: dict, update_query: dict):
        table = self.client[db_name, table_name]
        response = table.update_one(primary_key, update_query)
        return response


def initiate():
    if config.BOT_BACKEND == "mongodb":
        obj = PyMongo()
    elif config.BOT_BACKEND == "atlas_api":
        obj = AtlasAPI()
    else:
        raise AttributeError("Invalid Backend configuration.")
    return obj


def insert_into_table(data, db_table_name):
    try:
        db_name, table_name = db_table_name.split('.')
        mongodb = initiate()
        response = mongodb.insert(db_name, table_name, data)
    except:
        pass


def find_one_in_table(data, db_table_name):

    db_name, table_name = db_table_name.split('.')
    mongodb = initiate()
    response = mongodb.find_one(db_name, table_name, data)
    return response


def delete_one_from_table(data, db_table_name):

    db_name, table_name = db_table_name.split('.')
    mongodb = initiate()
    response = mongodb.delete_one(db_name, table_name, data)
    return response


def get_approved_groups(db_name):

    table_name = 'approved_groups'
    mongodb = initiate()
    response = mongodb.find_all(db_name, table_name, projection={'group_id': 1})
    all_groups = [item['group_id'] for item in response]
    return all_groups


def get_blacklist_users(db_name):

    table_name = 'blacklist_users'
    mongodb = initiate()
    response = mongodb.find_all(db_name, table_name,
        projection={'_id': 1, 'user_id': 1, 'infringement_count': 1}
    )
    blacklisted_users = [item['user_id'] for item in response if int(item['infringement_count']) >= 3]
    return blacklisted_users


def update_watchlist_table(data, db_table_name):

    db_name, table_name = db_table_name.split('.')
    mongodb = initiate()

    existing_info = mongodb.find_one(db_name, table_name, {'user_id': data['user_id']})
    if existing_info is not None:
        if 'infringement_count' not in data:
            new_count = int(existing_info['infringement_count'])+1
        else:
            new_count = data['infringement_count']
        response = mongodb.update_one(db_name, table_name,
            primary_key={'user_id': data['user_id']},
            update_query={'$set': {'infringement_count': new_count}}
        )
        print(f"Updated {response.modified_count} items in watchlist_users.")
    else:
        if 'infringement_count' not in data:
            data['infringement_count'] = 1
        response = mongodb.insert(db_name, table_name, data)
