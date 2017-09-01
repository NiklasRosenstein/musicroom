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
# OUT OF OR IN CONN

import re
import requests
import conf from '../conf.json'

API_KEY = conf['auth']['google']['apiKey']


def video(video_id, parts=['snippet', 'contentDetails']):
  params = {'key': API_KEY, 'part': ','.join(parts), 'id': video_id}
  resp = requests.get('https://www.googleapis.com/youtube/v3/videos',
    params=params)
  resp.raise_for_status()
  data = resp.json()
  if len(data['items']) != 1:
    raise ValueError('invalid YouTube Video ID: {!r}'.format(video_id))
  return data['items'][0]


def parse_duration(duration):
  """
  Parses content duration as described here:
  https://developers.google.com/youtube/v3/docs/videos#contentDetails.duration
  """

  match = re.match('P(\d+D)?T(\d+H)?(\d+M)?(\d+S)', duration)
  if not match:
    raise ValueError('invalid duration: {!r}'.format(duration))
  days, hours, minutes, seconds = [int(x[:-1]) if x else 0 for x in match.groups()]
  return seconds + minutes * 60 + hours * 3600 + hours * 86400
