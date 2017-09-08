
from pony.orm import db_session
import argparse
import models, {db} from './models'
import {app, sio} from './app'
import conf from '../conf'

app.config['SECRET_KEY'] = conf.secret_key

parser = argparse.ArgumentParser()
parser.add_argument('--drop-all', action='store_true')
parser.add_argument('--update-song-metadata', action='store_true')


def main():
  args = parser.parse_args()
  if args.drop_all:
    print('Aye, sir! Dropping all our data out tha window!')
    db.drop_all_tables(with_all_data=True)
    return
  if args.update_song_metadata:
    with db_session():
      songs = models.Song.select()
      num_songs = len(songs)
      for index, song in enumerate(songs):
        print('\r{}/{}'.format(index, num_songs), end='')
        if isinstance(song, models.YtSong):
          models.YtSong.from_video_id(song.video_id)
        else:
          ... # TODO
      print()
      return

  # Queue all current songs in all rooms.
  with db_session():
    for room in models.Room.select():
      room.update_song()
      room.add_to_schedule()

  # TODO: Don't start queue in the main reloader process.
  models.room_update_schedule.start(daemon=True)
  sio.run(app, host=conf.host, port=conf.port, debug=conf.debug)


if require.main == module:
  main()
