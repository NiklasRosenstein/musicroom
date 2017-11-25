import React from 'react'
import YouTube from 'react-youtube'
import {PageHeader} from './PageHeader'
import {PageFooter} from './PageFooter'
import {QueuedTitle} from './QueuedTitle'
import {SongSubmitForm} from './SongSubmitForm'
import sio from '../sio'

export class RoomPage extends React.Component {
  // props: youtubePlayer -- <YouTube/> component from render()
  constructor(props) {
    super(props)
    this.state = {song: null, queue: [], history: []}
    this.handleCurrentSong = this.handleCurrentSong.bind(this)
    this.handleQueue = this.handleQueue.bind(this)
    this.handleSkipSong = this.handleSkipSong.bind(this)
    this.handlePlayerReader = this.handlePlayerReader.bind(this)
    this.handleSongQueued = this.handleSongQueued.bind(this)
    this.handleQueueClick = this.handleQueueClick.bind(this)
  }
  getRoomName() {
    return this.props.match.params.name
  }
  handleCurrentSong(song) {
    console.log('handleCurrentSong:', song)
    if (song && this.state.song && song.id == this.state.song.id) {
      console.log('Skip same song.')
      return
    }
    else if (!song && !this.state.song) {
      console.log('Skip null song.')
      return
    }
    this.setState(state => {
      console.log('Song state updated')
      state.song = song
      return state
    })
  }
  handleQueue(data) {
    this.setState(state => {
      state.queue = data.queue
      state.history = data.history
      console.log('queue:', data.queue)
      console.log('history:', data.history)
      return state
    })
  }
  handlePlayerReader() {
    if (this.state.song) {
      this.youtubePlayer.internalPlayer.seekTo(this.state.song.time_passed)
    }
  }
  handleSongQueued(data) {
    if (!data.song) return  // eq when the song in the queue already exists
    this.setState(state => {
      state.queue.push(data.song)
      return state
    })
  }
  handleQueueClick(song) {
    sio.submitSong(song.url, this.handleSongQueued)
  }
  handleSkipSong() {
    sio.skipSong()
  }

  componentDidMount() {
    sio.connect(this.getRoomName(), () => {
      sio.getCurrentSong(this.handleCurrentSong)
      sio.getQueueAndHistory(this.handleQueue)
    })
  }

  render() {
    let name = this.getRoomName()
    let song = this.state.song
    let opts = {width: 640, height: 390, playerVars: {autoplay: 1}}
    console.log('queue:', this.state.queue)
    console.log('history:', this.state.history)
    return <div>
      <PageHeader>
        <hr/>
        <div className="ui player">
          <div className="fifteen wide column">
            <h2 className="current-title" style={{display: song? '': 'none'}}>
              {song? song.title: ''}
            </h2>
            <YouTube id="yt-player" opts={opts} videoId={song?song.video_id:null}
                ref={x => this.youtubePlayer = x} onReady={this.handlePlayerReader}/>
          </div>
        </div>
        <div className="ui text container">
          <a style={{color: 'white', fontSize: '150%'}} href='#' onClick={this.handleSkipSong}>
            <i className="lerge forward icon"></i>
          </a>
        </div>
      </PageHeader>

      <div className="ui vertical aligned segment head">
        <SongSubmitForm className="head-container" roomName={name} onSongQueued={this.handleSongQueued}/>
      </div>

      <div className="ui inverted vertical aligned segment head">
        <div className="head-container">
          <hr/>
          <div className="ui grid">
            <div className="row">
              <div className="eight wide column">
                <h1>Queue</h1>
                <div className="ui inverted relaxed divided list" id="queue">
                  {this.state.queue.map(song => {
                    return <QueuedTitle song={song} key={song.id} handleClick={this.handleQueueClick}/>
                  })}
                </div>
              </div>
              <div className="eight wide column">
                <h1>History</h1>
                <div className="ui inverted relaxed divided list" id="history">
                  {this.state.history.map(song => {
                    return <QueuedTitle song={song} key={song.id} handleClick={this.handleQueueClick}/>
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <PageFooter/>
    </div>
  }
}
