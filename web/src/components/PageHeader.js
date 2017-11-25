import React from 'react'
import {Link} from 'react-router-dom'

export class PageHeader extends React.Component {
  render() {
    let children = React.Children.toArray(this.props.children)
    let inner = children.filter(x => x.props.loc == 'inner')
    let outter = children.filter(x => x.props.loc != 'inner')
    return <div className="ui inverted vertical center aligned segment head">
      <div className="head-container">
        <div className="ui text container">
          {inner.length > 0 ? inner : <div>
            <h1 className="ui inverted header">
              <Link to="/" style={{color: 'inherit'}}>Music Room</Link>
            </h1>
            <h3>Listen to music together with your friends.</h3>
          </div>}
        </div>
        {outter}
      </div>
    </div>
  }
}
