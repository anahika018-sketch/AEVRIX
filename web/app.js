/**
 * Aevrix AI Frontend Web Application
 * ChatGPT / Gemini styled Dark Theme interface with Continuous Live Hands-Free Voice
 */

const API_BASE = window.location.origin.startsWith("http") ? "" : "http://localhost:5000";

let isRecording = false;
let recognition = null;
let voiceOutputEnabled = true;
let handsFreeMode = true; // Auto-listen after answering
let currentProfile = { user_name: "Sir", assistant_name: "Aevrix" };

// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const micBtn = document.getElementById("micBtn");
const voiceOrb = document.getElementById("voiceOrb");
const voiceWaveBar = document.getElementById("voiceWaveBar");
const welcomeHero = document.getElementById("welcomeHero");
const voiceMuteToggle = document.getElementById("voiceMuteToggle");
const voiceMuteIcon = document.getElementById("voiceMuteIcon");
const handsFreeToggleBtn = document.getElementById("handsFreeToggleBtn");
const handsFreeLabel = document.getElementById("handsFreeLabel");
const waveText = document.getElementById("waveText");

// Initialize on Load
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSpeechRecognition();
  initTextareaAutoResize();
  fetchProfile();
  fetchReminders();
  fetchNotes();
  fetchAnalytics();

  // Voice mute toggle
  voiceMuteToggle.addEventListener("click", () => {
    voiceOutputEnabled = !voiceOutputEnabled;
    voiceMuteIcon.textContent = voiceOutputEnabled ? "🔊" : "🔇";
  });

  // Hands-free toggle
  if (handsFreeToggleBtn) {
    handsFreeToggleBtn.addEventListener("click", () => {
      handsFreeMode = !handsFreeMode;
      handsFreeToggleBtn.classList.toggle("active", handsFreeMode);
      handsFreeLabel.textContent = handsFreeMode ? "Hands-Free: ON" : "Hands-Free: OFF";
    });
  }

  // Mobile sidebar toggle
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  // New Chat button
  document.getElementById("newChatBtn").addEventListener("click", () => {
    chatMessages.innerHTML = "";
    chatMessages.appendChild(welcomeHero);
    welcomeHero.style.display = "flex";
  });

  // Settings modal toggle
  document.getElementById("settingsToggleBtn").addEventListener("click", () => {
    toggleSettingsModal(true);
  });

  // Greet user on first user interaction
  document.body.addEventListener("click", playInitialGreetingOnce, { once: true });
});

let greetingPlayed = false;
function playInitialGreetingOnce() {
  if (greetingPlayed) return;
  greetingPlayed = true;
  // Play subtle audio greeting and prime speech engine
  setTimeout(() => {
    speakText("Hello! I am Aevrix. How can I help you?");
  }, 300);
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================
function initTabs() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", () => {
      navItems.forEach(n => n.classList.remove("active"));
      item.classList.add("active");

      const tabName = item.getAttribute("data-tab");
      document.querySelectorAll(".view-panel").forEach(panel => {
        panel.classList.remove("active");
      });

      const targetPanel = document.getElementById(`view${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }

      if (tabName === "reminders") fetchReminders();
      if (tabName === "notes") fetchNotes();
      if (tabName === "analytics") fetchAnalytics();
    });
  });
}

// ============================================================================
// BROWSER SPEECH RECOGNITION (Web Speech API)
// ============================================================================
function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("Web Speech API not supported in this browser.");
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onstart = () => {
    isRecording = true;
    micBtn.classList.add("active");
    voiceOrb.classList.add("listening");
    voiceWaveBar.classList.add("active");
    if (waveText) waveText.textContent = "Listening to you... Speak now";
  };

  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(result => result[0].transcript)
      .join("");
    messageInput.value = transcript;
  };

  recognition.onerror = (event) => {
    console.error("Speech Recognition Error:", event.error);
    stopRecordingUI();
  };

  recognition.onend = () => {
    stopRecordingUI();
    const query = messageInput.value.trim();
    if (query) {
      handleSend();
    }
  };
}

function startListening() {
  if (!recognition || isRecording) return;
  try {
    messageInput.value = "";
    recognition.start();
  } catch (e) {
    console.warn("Recognition start notice:", e);
  }
}

function toggleVoiceRecording() {
  if (!recognition) {
    alert("Speech recognition is supported in Chrome, Edge, and modern browsers.");
    return;
  }

  if (isRecording) {
    recognition.stop();
    stopRecordingUI();
  } else {
    startListening();
  }
}

function stopRecordingUI() {
  isRecording = false;
  micBtn.classList.remove("active");
  voiceOrb.classList.remove("listening");
  voiceWaveBar.classList.remove("active");
}

// ============================================================================
// SPEECH SYNTHESIS (Voice Output with Hands-Free Auto-Listen Loop)
// ============================================================================
function speakText(text) {
  if (!voiceOutputEnabled || !window.speechSynthesis) return;

  window.speechSynthesis.cancel();
  const cleanText = text.replace(/[*_#`[\]()]/g, "");
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.rate = 1.05;
  utterance.pitch = 1.0;

  voiceOrb.classList.add("speaking");

  utterance.onend = () => {
    voiceOrb.classList.remove("speaking");
    // Hands-Free Mode: automatically listen for next question after speaking
    if (handsFreeMode && recognition) {
      setTimeout(() => {
        startListening();
      }, 500);
    }
  };

  utterance.onerror = () => {
    voiceOrb.classList.remove("speaking");
  };

  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find(v => 
    v.name.includes("Google UK English Male") || 
    v.name.includes("Natural") || 
    v.name.includes("David") ||
    v.lang === "en-US"
  );
  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }

  window.speechSynthesis.speak(utterance);
}

