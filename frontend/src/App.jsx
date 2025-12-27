import { useState, useRef } from 'react'

function App() {
  const [activeTab, setActiveTab] = useState('voice')
  const [languages, setLanguages] = useState([
    'English', 'Hindi', 'Bengali', 'Marathi', 'Tamil', 'Telugu',
    'Gujarati', 'Kannada', 'Malayalam', 'Punjabi', 'Urdu', 'Assamese', 'Sanskrit'
  ])
  
  // Voice tab states
  const [voiceSourceLang, setVoiceSourceLang] = useState('English')
  const [voiceTargetLang, setVoiceTargetLang] = useState('Hindi')
  const [isRecording, setIsRecording] = useState(false)
  const [voiceLoading, setVoiceLoading] = useState(false)
  const [voiceResult, setVoiceResult] = useState(null)
  
  // Video tab states
  const [videoSourceLang, setVideoSourceLang] = useState('English')
  const [videoTargetLang, setVideoTargetLang] = useState('Hindi')
  const [videoFile, setVideoFile] = useState(null)
  const [videoLoading, setVideoLoading] = useState(false)
  const [videoResult, setVideoResult] = useState(null)
  
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const videoPreviewRef = useRef(null)

  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await translateAudio(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (error) {
      alert('Microphone access denied: ' + error.message)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const translateAudio = async (audioBlob) => {
    setVoiceLoading(true)
    setVoiceResult(null)

    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')
      formData.append('source_lang', voiceSourceLang)
      formData.append('target_lang', voiceTargetLang)

      const response = await fetch('http://localhost:8000/translate-audio', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Translation failed')
      }

      const data = await response.json()
      setVoiceResult(data)
    } catch (error) {
      alert('Error: ' + error.message)
    } finally {
      setVoiceLoading(false)
    }
  }

  const handleVideoUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setVideoFile(file)
      const url = URL.createObjectURL(file)
      if (videoPreviewRef.current) {
        videoPreviewRef.current.src = url
      }
    }
  }

  const translateVideo = async () => {
    if (!videoFile) {
      alert('Please upload a video first')
      return
    }

    setVideoLoading(true)
    setVideoResult(null)

    try {
      const formData = new FormData()
      formData.append('video', videoFile)
      formData.append('source_lang', videoSourceLang)
      formData.append('target_lang', videoTargetLang)

      const response = await fetch('http://localhost:8000/translate-video', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Translation failed')
      }

      const data = await response.json()
      setVideoResult(data)
    } catch (error) {
      alert('Error: ' + error.message)
    } finally {
      setVideoLoading(false)
    }
  }

  const hexToBase64 = (hex) => {
    const bytes = new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)))
    let binary = ''
    bytes.forEach(byte => binary += String.fromCharCode(byte))
    return btoa(binary)
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-indigo-900 mb-2">
            🌐 Real time Speech to text using STT & TTS
          </h1>
          <p className="text-gray-600">Translate speech and video across Indian languages</p>
        </header>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('voice')}
              className={`flex-1 py-4 px-6 text-center font-semibold transition-colors ${
                activeTab === 'voice'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🎙️ Voice Translation
            </button>
            <button
              onClick={() => setActiveTab('video')}
              className={`flex-1 py-4 px-6 text-center font-semibold transition-colors ${
                activeTab === 'video'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🎥 Video Translation
            </button>
          </div>

          {/* Voice Tab */}
          {activeTab === 'voice' && (
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    From:
                  </label>
                  <select
                    value={voiceSourceLang}
                    onChange={(e) => setVoiceSourceLang(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    {languages.map(lang => (
                      <option key={lang} value={lang}>{lang}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    To:
                  </label>
                  <select
                    value={voiceTargetLang}
                    onChange={(e) => setVoiceTargetLang(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    {languages.map(lang => (
                      <option key={lang} value={lang}>{lang}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="text-center mb-6">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={voiceLoading}
                  className={`px-8 py-4 rounded-lg font-semibold text-white transition-all transform hover:scale-105 ${
                    isRecording
                      ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                      : voiceLoading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-indigo-600 hover:bg-indigo-700'
                  }`}
                >
                  {voiceLoading ? '⏳ Translating...' : isRecording ? '⏹️ Stop & Translate' : '⏺️ Start Recording'}
                </button>
              </div>

              {voiceResult && (
                <div className="space-y-4 bg-gray-50 p-6 rounded-lg">
                  <div className="border-l-4 border-blue-500 pl-4">
                    <h3 className="font-semibold text-gray-700 mb-1">
                      Original ({voiceSourceLang}):
                    </h3>
                    <p className="text-gray-800">{voiceResult.original_text}</p>
                  </div>
                  <div className="border-l-4 border-green-500 pl-4">
                    <h3 className="font-semibold text-gray-700 mb-1">
                      Translated ({voiceTargetLang}):
                    </h3>
                    <p className="text-gray-800">{voiceResult.translated_text}</p>
                  </div>
                  {voiceResult.audio_base64 && (
                    <div className="pt-4">
                      <h3 className="font-semibold text-gray-700 mb-2">🔊 Generated Audio:</h3>
                      <audio
                        controls
                        className="w-full"
                        src={`data:audio/mp3;base64,${hexToBase64(voiceResult.audio_base64)}`}
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Video Tab */}
          {activeTab === 'video' && (
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Video Language:
                  </label>
                  <select
                    value={videoSourceLang}
                    onChange={(e) => setVideoSourceLang(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    {languages.map(lang => (
                      <option key={lang} value={lang}>{lang}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Language:
                  </label>
                  <select
                    value={videoTargetLang}
                    onChange={(e) => setVideoTargetLang(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    {languages.map(lang => (
                      <option key={lang} value={lang}>{lang}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Video:
                </label>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleVideoUpload}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {videoFile && (
                <div className="mb-6">
                  <video
                    ref={videoPreviewRef}
                    controls
                    className="w-full rounded-lg shadow-md"
                  />
                </div>
              )}

              {videoFile && (
                <div className="text-center mb-6">
                  <button
                    onClick={translateVideo}
                    disabled={videoLoading}
                    className={`px-8 py-4 rounded-lg font-semibold text-white transition-all transform hover:scale-105 ${
                      videoLoading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-indigo-600 hover:bg-indigo-700'
                    }`}
                  >
                    {videoLoading ? '⏳ Processing...' : '🚀 Start Translation'}
                  </button>
                </div>
              )}

              {videoResult && (
                <div className="space-y-4 bg-gray-50 p-6 rounded-lg">
                  <div className="border-l-4 border-blue-500 pl-4">
                    <h3 className="font-semibold text-gray-700 mb-1">
                      Original ({videoSourceLang}):
                    </h3>
                    <p className="text-gray-800">{videoResult.original_text}</p>
                  </div>
                  <div className="border-l-4 border-green-500 pl-4">
                    <h3 className="font-semibold text-gray-700 mb-1">
                      Translated ({videoTargetLang}):
                    </h3>
                    <p className="text-gray-800">{videoResult.translated_text}</p>
                  </div>
                  {videoResult.audio_base64 && (
                    <div className="pt-4">
                      <h3 className="font-semibold text-gray-700 mb-2">🔊 Generated Audio:</h3>
                      <audio
                        controls
                        className="w-full"
                        src={`data:audio/mp3;base64,${hexToBase64(videoResult.audio_base64)}`}
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
