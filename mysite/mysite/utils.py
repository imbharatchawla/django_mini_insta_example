from pymongo import MongoClient
def get_db_handle(db_name="", host="", port=0):

 client = MongoClient(host='localhost',
                      port=27017
                     )
 db_handle = client['insta']
 return db_handle