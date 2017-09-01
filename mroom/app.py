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

from flask import request
from urllib.parse import urlparse, parse_qs
import collections
import contextlib
import flask
import json
import os
import decorators from './decorators'
import models from './models'


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'REPLACE WITH RANDOM STRING ;-)'


@app.route('/room/<room_name>')
def room(room_name):
  """
  Visiting a room automatically creates it if it doesn't already exist.
  """

  room = models.Room.objects(name=room_name).first()
  if not room:
    room = models.Room.create(name=room_name)

  return flask.render_template('index.html', room=room)


@app.route('/api/submit', methods=['POST'])
@decorators.restify()
def submit():
  """
  REST end-point to add a song to the queue of a room.
  """

  if not 'room' in request.form or not 'url' in request.form:
    return None, 400, "Invalid form parameters"
  room = models.Room.objects(name=request.form['room'])
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
    video_id = query['v'][0]
    # TODO: Find video name and length.
    print('YouTube:', video_id)
  elif 'soundcloud' in url.netloc:
    path = url.path
    # TODO: Find track name and length.
    print('SoundCloud:', path)
  else:
    raise RuntimeError

  # TODO: Update existing song information (just in case it is outdated)
  #       and add the song to the queue of the current room.
  return None


if require.main == module:
  app.run(host='0.0.0.0', debug=True)
