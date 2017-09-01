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

import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table, drop_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType
from datetime import datetime
import conf from '../conf.json'
import youtube from './youtube'


def create_or_update(model_class, primary_keys, **kwargs):
  query = model_class.objects(**{k: kwargs[k] for k in primary_keys})
  if query.count() > 1:
    raise ValueError('more than one object returned')
  obj = query.first()
  if obj:
    obj.update(**kwargs)
  else:
    obj = model_class.create(**kwargs)
  return obj


def to_json(x, default=None):
  if hasattr(x, 'to_json'):
    return x.to_json()
  elif isinstance(x, list):
    return [to_json(y, default) for y in x]
  elif isinstance(x, dict):
    return {k: to_json(v, default) for k, v in x.items()}
  elif x is None or isinstance(x, (bool, int, float, str)):
    return x
  if default:
    x = default(x)
  return x


class JSONSerializable:
  """
  Mixin for JSON Serializables.
  """

  __json_fields__ = []

  @staticmethod
  def __json_default__(obj):
    return str(obj)

  def to_json(self):
    result = {}
    for field in self.__json_fields__:
      result[field] = to_json(getattr(self, field), self.__json_default__)
    return result


class Song(Model, JSONSerializable):
  __json_fields__ = ['id', 'type', 'title']
  id = columns.UUID(primary_key=True, default=uuid.uuid4)
  type = columns.Ascii(discriminator_column=True, index=True)
  title = columns.Text()


class YouTubeSong(Song):
  __discriminator_value__ = 'youtube'
  __json_fields__ = Song.__json_fields__ + ['url', 'video_id', 'duration',
    'duration_in_seconds', 'licensed_content', 'live_broadcast']

  video_id = columns.Ascii(index=True)
  duration = columns.Ascii()    # As ISO 8601 string
  definition = columns.Ascii()
  licensed_content = columns.Boolean()
  live_broadcast = columns.Ascii()  # "live", "none" or "upcoming"

  @property
  def duration_in_seconds(self):
    return youtube.parse_duration(self.duration)

  @property
  def url(self):
    return 'https://www.youtube.com/watch?v=' + self.video_id


class SoundCloudSong(Song):
  __discriminator_value__ = 'soundcloud'
  path = columns.Ascii(index=True)
  api_url = columns.Ascii()
  length = columns.Integer()

  @property
  def duration_in_seconds(self):
    raise NotImplementedError

  @property
  def url(self):
    return 'https://www.soundcloud.com' + self.path


class Room(Model):
  id = columns.UUID(primary_key=True, default=uuid.uuid4)
  name = columns.Text(index=True)
  created_at = columns.DateTime(default=datetime.now)

  # The song that is currently playing in the room.
  current_song_id = columns.UUID(default=None)

  # The (server) time that the song has started playing in the room.
  current_song_starttime = columns.DateTime(default=None)

  # A list of songs that have been played in the room.
  history = columns.List(columns.UUID())

  # A list of songs that are going to be played in the room.
  queued = columns.List(columns.UUID())


connection.setup(
  conf['auth']['cassandra']['clusterIps'],
  conf['auth']['cassandra']['keyspace'],
  protocol_version=3)

#drop_table(Song)
#drop_table(YouTubeSong)
#drop_table(SoundCloudSong)
#drop_table(Room)

sync_table(Song)
sync_table(YouTubeSong)
sync_table(SoundCloudSong)
sync_table(Room)


print()
for song in Song.filter(id='7f076585-4d13-4f7e-a7bc-5cea1661fc75').all():
  print(repr(song))
