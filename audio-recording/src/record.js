// Shim for Safari.
window.AudioContext = window.AudioContext || window.webkitAudioContext;

function audioBufferToWav(buffer, opt) {
  opt = opt || {};
  var numChannels = buffer.numberOfChannels;
  var sampleRate = buffer.sampleRate;
  var format = opt.float32 ? 3 : 1;
  var bitDepth = format === 3 ? 32 : 16;
  var result;
  if (numChannels === 2) {
    result = interleave(buffer.getChannelData(0), buffer.getChannelData(1));
  } else {
    result = buffer.getChannelData(0);
  }
  return encodeWAV(result, format, sampleRate, numChannels, bitDepth);
}

function encodeWAV(samples, format, sampleRate, numChannels, bitDepth) {
  var bytesPerSample = bitDepth / 8;
  var blockAlign = numChannels * bytesPerSample;
  var buffer = new ArrayBuffer(44 + samples.length * bytesPerSample);
  var view = new DataView(buffer);
  /* RIFF identifier */
  writeString(view, 0, "RIFF");
  /* RIFF chunk length */
  view.setUint32(4, 36 + samples.length * bytesPerSample, true);
  /* RIFF type */
  writeString(view, 8, "WAVE");
  /* format chunk identifier */
  writeString(view, 12, "fmt ");
  /* format chunk length */
  view.setUint32(16, 16, true);
  /* sample format (raw) */
  view.setUint16(20, format, true);
  /* channel count */
  view.setUint16(22, numChannels, true);
  /* sample rate */
  view.setUint32(24, sampleRate, true);
  /* byte rate (sample rate * block align) */
  view.setUint32(28, sampleRate * blockAlign, true);
  /* block align (channel count * bytes per sample) */
  view.setUint16(32, blockAlign, true);
  /* bits per sample */
  view.setUint16(34, bitDepth, true);
  /* data chunk identifier */
  writeString(view, 36, "data");
  /* data chunk length */
  view.setUint32(40, samples.length * bytesPerSample, true);
  if (format === 1) {
    // Raw PCM
    floatTo16BitPCM(view, 44, samples);
  } else {
    writeFloat32(view, 44, samples);
  }
  return buffer;
}

function interleave(inputL, inputR) {
  var length = inputL.length + inputR.length;
  var result = new Float32Array(length);
  var index = 0;
  var inputIndex = 0;
  while (index < length) {
    result[index++] = inputL[inputIndex];
    result[index++] = inputR[inputIndex];
    inputIndex++;
  }
  return result;
}

function writeFloat32(output, offset, input) {
  for (var i = 0; i < input.length; i++, offset += 4) {
    output.setFloat32(offset, input[i], true);
  }
}

function floatTo16BitPCM(output, offset, input) {
  for (var i = 0; i < input.length; i++, offset += 2) {
    var s = Math.max(-1, Math.min(1, input[i]));
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
}

function writeString(view, offset, string) {
  for (var i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

// Safari does not support promise-based decodeAudioData, need to use callback instead.
const decodeAudioData = (buffer) =>
  new Promise((res, rej) => {
    new AudioContext().decodeAudioData(buffer, res, rej);
  });

const startRecording = async () => {
  const data = [];
  // Ask for mic permissions.
  const stream = await navigator.mediaDevices.getUserMedia({
    video: false,
    audio: true,
  });
  window.stream = stream;
  // Use polyfill for older browsers.
  if (!window.MediaRecorder) {
    window.MediaRecorder = OpusMediaRecorder;
    window.recorder = new MediaRecorder(
      stream,
      {},
      {
        OggOpusEncoderWasmPath:
          "https://cdn.jsdelivr.net/npm/opus-media-recorder@latest/OggOpusEncoder.wasm",
        WebMOpusEncoderWasmPath:
          "https://cdn.jsdelivr.net/npm/opus-media-recorder@latest/WebMOpusEncoder.wasm",
      }
    );
  } else window.recorder = new MediaRecorder(stream);
  // Handle incoming data.
  window.recorder.ondataavailable = (e) => data.push(e.data);
  window.recorder.start();
  window.recorder.onerror = (e) => {
    throw e.error || new Error(e.name);
  };
  window.recorder.onstop = async (e) => {
    const blob = new Blob(data);
    const fetchedBlob = await fetch(URL.createObjectURL(blob));
    const arrayBuffer = await fetchedBlob.arrayBuffer();
    // Convert to wav format.
    const wav = audioBufferToWav(await decodeAudioData(arrayBuffer));
    const formData = new FormData();
    formData.append(
      "files",
      new Blob([wav], { type: "audio/wave" }),
      "sound.wav"
    );
    // Send the audio file to Wave server.
    const res = await fetch(wave.uploadURL, { method: "POST", body: formData });
    const { files } = await res.json();
    // Emit event (q.events.audio.captured) with a URL of the audio file at Wave server.
    window.wave.emit("audio", "captured", files[0]);
  };
};

const stopRecording = () => {
  window.recorder.stop();
  window.stream.getTracks().forEach((track) => track.stop());
};
