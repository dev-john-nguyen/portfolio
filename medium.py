import requests
import json
import os
from firebase_admin import storage
import firebase_admin
from firebase_admin import credentials

postsPath = "./posts.json"

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.environ.get('PROJECT_ID'),
    "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
    "private_key": os.environ.get('PRIVATE_KEY'),
    "client_email": os.environ.get('CLIENT_EMAIL'),
    "client_id": os.environ.get('CLIENT_ID'),
    "token_uri": "https://oauth2.googleapis.com/token",
})

firebase_app = firebase_admin.initialize_app(
    cred, {"storageBucket": "athletecoder-192c9.appspot.com"})


bucket = storage.bucket()


def formatPost(post):
    s = post['description'].index("<p>")
    e = post['description'].index("</p>")
    preview = post['description'][s:e]
    preview = preview.replace("<strong>", "")
    preview = preview.replace("</strong>", "")
    h4s = post['description'].index("<h4>")
    h4e = post['description'].index("</h4>")
    h4 = post['description'][h4s:h4e]
    post['description'] = h4 + "</h4>" + preview[0:200] + "...</p>"
    r = post["guid"].split("https://medium.com/p/")
    post['id'] = r[1]


def storePosts():
    with open(postsPath) as file:
        data = json.dumps(json.load(file))
        blob = bucket.blob("posts.json")
        blob.upload_from_string(data, content_type="application/json")


def getPosts():
    blob = bucket.blob("posts.json")
    file = blob.download_as_string()
    return json.loads(file)


def findIndex(pred, iterable):
    for x in range(len(iterable)):
        ele = iterable[x]
        if pred(ele):
            return x
    return -1


def mediumPostsHandler():
    # get old posts in store
    print("started")
    postStore = getPosts()
    res = requests.get(
        "https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/@athletecoder")
    obj = res.json()
    posts = obj['items']
    # reformat
    for post in posts:
        formatPost(post)
    # update postStore

    if len(postStore) == 0:
        postStore.extend(posts)
    else:
        for p in posts:
            matchIndex: int = findIndex(
                lambda item: item.get("id") == p.get("id"), postStore)
            if matchIndex > -1:
                postStore[matchIndex] = p
            else:
                postStore.insert(0, p)

    # save posts
    # savePosts(postStore)
    storePosts()
    print("updated")
