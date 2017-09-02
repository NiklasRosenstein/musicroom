# Music Room

A web application to listen to music together with your friends. Choose your
favorite room name by choosing the appropriate URL (eg. `/room/my-room`) and
share the link with your friends. Everyone that joins the room can add songs
to the queue.

## Screenshots

<img height="100px" src="https://i.imgur.com/fYzsesE.png" alt="screenshot">

## Technology

* [CPython 3.6](https://www.python.org/)
  * [Node.py](https://nodepy.org/)
  * [Flask](http://flask.pocoo.org/)
  * [PonyORM](https://python-orm.com/)
* [PostgreSQL](https://www.postgresql.org/)
* JavaScript
  * [YouTube Player API](https://developers.google.com/youtube/v3/docs/videos/list)
  * [SoundCloud HTML5 Widget API](https://developers.soundcloud.com/docs/api/html5-widget#methods)
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
