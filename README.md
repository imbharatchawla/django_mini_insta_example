# django_mini_insta_example

- JSON file for all the POSTMAN endpoints is also include, please import that and use that.
- MongoDB has been used as the DB in the Backend.

Purpose: Coding Exercise
@author : Bharat Chawla (git: @imbharatchawla)
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
