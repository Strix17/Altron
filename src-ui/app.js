/**
 * ALTRON // FRONTEND APP CONTROLLER & BRIDGE CLIENT
 */

class AltronUIController {
  constructor() {
    this.ws = null;
    this.initElements();
    this.initEvents();
    this.initUptimeTimer();
    this.connectBridge();
  }

  initElements() {
    this.cmdInput = document.getElementById('cmd-input');
    this.btnSend = document.getElementById('btn-send');
    this.btnMic = document.getElementById('btn-mic');
    this.telemetryLog = document.getElementById('telemetry-log');
    this.chatStream = document.getElementById('chat-stream');
    this.statusBadge = document.getElementById('status-badge');
    this.statusText = document.getElementById('status-text');
    this.uptimeEl = document.getElementById('sys-uptime');
  }

  initEvents() {
    this.btnSend.addEventListener('click', () => this.submitInput());
    this.cmdInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.submitInput();
    });
    this.btnMic.addEventListener('click', () => this.triggerMic());
  }

  initUptimeTimer() {
    const startTime = Date.now();
    setInterval(() => {
      const diff = Math.floor((Date.now() - startTime) / 1000);
      const hrs = String(Math.floor(diff / 3600)).padStart(2, '0');
      const mins = String(Math.floor((diff % 3600) / 60)).padStart(2, '0');
      const secs = String(diff % 60).padStart(2, '0');
      if (this.uptimeEl) {
        this.uptimeEl.textContent = `${hrs}:${mins}:${secs}`;
      }
    }, 1000);
  }

  connectBridge() {
    const wsUrl = 'ws://127.0.0.1:8765';
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.addTelemetry('[BRIDGE] Connected to Altron Python Engine.', 'sys');
        this.setStatus('ONLINE');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleServerMessage(data);
        } catch (e) {
          console.error('Failed to parse bridge event:', e);
        }
      };

      this.ws.onclose = () => {
        this.setStatus('OFFLINE');
        // Auto reconnect attempt
        setTimeout(() => this.connectBridge(), 3000);
      };

      this.ws.onerror = () => {
        this.setStatus('CONNECTING...');
      };
    } catch (err) {
      console.warn('Bridge not reachable yet:', err);
    }
  }

  handleServerMessage(msg) {
    switch (msg.type) {
      case 'status':
        this.setStatus(msg.payload);
        if (window.jarvisCore) {
          window.jarvisCore.setState(msg.payload);
        }
        break;

      case 'chat':
        this.addChat(msg.speaker, msg.text);
        break;

      case 'log':
        this.addTelemetry(msg.text, msg.success ? 'sys' : 'err');
        break;
    }
  }

  submitInput() {
    const text = this.cmdInput.value.trim();
    if (!text) return;

    this.addChat('YOU', text);
    this.cmdInput.value = '';

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'submit_text', text }));
    }
  }

  triggerMic() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      if (this.isListeningWebSpeech) {
        if (this.recognition) this.recognition.stop();
        return;
      }

      try {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;

        this.recognition.onstart = () => {
          this.isListeningWebSpeech = true;
          this.btnMic.classList.add('listening');
          this.setStatus('LISTENING...');
          this.addTelemetry('Microphone active. Speak your command now.', 'sys');
        };

        this.recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          if (transcript) {
            this.addTelemetry(`Voice transcript: "${transcript}"`, 'sys');
            this.cmdInput.value = transcript;
            this.submitInput();
          }
        };

        this.recognition.onerror = (event) => {
          this.addTelemetry(`Voice error: ${event.error}`, 'err');
          this.stopWebSpeech();
        };

        this.recognition.onend = () => {
          this.stopWebSpeech();
        };

        this.recognition.start();
        return;
      } catch (e) {
        console.warn('Web Speech API failed, falling back to python bridge:', e);
      }
    }

    // Fallback to Python backend STT
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'listen_mic' }));
    }
  }

  stopWebSpeech() {
    this.isListeningWebSpeech = false;
    if (this.btnMic) this.btnMic.classList.remove('listening');
    this.setStatus('ONLINE');
  }

  setStatus(status) {
    if (this.statusText) {
      this.statusText.textContent = status.toUpperCase();
    }
  }

  addChat(speaker, text) {
    // Deduplicate consecutive identical user messages if needed
    const lastBubble = this.chatStream.lastElementChild;
    if (lastBubble && speaker.toUpperCase() === 'YOU') {
      const lastSpeaker = lastBubble.querySelector('.speaker-tag')?.textContent;
      const lastText = lastBubble.querySelector('.bubble-content')?.textContent;
      if (lastSpeaker?.includes('YOU') && lastText === text) {
        return; // Ignore duplicate
      }
    }

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${speaker.toLowerCase()}`;

    const tag = document.createElement('span');
    tag.className = 'speaker-tag';
    tag.textContent = speaker.toUpperCase() === 'ALTRON' ? '◆ ALTRON' : '› YOU';

    const content = document.createElement('div');
    content.className = 'bubble-content';
    content.textContent = text;

    bubble.appendChild(tag);
    bubble.appendChild(content);

    this.chatStream.appendChild(bubble);
    this.chatStream.scrollTop = this.chatStream.scrollHeight;
  }

  addTelemetry(text, type = 'sys') {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;

    const time = new Date().toTimeString().split(' ')[0];
    entry.innerHTML = `<span class="timestamp">[${time}]</span> ${text}`;

    this.telemetryLog.appendChild(entry);
    this.telemetryLog.scrollTop = this.telemetryLog.scrollHeight;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.altronApp = new AltronUIController();
});

