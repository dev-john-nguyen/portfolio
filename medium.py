import requests
import json
import os
postsPath = "posts.json"


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


def savePosts(posts):
    with open(postsPath, "w") as file:
        json.dump(posts, file)


def getPosts():
    if os.path.isfile(postsPath) and os.access(postsPath, os.R_OK):
        with open(postsPath) as file:
            return json.load(file)
    else:
        return []


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
    savePosts(postStore)
    print("updated")
