# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime, timedelta
from flask import request
from pony.orm import db_session, commit
from urllib.parse import urlparse, parse_qs

import collections
import contextlib
import flask
import json
import os
import random
import decorators from './decorators'
import models from './models'
import youtube from './youtube'
import namegen from './namegen'


app = flask.Flask(__name__, root_path=__directory__)


@app.route('/')
def index():
  """
  Presents a form to go to a new room.
  """

  funny_name = namegen()
  return flask.render_template('index.html', funny_name=funny_name)


@app.route('/room/<room_name>')
@db_session
def room(room_name):
  """
  Visiting a room automatically creates it if it doesn't already exist.
  """

  room = models.Room.get(name=room_name)
  if not room:
    room = models.Room(name=room_name)
    commit()

  return flask.render_template('room.html', room=room)


@app.route('/api/queue')
@decorators.restify()
@db_session
def queue():
  """
  Returns a JSON representation of the the songs in the queue.
  """

  room = models.Room.get(name=request.args.get('room'))
  if not room:
    return None, 404

  return [x.to_dict() for x in room.queue]


@app.route('/api/history')
@decorators.restify()
@db_session
def history():
  """
  Returns a JSON representation of the the songs in the history.
  """

  room = models.Room.get(name=request.args.get('room'))
  if not room:
    return None, 404

  return [x.to_dict() for x in room.history]


@app.route('/api/skip-song', methods=['POST'])
@decorators.restify()
@db_session
def skip_song():
  """
  Skips the currently played song.
  """

  room = models.Room.get(name=request.args.get('room'))
  if not room:
    return None, 404

  room.skip_song()


@app.route('/api/current-song')
@decorators.restify()
@db_session
def current_song():
  """
  Updates the room's currently played song and returns it.
  """

  room = models.Room.get(name=request.args.get('room'))
  if not room:
    return None, 404

  song, time_passed = room.update_song()
  commit()

  if song:
    result = song.to_dict()
    result['time_passed'] = time_passed.total_seconds()
  else:
    result = {}
  return result


@app.route('/api/submit', methods=['POST'])
@decorators.restify()
@db_session
def submit():
  """
  REST end-point to add a song to the queue of a room.
  """

  if not 'room' in request.form or not 'url' in request.form:
    return None, 400, "Invalid form parameters"

  room = models.Room.get(name=request.form['room'])
  if not room:
    return None, 400, "Invalid room {!r}".format(request.form['room'])

  url = urlparse(request.form['url'])

  # Validate the URL scheme and host.
  HOSTS = ['www.youtube.com', 'youtube.com', 'youtu.be']
  if url.scheme not in ('', 'http', 'https') or url.netloc not in HOSTS:
    return None, 400, "Not a YouTube URL."

  # Parse the Youtube Video ID.
  if 'youtube' in url.netloc:
    query = parse_qs(url.query)
    if 'v' not in query or len(query['v']) != 1:
      return None, 400, "This is a YouTube URL, but it looks like there's not Video ID."
    yt_video_id = query['v'][0]
  elif 'youtu.be' in url.netloc:
    yt_video_id = url.path.lstrip('/')
  else:
    yt_video_id = None

  # Create/update the YouTube Song.
  if yt_video_id:
    try:
      video = youtube.video(yt_video_id)
    except ValueError as e:
      return None, 400, str(e)

    song = models.create_or_update(
      models.YtSong,
      filter_keys = ['video_id'],
      title = video['snippet']['title'],
      video_id = video['id'],
      duration = youtube.parse_duration(video['contentDetails']['duration'])
    )
    commit()

  else:
    raise RuntimeError

  # Check if the song is already in the rooms queue.
  result = song.to_dict()
  result['already_in_queue'] = song in room.queue
  if not result['already_in_queue']:
    room.queue.add(song)

  commit()
  return result, 200
