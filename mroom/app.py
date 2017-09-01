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
from urllib.parse import urlparse, parse_qs
import collections
import contextlib
import flask
import json
import os
import decorators from './decorators'
import models from './models'
import youtube from './youtube'
import conf from '../conf.json'


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = conf['web']['secretKey']


@app.route('/room/<room_name>')
def room(room_name):
  """
  Visiting a room automatically creates it if it doesn't already exist.
  """

  room = models.Room.objects(name=room_name).first()
  if not room:
    room = models.Room.create(name=room_name)

  return flask.render_template('index.html', room=room)


@app.route('/api/queue')
@decorators.restify()
def queue():
  """
  Returns a JSON representation of the the songs in the queue.
  """

  room_name = request.args.get('room')
  room = models.Room.objects(name=room_name).first()
  if not room_name or not room:
    return None, 404

  songs = models.Song.filter(id__in=room.queued)
  return [x.to_json() for x in songs]


@app.route('/api/current-song')
@decorators.restify()
def current_song():
  room_name = request.args.get('room')
  room = models.Room.objects(name=room_name).first()
  if not room_name or not room:
    return None, 404

  now = datetime.now()

  print('/api/current-song')
  if room.current_song_id is None:
    song = None
  else:
    song = models.Song.objects(id=room.current_song_id).first()
  print('  SONG:', song, song.title if song else None)

  # Check if this song has already stopped. Also consume as many items
  # as necessary to find the song that is currently playing.
  if song and room.current_song_starttime is not None:
    time_passed = now - timedelta(seconds=room.current_song_starttime)
    print('  TIME PASSED:', time_passed)
    while song:
      current_duration = timedelta(seconds=song.duration_in_seconds)
      print('    CURRENT DURATION:', current_duration)
      if time_passed < current_duration:
        break
      # Discard this song into the rooms history.
      time_passed -= current_duration
      room.history.append(song.id)
      song = None
      if room.queued:
        song = models.Song.objects(id=room.queued.pop(0)).first()
      print('      NEXT SONG:', song)

    if not song:
      time_passed = None
  else:
    time_passed = None

  if song is None and room.queued:
    song = models.Song.filter(id=room.queued.pop(0)).get()
    time_passed = timedelta(seconds=0)

  print('  FINAL SONG:', repr(song))
  print('  FINAL TIME PASSED:', time_passed)
  room.current_song_id = song.id if song else None
  room.current_song_starttime = now + time_passed if time_passed else None
  room.save()

  return {
    'song': song.to_json() if song else None,
    'time_passed': time_passed.total_seconds() if time_passed else None
  }


@app.route('/api/submit', methods=['POST'])
@decorators.restify()
def submit():
  """
  REST end-point to add a song to the queue of a room.
  """

  if not 'room' in request.form or not 'url' in request.form:
    return None, 400, "Invalid form parameters"
  room = models.Room.objects(name=request.form['room']).first()
  if not room:
    return None, 400, "Invalid room {!r}".format(request.form['room'])

  url = urlparse(request.form['url'])

  # Validate the URL scheme and host.
  HOSTS = ['www.youtube.com', 'youtube.com', 'www.soundcloud.com' 'soundcloud.com']
  if url.scheme not in ('', 'http', 'https') or url.netloc not in HOSTS:
    return None, 400, "Not a YouTube/SoundCloud URL."

  if 'youtube' in url.netloc:
    query = parse_qs(url.query)
    if 'v' not in query or len(query['v']) != 1:
      return None, 400, "This is a YouTube URL, but it looks like there's not Video ID."
    try:
      video = youtube.video(query['v'][0])
    except ValueError as e:
      return None, 400, str(e)

    song = models.create_or_update(
      models.YouTubeSong,
      primary_keys = ['video_id'],
      video_id = video['id'],
      title = video['snippet']['title'],
      live_broadcast = video['snippet']['liveBroadcastContent'],
      duration = video['contentDetails']['duration'],
      definition = video['contentDetails']['definition']
    )
    song.save()
    print(">>> NEW SONG:", song)
    print('    ', dict(song.items()))

  elif 'soundcloud' in url.netloc:
    return None, 501, "SoundCloud is not yet implemented."
  else:
    raise RuntimeError

  # Check if the song is already in the rooms queue.
  in_queue = song.id in room.queued
  result = {'title': song.title, 'duration': song.duration_in_seconds,
            'alreadyInQueue': in_queue, 'url': song.url, 'type': song.type}
  if not in_queue:
    room.queued.append(song.id)
    room.save()

  return result, 200


if require.main == module:
  app.run(host=conf['web']['host'], port=conf['web']['port'],
          debug=conf['web']['debug'])
