import React from 'react'
import sio from '../sio'

export class QueuedTitle extends React.Component {
  constructor(props) {
    super(props)
  }
  render() {
    let song = this.props.song;
    let icon = 'youtube';
    return <div className="item">
      <i className={"large middle aligned icon " + icon}></i>
      <div className="content">
        <a onClick={() => this.props.handleClick(this.props.song)} className="header">{song.title}</a>
        <div className="description">{song.url}</div>
      </div>
    </div>
  }
}
