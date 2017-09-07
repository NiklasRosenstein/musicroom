
from pony.orm import db_session
import argparse
import models, {db} from './models'
import {queue, app, sio, update_room} from './app'
import conf from '../conf'

app.config['SECRET_KEY'] = conf.secret_key

parser = argparse.ArgumentParser()
parser.add_argument('--drop-all', action='store_true')


def main():
  args = parser.parse_args()
  if args.drop_all:
    print('Aye, sir! Dropping all our data out tha window!')
    db.drop_all_tables(with_all_data=True)
    return

  # Queue all current songs in all rooms.
  with db_session():
    for room in models.Room.select():
      update_room(room)

  queue.start(daemon=True)
  sio.run(app, host=conf.host, port=conf.port, debug=conf.debug)


if require.main == module:
  main()