// ============================================================================
// CHAT MESSAGING
// ============================================================================
function initTextareaAutoResize() {
  messageInput.addEventListener("input", function() {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
  });

  messageInput.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });
}

function sendQuickCommand(cmd) {
  messageInput.value = cmd;
  handleSend();
}

function removeWakeWord(text) {
  let cleaned = text.trim();
  const wakeWords = ["hey aevrix", "aevrix", "hey jarvis", "jarvis"];
  const lower = cleaned.toLowerCase();
  for (const w of wakeWords) {
    if (lower.startsWith(w)) {
      cleaned = cleaned.slice(w.length).replace(/^[,:.\s]+/, "");
      break;
    }
  }
  return cleaned || text;
}

async function handleSend() {
  let query = messageInput.value.trim();
  if (!query) return;

  query = removeWakeWord(query);

  if (welcomeHero) {
    welcomeHero.style.display = "none";
  }

  appendMessage("user", query);
  messageInput.value = "";
  messageInput.style.height = "auto";

  const typingId = appendTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: query })
    });

    const data = await res.json();
    removeTypingIndicator(typingId);

    const reply = data.response || "No response received.";
    appendMessage("assistant", reply);

    // Speak response aloud (hands-free auto-listens when done!)
    speakText(reply);

    fetchAnalytics();
    fetchReminders();
    fetchNotes();

  } catch (err) {
    removeTypingIndicator(typingId);
    appendMessage("assistant", `Connection error: ${err.message}. Ensure the backend server is running.`);
  }
}

