
from pony.orm import db_session
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=('run', 'build', 'db'))
parser.add_argument('--production', action='store_true')
parser.add_argument('--development', action='store_true')
parser.add_argument('--drop-all', action='store_true')
parser.add_argument('--update-song-metadata', action='store_true')


def main():
  args = parser.parse_args()
  sys.path.append('.')

  import conf
  if args.production:
    conf.debug = False
  elif args.development:
    conf.debug = True

  globals()[args.command](args)


def run(args):
  import conf
  from .app import app, sio, init as init_app
  init_app()
  sio.run(app, host=conf.host, port=conf.port, debug=conf.debug)


def build(args):
  import subprocess as sh
  sh.run(['npx', 'webpack'], cwd='web')


def db(args):
  from . import models
  from .models import db
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



if __name__ == '__main__':
  sys.exit(main())
