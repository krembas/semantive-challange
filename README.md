# Semantive recruitment challenge

My solution for given recruitment challenge task and a "quickstart" description for reviewer ;)

# Design

Minimalistic design & implementation "for recruitment purposes" has been applied for this "project" ;) Application has been designed as a Django application with help of some external libraries (requests, lxml etc), tests are powered by pytest ;). API is simple so there is no need for additional "rest framework" libraries and endpoints are done in pure django. Docker has been used for application "deployment" (app is available at port 8000 of docker container). App is served by Django development server, SQLite DB has been used for simplicity. 

As it's a Django app, it means that whole architecture follows Django app design principles (class based views are used as "API call handlers", models are used for task data/statuses persistence, filesystem based storage is used for images storage. As no asynhronous data gathering was required, page data are gathered during "new task" request so it may take a while.

# API

Here is a REST JSON API designed for application (notice ending slashes;):

API call | info | success response | error response |
-------- | ---- | ---------------- | -------------- |
POST /task/ | *creates new task <br />(page text & images gathering)* |  HTTP200 with json object containing task id and page url | HTTP400/500 with json object containing error message | 
GET /task/<task_id>/status/ | *checks task status* | HTTP200 with json object containing task id and its statuses for text & images (true if ready) | HTTP400/HTTP500 with json object containing error message |
GET /task/<task_id>/text/ | *get page text* | HTTP200 if page text is ready, HTTP202 otherwise. Payload contains json object containing task id, page url and page text (null if text gathering in progress) | HTTP400/HTTP500 with json object containing error message |
GET /task/<task_id>/images/ | *get page images list* | HTTP200 if page images are ready, HTTP202 otherwise. Payload contains json object containing task id, page url and list of images urls (empty if image gathering in progress) | HTTP400/HTTP500 with json object containing error message |
GET /images/<task_id>/<image_filename>/ | *get stored image* | HTTP200 and image file in payload | HTTP400/HTTP500 with json object containing error message |