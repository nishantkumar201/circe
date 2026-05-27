const record = document.getElementById('record-btn')
let recording = false

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  console.log('getUserMedia supported.')

  navigator.mediaDevices
    .getUserMedia({ audio: true, video: false })
    .then(stream => {
      const mediaRecorder = new MediaRecorder(stream)

      record.onclick = () => {
        if (recording == false) {
          recording = startRecording(mediaRecorder)
        } else {
          recording = stopRecording(mediaRecorder)
        }
      }
    })
    .catch(err => console.log('getUserMedia error:', err))
} else {
  console.log('getUserMedia not supported.')
}

function startRecording(mediaRecorder) {
  mediaRecorder.start()
  console.log('Recording...')
  record.classList.add('recording')
  return true
}

function stopRecording(mediaRecorder) {
  mediaRecorder.stop()
  console.log('Recording stopped.')
  record.classList.remove('recording')
  return false
}