import React from 'react'
import ReactDOM from 'react-dom'
import {BrowserRouter} from 'react-router-dom'
import {IndexRoute, Route} from 'react-router'
import {IndexPage} from './components/IndexPage'
import {RoomPage} from './components/RoomPage'

import 'semantic-ui-css/semantic.min.css'
import './style.css'

ReactDOM.render(
  <BrowserRouter>
    <div>
      <Route exact path="/" component={IndexPage}/>
      <Route path="/room/:name" component={RoomPage}/>
    </div>
  </BrowserRouter>,
  document.getElementById('container')
)
