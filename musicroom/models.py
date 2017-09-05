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
from datetime import datetime, timedelta
import conf from '../conf'

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

  @property
  def song_time_passed(self):
    return datetime.now() - self.song_starttime

  def add_song(self, song):
    if song in self.queue:
      return False
    else:
      self.queue.add(song)
      return True

  def skip_song(self):
    """
    Skips the current song.
    """

    song = room.queue.select().first()
    if song:
      self.history.add(song)
      self.queue.remove(song)
      commit()

    self.song = song
    self.song_starttime = datetime.now() if song else None

  def update_song(self):
    """
    Validates the song that is currently being played in the room. If the
    #song has ended by now, #song and #song_starttime will be updated. Both
    will be set to #None if the queue is empty.

    Returns a tuple of the current song and the number of seconds passed
    since the song started. If there is not current song, both will be #None.
    """

    now = datetime.now()
    song = self.song

    # Check if this song has already stopped. Also consume as many items
    # as necessary to find the song that is currently playing.
    if song and self.song_starttime is not None:
      time_passed = now - self.song_starttime
      while song:
        current_duration = timedelta(seconds=song.duration)
        if time_passed < current_duration:
          break

        # Discard this song into the rooms history.
        time_passed -= current_duration + timedelta(seconds=conf.seconds_between_songs)
        self.history.add(song)
        song = self.queue.select().first()
        if song:
          self.queue.remove(song)

      if not song:
        time_passed = None
    else:
      time_passed = None

    # Get the next song from the queue.
    if song is None:
      song = self.queue.select().first()
      if song:
        self.queue.remove(song)
        time_passed = timedelta(seconds=0)

    # We should never end up with a song but no time since it started
    # playing, or the other way round.
    assert bool(song) == (time_passed is not None)

    self.song = song
    self.song_starttime = now - time_passed if time_passed is not None else None

    return song, time_passed


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
    return 'https://youtu.be/' + self.video_id


db.bind(**conf.database)
db.generate_mapping(create_tables=True)
