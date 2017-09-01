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


class Song(Model):
  id = columns.UUID(primary_key=True)
  type = columns.Ascii(discriminator_column=True)


class YouTubeSong(Song):
  __discriminator_value__ = 'youtube'
  video_id = columns.Ascii(index=True)
  length = columns.Integer()


class SoundCloudSong(Song):
  __discriminator_value__ = 'soundcloud'
  path = columns.Ascii(index=True)
  api_url = columns.Ascii()
  length = columns.Integer()


class Room(Model):
  id = columns.UUID(primary_key=True, default=uuid.uuid4)
  name = columns.Text(index=True)
  created_at = columns.DateTime(default=datetime.now)

  # The song that is currently playing in the room.
  current_song = columns.UUID(default=None)

  # The (server) time that the song has started playing in the room.
  current_song_started = columns.DateTime(default=None)

  # A list of songs that have been played in the room.
  history = columns.List(columns.UUID())

  # A list of songs that are going to be played in the room.
  queued = columns.List(columns.UUID())



connection.setup(['127.0.0.1'], 'cqlengine', protocol_version=3)

#drop_table(Song)
#drop_table(YouTubeSong)
#drop_table(SoundCloudSong)
#drop_table(Room)

sync_table(Song)
sync_table(YouTubeSong)
sync_table(SoundCloudSong)
sync_table(Room)
