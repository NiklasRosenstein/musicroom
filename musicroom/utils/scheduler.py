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

Event = collections.namedtuple('Event', 'time func key')


class Scheduler:
  """
  An efficient priority queue for scheduling events at fixed points in time.
  Events can be associated with a key that will be unique in the whole queue.
  """

  def __init__(self):
    self._queue = []
    self._min = None
    self._running = False
    self._rlock = threading.RLock()
    self._update_timer = threading.Event()
    self._item_processed = threading.Event()

  @property
  def is_running(self):
    """
    True if the scheduler thread is currently running. Use the #stop() method
    to instantly stop the thread.
    """

    with self._rlock:
      return self._running

  def put(self, seconds, func, key=None):
    """
    Put an item on the priority queue to be run the specified number of
    *seconds* from the current point in time.

    # Parameters
    seconds (float): The number of seconds from now to kick off *func*.
    func (callable): The function to call when *seconds* has passed.
    key (any): A key associated with the event. If an event with that
      key is already in the queue, the old will be removed.
    """

    t = time.time() + seconds
    with self._rlock:
      if key is not None:
        prev_len = len(self._queue)
        self._queue = [event for event in self._queue if event.key != key]
        if prev_len != len(self._queue) and self._queue:
          # Length changed, update min-time.
          self._min = heapq.nsmallest(1, self._queue)[0].time
      if self._min is None or t < self._min:
        self._min = t
        self._update_timer.set()
      heapq.heappush(self._queue, Event(t, func, key))

  def remove(self, key):
    """
    Remove an event from the priority queue with the specified *key*. Returns
    the #Event that was removed, or #None if no such event existed in the
    queue.
    """

    result = None
    with self._rlock:
      queue = self._queue
      offset = 0
      for index in range(len(self._queue)):
        event = queue[index - offset]
        if event.key == key:
          del queue[index - offset]
          result = event
          offset += 1

    return result

  def start(self, daemon=True):
    """
    Start the thread that processes the events. Can not be used when the
    thread is already started.
    """

    with self._rlock:
      if self._running:
        raise RuntimeError('already started')
      self._running = True
      self._thread = threading.Thread(target=self._run)
      self._thread.daemon = daemon
    self._thread.start()

  def stop(self, join=True):
    """
    Stops the thread immediately. Does nothing if the thread is not running.
    Note that if an event is currently executed, the thread can only be
    stopped after the event finished.
    """

    with self._rlock:
      self._running = False
      thread = self._thread
      self._update_timer.set()

    if join:
      thread.join()

  def wait(self, timeout=None):
    """
    Wait until the queue is empty.
    """

    tstart = time.time()
    while True:
      with self._rlock:
        if not self._thread or not self._thread.is_alive():
          break
        if not self._queue:
          break
        if timeout is None:
          remainder = None
        else:
          remainder = timeout - (time.time() - tstart)
      self._item_processed.wait(remainder)

  def _run(self):
    while True:
      with self._rlock:
        if not self._running:
          break
        timeout = self._min - time.time() if self._min else None
        m = self._min

      self._update_timer.wait(timeout)

      with self._rlock:
        if not self._running:
          break
        try:
          if self._queue:
            event = heapq.heappop(self._queue)
            delta = event.time - time.time()
            if delta > 1.0e-7:
              # Requeue, as it is not time to trigger this item.
              self.put(delta, event.func, event.key)
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
        event.func()
      except:
        traceback.print_exc()
      finally:
        self._item_processed.set()
        self._item_processed.clear()
