
import collections
import contextlib
import flask
import json
import os
from urllib.parse import urlparse, parse_qs
from flask import request

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'REPLACE WITH RANDOM STRING ;-)'
queue = collections.deque()

@app.route('/', methods=['GET', 'POST'])
def view_index():
  if request.method == 'POST' and 'queue-url' in request.form:
    info = urlparse(request.form['queue-url'])
    params = parse_qs(info.query)
    if 'v' not in params:
      flask.flash('URL does not look like a YouTube Video URL')
    else:
      video_id = params['v'][0]
      flask.flash('Video {!r} added'.format(video_id))
      queue.append(video_id)
  return flask.render_template('index.html', queue=queue)

@app.route('/play')
def view_play():
  return flask.render_template('play.html', queue=queue)


@app.route('/api/queue')
def view_queue():
  return flask.Response(json.dumps(list(queue)), mimetype="application/json")


@app.route('/api/queue-pop')
def view_queue_pop():
  if not queue:
    data = {"status": "empty queue"}
  else:
    data = {"status": "ok", "videoId": queue.popleft()}
  return flask.Response(json.dumps(data), mimetype="application/json")


if require.main == module:
  app.run(host='0.0.0.0')
