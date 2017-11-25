import socketio from 'socket.io-client'

let socket = socketio()
let roomName = null

/* Emits a S.IO event, passing the currently configured #roomName
 * as first argument, followed by any additional arguments passed
 * to this function. */
function emit(event) {
  if (roomName == null) {
    console.warn('sio.roomName is not initialized.')
    return
  }
  let remainders = Array.from(arguments).slice(1)
  console.log('emit(', roomName, ...remainders, ')')
  socket.emit(event, roomName, ...remainders)
}

function connect(_roomName, connected) {
  roomName = _roomName
  emit('join')
  socket.once('joined', connected)
}

function getCurrentSong(callback) {
  emit('get current song')
  socket.once('current song', callback)
}

function getQueueAndHistory(callback) {
  emit('get queue and history')
  socket.once('queue and history', callback)
}

function submitSong(url, callback) {
  emit('put song', url)
  socket.once('put song', callback)
}

function skipSong() {
  emit('skip song')
}

export default {
  connect,
  getCurrentSong,
  getQueueAndHistory,
  submitSong
}
