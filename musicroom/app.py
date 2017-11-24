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
from flask_socketio import SocketIO, emit, join_room
from pony.orm import db_session
from urllib.parse import urlparse, parse_qs

import collections
import contextlib
import flask
import functools
import json
import os
import random
import re
import socketio

import conf from '../conf'
import decorators from './decorators'
import models from './models'
import youtube from './youtube'
import namegen from './namegen'
import {Scheduler} from './utils/scheduler'

app = flask.Flask(__name__, root_path=str(module.directory))
sio = SocketIO(app, async_mode='threading' if conf.debug else 'gevent')


@sio.on('connect')
def connect():
  pass


@sio.on('join')
def join(room_name):
  join_room(room_name)


@sio.on('get current song')
@db_session
def current_song(room_name):
  room = models.Room.get(name=room_name)
  if room:
    room.emit_current_song(broadcast=False)


@sio.on('get queue and history')
@db_session
def queue_and_history(room_name):
  room = models.Room.get(name=room_name)
  if room:
    queue = [x.to_dict() for x in room.queue]
    history = [x.to_dict() for x in room.history]
    emit('queue and history', {'queue': queue, 'history': history})


@sio.on('skip song')
@db_session
def skip(room_name):
  room = models.Room.get(name=room_name)
  if room:
    room.skip_song()
    room.add_to_schedule()
    room.emit_current_song()


@sio.on('put song')
@db_session
def put_song_sio(room_name, url):
  try:
    song = _put_song(room_name, url)
  except ValueError as e:
    emit('put song', {'error': str(e)})
  else:
    emit('put song', {'song': song.to_dict()})


@app.route('/')
def index():
  """
  Presents a form to go to a new room.
  """

  funny_name = namegen()
  return flask.render_template('index.html', funny_name=funny_name,
    room_name_validate=conf.room_name_validate)


@app.route('/room/<room_name>')
@db_session
def room(room_name):
  """
  Visiting a room automatically creates it if it doesn't already exist.
  """

  if not re.match(conf.room_name_validate, room_name):
    flask.abort(404)

  room = models.Room.get(name=room_name)
  if not room:
    room = models.Room(name=room_name)

  return flask.render_template('room.html', room=room)


@app.route('/room/<room_name>/put')
@decorators.restify()
@db_session
def put_song_api(room_name):
  url = request.args.get('url')
  if not url:
    flask.abort(404)
  try:
    song = _put_song(room_name, url)
  except ValueError as e:
    return {'error': str(e)}
  else:
    return {'song': song.to_dict()}


def _put_song(room_name, url):
  room = models.Room.get(name=room_name)
  if not room:
    raise ValueError('invalid room: {!r}'.format(room))

  url = urlparse(url)

  # Validate the URL scheme and host.
  HOSTS = ['www.youtube.com', 'youtube.com', 'youtu.be']
  if url.scheme not in ('', 'http', 'https') or url.netloc not in HOSTS:
    raise ValueError('not a youtube url')

  # Parse the Youtube Video ID.
  if 'youtube' in url.netloc:
    query = parse_qs(url.query)
    if 'v' not in query or len(query['v']) != 1:
      raise ValueError("This is a YouTube URL, but it looks like there's not Video ID.")
    yt_video_id = query['v'][0]
  elif 'youtu.be' in url.netloc:
    yt_video_id = url.path.lstrip('/')
  else:
    yt_video_id = None

  # Create/update the YouTube Song.
  if yt_video_id:
    song = models.YtSong.from_video_id(yt_video_id)
  else:
    raise RuntimeError

  added = room.add_song(song)
  if not added:
    raise ValueError("Song is already in queue: " + song.title)

  if not room.song:
    room.update_song()
    room.emit_current_song()
  room.add_to_schedule()
  return song
