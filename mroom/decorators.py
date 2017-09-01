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

import flask
import functools
import json
import traceback
import werkzeug.exceptions


def restify(debug=None):
  """
  Wrapper for view functions that turns the returned object to a JSON
  response. The value returned by the view function must be JSON serializable,
  or a tuple of 1) a JSON serializable, 2) a status-code and optionally 3)
  a message.

  The returned JSON object always has the three keys `status`, `data` and
  `message`. #werkzeug.exceptions.HTTPException#s raised by the view will
  be translated respectively.

  if *status* is specified, that will be the status of the HTTP response
  always. The actual status will then only be contained in the JSON object.
  """

  def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      _debug = flask.current_app.debug if debug is None else debug
      try:
        result = func(*args, **kwargs)
      except werkzeug.exceptions.HTTPException as e:
        data = {"status": e.code, "message": e.description}
      except Exception as e:
        traceback.print_exc()
        if _debug:
          message = str(e)
        else:
          message = 'An internal server error occurred.'
        data = {"status": 500, "message": message}
      else:
        message = None
        if isinstance(result, tuple):
          if len(result) == 3:
            result, status, message = result
          else:
            result, status = result
        else:
          status = 200
        data = {"status": status}
        data['data'] = result
        data['message'] = message
      data.setdefault('data', None)
      data.setdefault('message', None)
      return flask.Response(json.dumps(data), status=data['status'], mimetype='application/json')
    return wrapper
  return decorator
