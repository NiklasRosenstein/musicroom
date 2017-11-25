import React from 'react'
import {Route, withRouter} from 'react-router'
import {Link} from 'react-router-dom'
import {PageHeader} from './PageHeader'
import {PageFooter} from './PageFooter'
import {RoomPage} from './RoomPage'

export class IndexPage extends React.Component {
  render() {
    return <div>
        <PageHeader>
          <div className="ui inverted vertical center aligned segment head">
            <div className="head-container">
              <hr/>
              <form className="ui inverted form" style={{display: 'inline-block'}} id="get-room-form" onSubmit={this.gotoRoom}>
                <div className="inline fields">
                  <div className="field">
                    <h1>Get a Room</h1>
                  </div>
                  <div className="field">
                    <input type="text" name="room-name" placeholder={window.MusicRoom.roomNameSuggestion} size="30" autoFocus/>
                  </div>
                  <div className="field">
                    <button className="ui button" type="submit">Go!</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </PageHeader>
        <PageFooter/>
      </div>
  }
  gotoRoom(event) {
    var roomNameValidate = window.MusicRoom.roomNameValidateRegex
    event.preventDefault()
    var roomName = document.querySelector('form input[name="room-name"]').value
    if (!roomName.match(roomNameValidate)) {
      alert("Invalid room name.")
    }
    else if (roomName) {
      // TODO: Update the router location.
      document.location = "/room/" + roomName
    }
  }
}
