
from pony.orm import db_session
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--production', action='store_true')
parser.add_argument('--development', action='store_true')
parser.add_argument('--drop-all', action='store_true')
parser.add_argument('--update-song-metadata', action='store_true')


def main():
  args = parser.parse_args()

  import conf from '../conf'
  if args.production:
    conf.debug = False
  elif args.development:
    conf.debug = True

  import models, {db} from './models'
  import {app, sio, init as init_app} from './app'

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

  init_app()
  sio.run(app, host=conf.host, port=conf.port, debug=conf.debug)


if require.main == module:
  main()
