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

import collections
import heapq
import threading
import time
import traceback

Item = collections.namedtuple('Item', 'time func')


class TimedQueue:

  def __init__(self):
    self._queue = []
    self._min = None
    self._running = False
    self._rlock = threading.RLock()
    self._update_timer = threading.Event()

  @property
  def running(self):
    with self._rlock:
      return self._running

  def put(self, seconds_from_now, func):
    t = time.time() + seconds_from_now
    with self._rlock:
      if self._min is None or t < self._min:
        self._min = t
        self._update_timer.set()
      heapq.heappush(self._queue, Item(t, func))

  def start(self, daemon=True):
    with self._rlock:
      if self._running:
        raise RuntimeError('EventQueue is already running.')
      self._running = True
      self._thread = threading.Thread(target=self._run)
      self._thread.daemon = daemon
    self._thread.start()

  def stop(self, join=True):
    with self._rlock:
      self._running = False
      thread = self._thread
    if join:
      thread.join()

  def _run(self):
    while True:
      with self._rlock:
        if not self._running:
          break
        timeout =  self._min - time.time() if self._min else None

      self._update_timer.wait(timeout)

      with self._rlock:
        try:
          if self._queue:
            item = heapq.heappop(self._queue)
            if time.time() - item.time > 1.0e-7:
              # Requeue, as it is not time to trigger this item.
              self.put(time.time() - item.time, item.func)
              continue
        finally:
          self._update_timer.clear()

        if self._queue:
          next_item = heapq.heappop(self._queue)
          self._min = next_item.time
          self.put(next_item.time - time.time(), next_item.func)
        else:
          self._min = None

      try:
        item.func()
      except:
        traceback.print_exc()
