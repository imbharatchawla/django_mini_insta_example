'''
Purpose: Coding Exercise
@author : Bharat Chawla
@Org: Yoro

The app mysite contains a barebone mini instagram app made entirely for the purpose of 
coding exercise by yoro given to Bharat Chawla.

This app consist of endpoints which are made using django inbuilt methods instead of using DRF.

The app consists of following endpoints with its details:

    - create_album/ - This endpoint will create album for the new user and if the album with same name by same user
    is already created, it will exit with message same album is already created

    - update_album/ - This endpoint will add pictures to the albums created, in base64 strings, the pictures
    must be converted to base64 before handing as payload to the api, as it is a good practice to stream the 
    file instead of using file object directly

    - publish_album/ - This endpoint will change the status of the album from draft to published and also
    to publish the album, hashtag is required, currently only single hashtag is being required but can be changed
    to multiple hashtags in the future with some changes. This endpoint also make some changes in the collection
    which consist of the all the records of the albums published.

    - follow_hashtag/ - This endpoint will return all the users who have used the hashtag sent in payload
    in their albums

    - check_published_albums_by_user/ - This endpoint will return only those album which have been published by
    the user
'''
from subprocess import check_call
from django.http import HttpResponse
from mysite import utils
from mysite.utils import get_db_handle
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse



db_handle = get_db_handle() #get mongo connection handler

#Create as many albums as I want, save it to my outbox, but not publish it yet.
@csrf_exempt ## To exempt from default requirement for CSRF tokens to use postman
def create_album(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        collection = db_handle['albums']
        user_collection = db_handle['user']
        #check if collection already exists
        user_id = data['user_id']
        user_name = data['user_name']
        unique_album_id = data['unique_album_id']

        try:

            check_ = user_collection.find_one({"user_id": user_id, "user_name": user_name})
            if check_ is not None:
                pass
            else:
                user_data = {}
                user_data['user_id'] = data['user_id']
                user_data['user_name'] = data['user_name']
                user_data['albums_id'] = []
                user_data['hashtags_followed'] = []
                user_data['published_albums'] = []
                new_document = user_collection.insert_one(user_data)
                if new_document:
                    pass
            check_ = collection.find_one({"user_id": user_id, "user_name": user_name, "unique_album_id": unique_album_id})
            if check_ is not None:
                message = 'Success, Album {} is already created'.format(data['album_name'])
                return JsonResponse({'status':1, 'message': message})
            else:
                new_document = collection.insert_one(data)
                update_user = user_collection.update_one({"user_id": user_id, "user_name": user_name}, {'$push': {'album_id': unique_album_id}})
                if new_document:
                    message = 'Success, Album {} is created'.format(data['album_name'])
                    return JsonResponse({'status':1, 'message': message})
        # collection.insert_one(sample_record)
        except Exception as e:
            return JsonResponse({'status':0, 'err': 'Failed due to ' + str(e)})


#Add as many pics to any of my unpublished albums. For each pic I can add
#a caption on top of the pic and position it anywhere on the pic and select
#a specific font color
@csrf_exempt ## To exempt from default requirement for CSRF tokens to use postman
def update_album(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        collection = db_handle['albums']
        #check if collection already exists
        user_id = data['user_id']
        user_name = data['user_name']
        unique_album_id = data['unique_album_id']
        try:
            check_ = collection.find_one({"user_id": user_id, "user_name": user_name, "unique_album_id": unique_album_id})
            if check_ is not None:
                pictures = data['pictures']
                # for single_pic in pictures:
                collection.update_one({'unique_album_id': unique_album_id, "user_id": user_id}, {'$push': {'pictures': { '$each': pictures }}})
                message = 'Success, Album {} is updated'.format(data['album_name'])
                return JsonResponse({'status':1, 'message': message})
            else:
                message = 'Success, Album {} does not exist'.format(data['album_name'])
                return JsonResponse({'status':1, 'message': message})
        # collection.insert_one(sample_record)
        except Exception as e:
            return JsonResponse({'status':0, 'err': 'Failed due to ' + str(e)})

#Publish albums from my "drafts" and Add hashtags to my albums before I publish
@csrf_exempt ## To exempt from default requirement for CSRF tokens to use postman
def publish_album(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        if data['hashtag'] == "":
            return JsonResponse({'status':1, 'message': 'Please enter valid Hashtag'})
            
        collection = db_handle['albums']
        hashtag_collection = db_handle['hashtag']
        user_collection = db_handle['user']
        #check if collection already exists
        user_id = data['user_id']
        user_name = data['user_name']
        unique_album_id = data['unique_album_id']
        try:
            check_ = collection.find_one({"user_id": user_id, "user_name": user_name, "unique_album_id": unique_album_id})
            if check_ is not None:
                collection.update_one({'unique_album_id': unique_album_id, "user_id": user_id}, {'$set': {'status': 'published', 'hashtag': data['hashtag']}})
                update_user = user_collection.update_one({"user_id": user_id, "user_name": user_name}, {'$push': {'published_albums': unique_album_id}})
                find_hashtag_collection = hashtag_collection.find_one({'hashtag': data['hashtag']})
                if find_hashtag_collection is not None:
                    hashtag_collection.update_one({'hashtag': data['hashtag']}, {'$push': {'album_id': unique_album_id }})
                else:
                    new_document = hashtag_collection.insert_one({'hashtag': data['hashtag'], 'album_id': [], 'user_lists': []})
                    hashtag_collection.update_one({'hashtag': data['hashtag']}, {'$push': {'album_id': unique_album_id , 'user_lists': user_id }})

                message = 'Success, Album {} is published'.format(data['album_name'])
                return JsonResponse({'status':1, 'message': message})
            else:
                message = 'Success, Album {} does not exist'.format(data['album_name'])
                return JsonResponse({'status':1, 'message': message})
        # collection.insert_one(sample_record)
        except Exception as e:
            return JsonResponse({'status':0, 'err': 'Failed due to ' + str(e)})

# Discover users similar to my tastes & follow them
@csrf_exempt ## To exempt from default requirement for CSRF tokens to use postman
def follow_hashtag(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        if data['hashtag'] == "":
            return JsonResponse({'status':1, 'message': 'Please enter valid Hashtag'})
            
        collection = db_handle['albums']
        hashtag_collection = db_handle['hashtag']
        #check if collection already exists
        user_id = data['user_id']
        user_name = data['user_name']
        try:
            get_users_list = hashtag_collection.find_one({"hashtag": data['hashtag']})
            get_users_list.pop('_id')
            all_user = get_users_list['user_lists']

            return JsonResponse({'status':1, 'users_list': all_user})

        except Exception as e:
            return JsonResponse({'status':0, 'err': 'Failed due to ' + str(e)})

#other user can only see only published albums
@csrf_exempt ## To exempt from default requirement for CSRF tokens to use postman
def check_published_albums_by_user(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        if data['user_id'] == "":
            return JsonResponse({'status':1, 'message': 'Please enter valid user id'})
            
        collection = db_handle['albums']
        user_id = data['user_id']
        try:
            get_users_list = collection.find({"user_id": user_id, "status": "published"})
            album_published = []
            for data in get_users_list:
                data.pop('_id')
                album_name = data['album_name']
                album_published.append(album_name)
            return JsonResponse({'status':1, 'album_published': album_published})

        except Exception as e:
            return JsonResponse({'status':0, 'err': 'Failed due to ' + str(e)})




