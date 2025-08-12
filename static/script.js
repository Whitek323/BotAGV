const ENDPOINT = 'http://localhost:5000';

const $ = (id) => document.getElementById(id);
const mainForm = $('mainForm');
const textInput = $('textInput');
const textResponse = $('textResponse');
const voiceToggle = $('voiceToggle');
const micBtn = $('micBtn');

let audioContainer = $('audioContainer');
if (!audioContainer) {
  audioContainer = document.createElement('div');
  audioContainer.id = 'audioContainer';
  (textResponse || document.body).insertAdjacentElement('afterend', audioContainer);
}

mainForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  await sendToAI(textInput.value);
});

micBtn?.addEventListener('click', async () => {
  // lock UI
  const original = micBtn.textContent;
  micBtn.disabled = true;
  micBtn.textContent = '...';
  textResponse.textContent = '';
  audioContainer.innerHTML = '';

  let stream, recorder;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const preferMime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : undefined;
    recorder = new MediaRecorder(stream, preferMime ? { mimeType: preferMime } : undefined);

    const chunks = [];
    recorder.ondataavailable = (e) => e.data?.size && chunks.push(e.data);
    const stopped = new Promise((resolve) => (recorder.onstop = resolve));
    recorder.start();

    // อัด 4 วินาที
    setTimeout(() => {
      if (recorder.state === 'recording') recorder.stop();
    }, 4000);

    await stopped;
    stream.getTracks().forEach((t) => t.stop());

    // รวมไฟล์เสียง
    const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
    const file = new File([blob], 'speech.webm', { type: blob.type });

    // ส่งไป /stt
    const fd = new FormData();
    fd.append('audio', file);
    fd.append('language', 'th-TH');

    const sttRes = await fetch(ENDPOINT + '/stt', { method: 'POST', body: fd });
    if (!sttRes.ok) throw new Error(`STT ${sttRes.status} ${sttRes.statusText}`);
    const sttJson = await sttRes.json();
    const text = (sttJson && sttJson.text ? String(sttJson.text) : '').trim();

    if (!text) {
      textResponse.textContent = sttJson?.error ? `ไม่เข้าใจเสียง: ${sttJson.error}` : 'ไม่พบคำพูด';
    } else {
      textInput.value = text;       // โชว์ข้อความที่ถอดเสียงได้
      await sendToAI(text);         // ยิงต่อไป /ai
    }
  } catch (err) {
    textResponse.textContent = String(err);
  } finally {
    micBtn.textContent = original;
    micBtn.disabled = false;
  }
});

async function sendToAI(sentence) {
  const s = (sentence || '').trim();
  if (!s) return;
  textResponse.textContent = '...';
  audioContainer.innerHTML = '';

  try {
    const res = await fetch(ENDPOINT + '/ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sentence: s })
    });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);

    const { response: answer } = await res.json();
    textResponse.textContent = answer || '';

    if (voiceToggle?.checked && answer) {
      const ttsRes = await fetch(ENDPOINT + '/speak_answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer })
      });
      if (!ttsRes.ok) throw new Error(`TTS ${ttsRes.status} ${ttsRes.statusText}`);

      const { audio_url } = await ttsRes.json();
      const src = (audio_url || '/static/response.mp3') + `?t=${Date.now()}`; // กัน cache
      const audio = document.createElement('audio');
      audio.controls = true;
      audio.src = src;
      audioContainer.appendChild(audio);
      // auto-play (ถ้าต้องการ): audio.play().catch(()=>{});
    }
  } catch (err) {
    textResponse.textContent = String(err);
  }
}

