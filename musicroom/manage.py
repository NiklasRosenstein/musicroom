
import argparse
import {db} from './models'
import {app, sio} from './app'
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

  sio.run(app, host=conf.host, port=conf.port, debug=conf.debug)
  return

  #werkzeug.serving.run_simple(conf.host, conf.port, wsgi,
  #  use_reloader=conf.debug, use_debugger=conf.debug)
  eventlet.wsgi.server(eventlet.listen((conf.host, conf.port)), wsgi)


if require.main == module:
  main()
