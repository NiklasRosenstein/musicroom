## Music Room

  [Node.py]: https://nodepy.org/
  [Flask]: http://flask.pocoo.org/
  [React]: https://reactjs.org/

A [Node.py] + [Flask] + [React] application to collaborate on the YouTube
playlist. Inspired by https://plug.dj/.

<p align="center">
  <img height="400px" src="https://i.imgur.com/MfHd3gc.png" alt="screenshot">
</p>

### Bundle & Run

    $ cd web/ && yarn install && yarn run webpack && cd ..
    $ cp conf.template.py conf.py && $EDITOR conf.py
    $ pip install nodepy-runtime && nodepy https://nodepy.org/install-pm.py
    $ nodepy-pm install && nodepy .

### Get a Google YouTube API Key

  [1]: https://console.developers.google.com
  [2]: https://console.developers.google.com/apis/credential
  [3]: https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=1071764734035

1. Create a project in the [Google Developer Console][1]
2. Enable the YouTube Data API [here][3]
3. Create an API key in your project's [Credentials Page][2]
4. Paste the API key into `conf.py`

### For the future

* Keep order in the queue and history (currently implemented as a Pony ORM `Set`)
* Also, allow duplicates in the room history
* Ability to remove songs, and to move them up//down in the queue
* Automatically start playing the next song (broken since switch to React)
