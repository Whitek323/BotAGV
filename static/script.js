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

    setTimeout(() => { if (recorder.state === 'recording') recorder.stop(); }, 4000);
    await stopped;
    stream.getTracks().forEach((t) => t.stop());

    const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
    const file = new File([blob], 'speech.webm', { type: blob.type });

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
      textInput.value = text;
      await sendToAI(text);
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

    const { response: answer, res_id } = await res.json();
    textResponse.textContent = answer || '';

    if (voiceToggle?.checked) {
      playIntentAudio(res_id);
    }
  } catch (err) {
    textResponse.textContent = String(err);
  }
}

function playIntentAudio(resId) {
  audioContainer.innerHTML = '';
  const audio = document.createElement('audio');
  audio.controls = true;

  const fallback = ENDPOINT + '/static/sound/sys/unknown1.wav';
  let primary;


  if (resId === -1 || resId === '-1' || resId === null || resId === undefined || resId === '') {
    primary = null;
  } else {
    primary = ENDPOINT + `/static/sound/intent/${resId}.wav`;
  }

  // ใส่ cache-busting
  const bust = () => `?t=${Date.now()}`;

  audio.onerror = () => {
    // ถ้าเสียง intent โหลดไม่ได้ ให้สลับไปเสียง unknown
    if (audio.src.includes('/sound/intent/')) {
      audio.onerror = null; 
      audio.src = fallback + bust();
      audio.play().catch(() => {});
    }
  };

  audio.src = (primary || fallback) + bust();
  audioContainer.appendChild(audio);

  audio.play().catch(() => {});
}
