# Music Room

Listen to music together with your friends. Collaborate on the playlist that
you all want to enjoy.

## Screenshots

<p align="center">
  <img height="400px" src="https://i.imgur.com/MfHd3gc.png" alt="screenshot">
</p>

## Todo

* Keep order in the queue and history (currently implemented as a Pony ORM `Set`)
* Also, allow duplicates in the room history
* Ability to remove songs, and to move them up//down in the queue

## Technology

* [CPython 3.6](https://www.python.org/)
  * [Node.py](https://nodepy.org/)
  * [Flask](http://flask.pocoo.org/)
  * [PonyORM](https://python-orm.com/)
* [PostgreSQL](https://www.postgresql.org/)
* JavaScript
  * [YouTube Player API](https://developers.google.com/youtube/v3/docs/videos/list)
  * [jQuery](https://jquery.com/)
  * [d3](https://d3js.org/)
  * [Handlebars](http://handlebarsjs.com/)
* Css
  * [Semantic UI](https://semantic-ui.com/download)

## Configuration

### Google API Key (YouTube)

  [1]: https://console.developers.google.com
  [2]: https://console.developers.google.com/apis/credential
  [3]: https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=1071764734035

1. Create a project in the [Google Developer Console][1]
2. Enable the YouTube Data API [here][3]
3. Create an API key in your project's [Credentials Page][2]
4. Paste the API key into `conf.json` under `"auth.google.apiKey"`