function appendMessage(sender, text) {
  const row = document.createElement("div");
  row.className = `message-row ${sender}`;

  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const avatarLetter = sender === "user" ? (currentProfile.user_name ? currentProfile.user_name[0] : "U") : "A";

  row.innerHTML = `
    <div class="msg-avatar">${avatarLetter}</div>
    <div class="msg-bubble">
      <div class="msg-content">${formatMessageContent(text)}</div>
      <span class="msg-time">${now}</span>
    </div>
  `;

  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessageContent(text) {
  return text
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>");
}

function appendTypingIndicator() {
  const id = "typing-" + Date.now();
  const row = document.createElement("div");
  row.className = "message-row assistant";
  row.id = id;
  row.innerHTML = `
    <div class="msg-avatar">A</div>
    <div class="msg-bubble" style="opacity: 0.7;">
      <em>Aevrix is thinking...</em>
    </div>
  `;
  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ============================================================================
// API INTEGRATIONS
// ============================================================================

async function fetchProfile() {
  try {
    const res = await fetch(`${API_BASE}/api/profile`);
    if (res.ok) {
      currentProfile = await res.json();
      document.getElementById("profileUserName").textContent = currentProfile.user_name || "Sir";
      document.getElementById("heroUser").textContent = currentProfile.user_name || "Sir";
      document.getElementById("profileAssistantName").textContent = (currentProfile.assistant_name || "Aevrix") + " Assistant";
      document.getElementById("avatarLetter").textContent = currentProfile.user_name ? currentProfile.user_name[0] : "A";
      document.getElementById("settingUserName").value = currentProfile.user_name || "";
      document.getElementById("settingAssistantName").value = currentProfile.assistant_name || "";
      document.getElementById("settingPersonality").value = currentProfile.personality || "Jarvis";
      document.getElementById("settingSecurity").value = currentProfile.security_level || "STANDARD";
    }
  } catch (e) {
    console.warn("Notice fetching profile:", e);
  }
}

async function fetchReminders() {
  try {
    const res = await fetch(`${API_BASE}/api/reminders`);
    if (res.ok) {
      const reminders = await res.json();
      const countEl = document.getElementById("remindersCount");
      const listEl = document.getElementById("remindersList");
      
      const pending = reminders.filter(r => r.status === "pending");
      countEl.textContent = pending.length;

      if (reminders.length === 0) {
        listEl.innerHTML = `<div class="empty-state">No reminders scheduled yet.</div>`;
        return;
      }

      listEl.innerHTML = reminders.map(r => {
        const timeStr = r.remind_at ? r.remind_at.substring(11, 16) : "";
        return `
          <div class="list-row">
            <div class="list-row-left">
              <span class="status-badge ${r.status}">${r.status.toUpperCase()}</span>
              <div>
                <strong>${r.title}</strong>
                <div style="font-size: 0.75rem; color: #64748b;">Scheduled for ${timeStr}</div>
              </div>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="deleteReminder(${r.id})">Delete</button>
          </div>
        `;
      }).join("");
    }
  } catch (e) {
    console.warn("Notice fetching reminders:", e);
  }
}

async function createReminderManual() {
  const task = document.getElementById("remTaskInput").value.trim();
  const mins = parseInt(document.getElementById("remMinsInput").value) || 5;
  if (!task) return;

  try {
    await fetch(`${API_BASE}/api/reminders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task, minutes: mins })
    });
    document.getElementById("remTaskInput").value = "";
    fetchReminders();
    appendMessage("assistant", `I have scheduled a reminder: '${task}' in ${mins} minutes.`);
  } catch (e) {
    alert("Failed to create reminder: " + e.message);
  }
}

async function deleteReminder(id) {
  try {
    await fetch(`${API_BASE}/api/reminders/${id}`, { method: "DELETE" });
    fetchReminders();
  } catch (e) {
    console.warn(e);
  }
}

async function fetchNotes() {
  try {
    const res = await fetch(`${API_BASE}/api/notes`);
    if (res.ok) {
      const notes = await res.json();
      document.getElementById("notesCount").textContent = notes.length;
      const listEl = document.getElementById("notesList");

      if (notes.length === 0) {
        listEl.innerHTML = `<div class="empty-state">No notes saved in your vault yet.</div>`;
        return;
      }

      listEl.innerHTML = notes.map(n => `
        <div class="list-row">
          <div>
            <div>${n.content}</div>
            <div style="font-size: 0.72rem; color: #64748b; margin-top: 4px;">Saved: ${n.created_at}</div>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="deleteNote(${n.id})">Delete</button>
        </div>
      `).join("");
    }
  } catch (e) {
    console.warn("Notice fetching notes:", e);
  }
}

async function createNoteManual() {
  const content = document.getElementById("noteInput").value.trim();
  if (!content) return;

  try {
    await fetch(`${API_BASE}/api/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content })
    });
    document.getElementById("noteInput").value = "";
    fetchNotes();
  } catch (e) {
    alert("Failed to save note: " + e.message);
  }
}

async function deleteNote(id) {
  try {
    await fetch(`${API_BASE}/api/notes/${id}`, { method: "DELETE" });
    fetchNotes();
  } catch (e) {
    console.warn(e);
  }
}

async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/api/analytics`);
    if (res.ok) {
      const data = await res.json();
      const s = data.summary;
      document.getElementById("kpiTotal").textContent = s.total_commands || 0;
      document.getElementById("kpiToday").textContent = s.today_count || 0;
      document.getElementById("kpiRate").textContent = `${s.success_rate}%`;
      document.getElementById("kpiAvg").textContent = `${s.avg_response_time_ms} ms`;

      const topEl = document.getElementById("topIntentsContainer");
      if (s.top_intents && s.top_intents.length > 0) {
        topEl.innerHTML = s.top_intents.map(item => `
          <div class="list-row">
            <strong>${item.intent}</strong>
            <span class="count-pill">${item.count} calls</span>
          </div>
        `).join("");
      } else {
        topEl.innerHTML = `<div class="empty-state">No interactions recorded yet.</div>`;
      }
    }
  } catch (e) {
    console.warn("Notice fetching analytics:", e);
  }
}

function toggleSettingsModal(show) {
  const modal = document.getElementById("settingsModal");
  if (show) modal.classList.add("active");
  else modal.classList.remove("active");
}

async function saveSettings() {
  const user_name = document.getElementById("settingUserName").value.trim();
  const assistant_name = document.getElementById("settingAssistantName").value.trim();
  const personality = document.getElementById("settingPersonality").value;
  const security_level = document.getElementById("settingSecurity").value;

  try {
    await fetch(`${API_BASE}/api/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_name, assistant_name, personality, security_level })
    });
    toggleSettingsModal(false);
    fetchProfile();
    appendMessage("assistant", `Preferences updated. I am now configured for ${user_name} in ${personality} mode.`);
  } catch (e) {
    alert("Error saving settings: " + e.message);
  }
}
