import React from 'react'
import sio from '../sio'

export class SongSubmitForm extends React.Component {
  constructor(props) {
    super(props)
    this.state = {value: '', error: null, song: null}
    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
  }
  render() {
    let name = this.props.roomName
    let hasMessage = this.state.error || this.state.song
    return <div className={this.props.className}>
      <h1>Add a Song</h1>
      {hasMessage &&
        <div className={"ui message " + (this.state.error? 'negative': 'positive')}>
          <p>{this.state.error || ('Added: ' + this.state.song.title)}</p>
        </div>
      }
      <form className="ui form" id="add-song-form" method="post" action="/api/submit" onSubmit={this.handleSubmit}>
        <div className="field">
          <label>YouTube URL</label>
          <input type="text" name="url" placeholder="https://www.youtube.com/watch?v=e8T_fzSY34s"
              autoFocus value={this.state.value} onChange={this.handleChange}/>
        </div>
        <input type="text" name="room" hidden value={name} readOnly/>
        <button className="ui button" type="submit">Submit</button>
      </form>
    </div>
  }
  handleSubmit(event) {
    event.preventDefault()
    sio.submitSong(this.state.value, data => {
      console.log('Response after put song:', data)
      if (this.props.onSongQueued) {
        this.props.onSongQueued(data)
      }
      this.setState(state => {
        state.error = data.error
        state.song = data.song
        return state
      })
    })
  }
  handleChange(event) {
    let value = event.target.value
    this.setState(state => {
      state.value = value
      return state
    })
  }
}
