from flask import Flask, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from medium import mediumPostsHandler, getPosts
import os

app = Flask(__name__)

scheduler = BackgroundScheduler()
# run job every day at midnight
scheduler.add_job(mediumPostsHandler, 'cron', month='*',
                  day='*', hour='0')
scheduler.start()

# catch all paths

app = Flask(__name__, static_folder='client/build')


# api paths


@app.route('/api/posts', methods=['GET'])
def apiPaths():
    posts = getPosts()
    return {"data": posts}


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def allPaths(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=True)
