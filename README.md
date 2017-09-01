# Music Room

A web application to listen to music together with your friends. Choose your
favorite room name by choosing the appropriate URL (eg. `/room/my-room`) and
share the link with your friends. Everyone that joins the room can add songs
to the queue.

## Screenshots

<img height="100px" src="https://i.imgur.com/fYzsesE.png" alt="screenshot">

## Technology

  [Node.py]: https://nodepy.org/

* Python + [Node.py] with Flask
* Apache Cassandra
* JavaScript with YouTube API, SoundCloud API, jQuery, d3
* SemanticUI

## Configuration

### Google API Key (YouTube)

  [1]: https://console.developers.google.com
  [2]: https://console.developers.google.com/apis/credential
  [3]: https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=1071764734035

1. Create a project in the [Google Developer Console][1]
2. Enable the YouTube Data API [here][3]
3. Create an API key in your project's [Credentials Page][2]
4. Paste the API key into `conf.json` under `"auth.google.apiKey"`
