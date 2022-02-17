import pymongo
import certifi
from . import config


def create_client():
    client = pymongo.MongoClient(
        host=config.MONGODB_HOST,
        tlsCAFile = certifi.where()
    )
    return client


def insert_into_table(data, db_table_name):

    try:
        db_name, table_name = db_table_name.split('.')
        mongo_client = create_client()
        table = mongo_client[db_name][table_name]

        if isinstance(data, dict):
            response = table.insert_one(data)
        elif isinstance(data, list):
            response = table.insert_many(data)
    except:
        pass


def find_one_in_table(data, db_table_name):

    mongodb_client = create_client()

    db_name, table_name = db_table_name.split('.')
    table = mongodb_client[db_name][table_name]

    response = table.find_one(data)

    mongodb_client.close()

    return response


def delete_one_from_table(data, db_table_name):

    mongodb_client = create_client()

    db_name, table_name = db_table_name.split('.')
    table = mongodb_client[db_name][table_name]

    response = table.delete_one(data)

    if response.deleted_count == 0:
        raise ValueError

    mongodb_client.close()

    return response


def get_approved_groups(db):
    
    mongo_client = create_client()
    table = mongo_client[db]['approved_groups']

    response = table.find({},{'group_id': 1})

    all_groups = [item['group_id'] for item in response]

    mongo_client.close()

    return all_groups


def get_blacklist_users(db):
    
    mongo_client = create_client()
    table = mongo_client[db]['blacklist_users']

    response = table.find({},{'_id': 1, 'user_id': 1, 'infringement_count': 1})

    blacklisted_users = [item['user_id'] for item in response if int(item['infringement_count']) >= 3]

    mongo_client.close()

    return blacklisted_users


def update_watchlist_table(data, db_table_name):

    mongo_client = create_client()
    db_name, table_name = db_table_name.split('.')
    table = mongo_client[db_name][table_name]

    existing_info = find_one_in_table({'user_id': data['user_id']}, db_table_name)

    if existing_info is not None:
        if 'infringement_count' not in data:
            new_count = int(existing_info['infringement_count'])+1
        else:
            new_count = data['infringement_count']

        response = table.update_one(
            {'user_id': data['user_id']},
            {'$set': {'infringement_count': new_count}})

        print("Updated {} items in watchlist_users.".format(response.modified_count))
    else:
        if 'infringement_count' not in data:
            data['infringement_count'] = 1

        response = table.insert_one(data)

    mongo_client.close()
