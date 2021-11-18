from pymongo import MongoClient


class InstagramPipeline:
    def __init__(self):
        client = MongoClient("localhost", 27017)
        self.instagram_db = client["instagram"]

    def process_item(self, item, spider):
        collection = self.instagram_db[item["collection_name"]]
        new_item = dict(item)
        new_item.pop("collection_name")
        new_item[item["collection_name"]] = new_item.pop("users")

        try:
            user = list(collection.find({"_id": new_item["_id"]}))[0]
            user[item["collection_name"]] += new_item[item["collection_name"]]

            ids = set()
            users_without_duplicate = []
            for el in user[item["collection_name"]]:
                if el["_id"] not in ids:
                    print("ADD", el)
                    ids.add(el["_id"])
                    users_without_duplicate.append(el)
                else:
                    print("DIPLICATE", el)

            new_item[item["collection_name"]] = users_without_duplicate
        except Exception as ex:
            print(ex)
        finally:
            collection.update_one({'_id': f'{new_item["_id"]}'}, {'$set': new_item}, upsert=True)
        return item
