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

from pony.orm import *
from datetime import datetime
import conf from '../conf'

session = db_session
db = Database()


def create_or_update(model, filter_keys, **kwargs):
  obj = model.get(**{k: kwargs[k] for k in filter_keys})
  if obj:
    for k, v in kwargs.items():
      setattr(obj, k, v)
  else:
    obj = model(**kwargs)
  return obj


class Room(db.Entity):
  name = PrimaryKey(str)
  song = Optional('Song', reverse='currently_playing_in')
  song_starttime = Optional(datetime)
  history = Set('Song')
  queue = Set('Song')


class Song(db.Entity):
  title = Required(str)
  duration = Required(int)

  currently_playing_in = Set(Room, reverse='song')
  history_in = Set(Room, reverse='history')
  queued_in = Set(Room, reverse='queue')

  def to_dict(self):
    result = super().to_dict()
    result['url'] = self.url
    return result


class YtSong(Song):
  video_id = Required(str)

  @property
  def url(self):
    return 'https://www.youtube.com/watch?v=' + self.video_id

class ScSong(Song):
  path = Required(str)
  song_id = Required(str)

  @property
  def url(self):
    raise NotImplementedError


db.bind(**conf.database)
db.generate_mapping(create_tables=True)
