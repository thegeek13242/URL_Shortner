# URL_Shortner
This is a free and simple URL Shortner API developed using python3 & flask.
This API uses MD5 as hashing algorithm to calculate hash, currently only first 6 characters are stored in database with the corresponding URL.


## Request Format

The URL needs to follow the ReGex pattern `((http|https)://)(www.)?" +
                 "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                 "{2,256}\\.[a-z]" +
                 "{2,6}\\b([-a-zA-Z0-9@:%" +
                 "._\\+~#?&//=]*)`

You need to send the JSON object to the API. An example of the request is as follows:

`curl http://femto.me:5000/shorten -H "content-type: application/json" --data '{\"url\":\" ---url-to-shorten--- \"}'`

## Response

### Hash already present in the DB (Repeated URL sent for shortening or hash collision)

`{"Message":"Already exists","shortened_url":"http://femto.me:5000/---hash---"}`

### URL not following the ReGex Pattern

`{"Message":"Invalid URL","shortened_url":""}`

### Successful Operation

`{"Message":"Success","shortened_url":"http://femto.me:5000/---hash---"}`
