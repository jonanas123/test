/* ═══════════════════════════════════════════════════════════
   Central Multimídia Automotiva — App Controller (JavaScript)
   Simula o backend C++ para demonstração standalone
   ═══════════════════════════════════════════════════════════ */

// ── Playlist (mesma da versão Python) ─────────────────────
const PLAYLIST = [
  { title: "Aquarela",           artist: "Toquinho",         album: "Grandes Sucessos",       duration: 234 },
  { title: "Garota de Ipanema",  artist: "Tom Jobim",        album: "Bossa Nova Essentials",  duration: 312 },
  { title: "Mas Que Nada",       artist: "Jorge Ben Jor",    album: "Samba Esquema Novo",     duration: 178 },
  { title: "Chega de Saudade",   artist: "João Gilberto",    album: "O Amor, o Sorriso...",   duration: 248 },
  { title: "País Tropical",      artist: "Jorge Ben Jor",    album: "Grandes Sucessos",       duration: 206 },
  { title: "Construção",         artist: "Chico Buarque",    album: "Construção",             duration: 378 },
  { title: "Wave",               artist: "Tom Jobim",        album: "Wave",                   duration: 195 },
  { title: "Águas de Março",     artist: "Elis Regina",      album: "Elis & Tom",             duration: 210 },
];

// ── State ─────────────────────────────────────────────────
const state = {
  media: {
    playing: false,
    trackIndex: 0,
    volume: 10,
    muted: false,
    elapsed: 0,
  },
  hvac: {
    power: true,
    ac: true,
    targetTemp: 22.0,
    currentTemp: 25.0,
    fan: 2,
    maxFan: 5,
  },
  vehicle: {
    speed: 0,
    rpm: 800,
    fuel: 100,
    engineTemp: 90,
    doors: [],
    parkingBrake: true,
    headlights: false,
    alerts: [],
  },
  connectivity: {
    btState: "off",
    btDevice: null,
    wifiState: "off",
    wifiNetwork: null,
    btDevices: [],
    wifiNetworks: [],
  },
};

// ── Mock Data ─────────────────────────────────────────────
const MOCK_BT_DEVICES = [
  { name: "iPhone de João",     address: "AA:BB:CC:DD:EE:01" },
  { name: "Galaxy S24",         address: "AA:BB:CC:DD:EE:02" },
  { name: "AirPods Pro",        address: "AA:BB:CC:DD:EE:03" },
  { name: "JBL Charge 5",       address: "AA:BB:CC:DD:EE:04" },
];

const MOCK_WIFI_NETWORKS = [
  { ssid: "Home_5G",        signal: 92, secured: true },
  { ssid: "Cafe_WiFi",      signal: 65, secured: false },
  { ssid: "Vizinho_Net",    signal: 34, secured: true },
  { ssid: "IoT_Network",    signal: 78, secured: true },
];

// ── Clock ─────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, "0");
  const m = String(now.getMinutes()).padStart(2, "0");
  document.getElementById("clock").textContent = `${h}:${m}`;
  const d = String(now.getDate()).padStart(2, "0");
  const mo = String(now.getMonth() + 1).padStart(2, "0");
  document.getElementById("date-display").textContent = `${d}/${mo}/${now.getFullYear()}`;
}
setInterval(updateClock, 1000);
updateClock();

// ── Navigation ────────────────────────────────────────────
function showPanel(name) {
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(`panel-${name}`).classList.add("active");
  document.querySelector(`[data-panel="${name}"]`).classList.add("active");
}

// ── Media Controls ────────────────────────────────────────
let progressInterval = null;

function mediaAction(action) {
  const m = state.media;
  switch (action) {
    case "toggle":
      m.playing = !m.playing;
      if (m.playing) startProgress(); else stopProgress();
      break;
    case "next":
      m.trackIndex = (m.trackIndex + 1) % PLAYLIST.length;
      m.elapsed = 0;
      break;
    case "prev":
      m.trackIndex = (m.trackIndex - 1 + PLAYLIST.length) % PLAYLIST.length;
      m.elapsed = 0;
      break;
    case "mute":
      m.muted = !m.muted;
      break;
  }
  updateMediaUI();
}

function setVolume(val) {
  state.media.volume = parseInt(val);
  state.media.muted = false;
  updateMediaUI();
}

function startProgress() {
  stopProgress();
  progressInterval = setInterval(() => {
    const track = PLAYLIST[state.media.trackIndex];
    if (state.media.elapsed < track.duration) {
      state.media.elapsed++;
      updateProgressBar();
    } else {
      mediaAction("next");
    }
  }, 1000);
}

function stopProgress() {
  if (progressInterval) { clearInterval(progressInterval); progressInterval = null; }
}

function updateProgressBar() {
  const track = PLAYLIST[state.media.trackIndex];
  const pct = (state.media.elapsed / track.duration) * 100;
  document.getElementById("progress-fill").style.width = `${pct}%`;
  document.getElementById("time-current").textContent = formatTime(state.media.elapsed);
}

function formatTime(s) {
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

function updateMediaUI() {
  const m = state.media;
  const track = PLAYLIST[m.trackIndex];

  document.getElementById("track-title").textContent = track.title;
  document.getElementById("track-artist").textContent = track.artist;
  document.getElementById("track-album").textContent = track.album;
  document.getElementById("time-total").textContent = formatTime(track.duration);
  document.getElementById("track-num").textContent = m.trackIndex + 1;
  document.getElementById("track-total").textContent = PLAYLIST.length;

  document.getElementById("mini-track").textContent = track.title;
  document.getElementById("mini-artist").textContent = track.artist;

  const playIcon = m.playing ? "⏸" : "▶";
  document.getElementById("play-btn").textContent = playIcon;
  document.getElementById("mini-play").textContent = playIcon;

  const vinyl = document.getElementById("vinyl");
  if (m.playing) vinyl.classList.add("spinning");
  else vinyl.classList.remove("spinning");

  document.getElementById("volume-slider").value = m.volume;
  document.getElementById("vol-value").textContent = m.muted ? "🔇" : m.volume;

  const volIcon = document.getElementById("vol-icon");
  if (m.muted) {
    volIcon.textContent = "🔇";
    volIcon.classList.add("muted");
  } else {
    volIcon.textContent = m.volume > 15 ? "🔊" : m.volume > 0 ? "🔉" : "🔈";
    volIcon.classList.remove("muted");
  }

  updateProgressBar();
}

// ── HVAC Controls ─────────────────────────────────────────
function hvacAction(action) {
  const h = state.hvac;
  switch (action) {
    case "temp-up":   h.targetTemp = Math.min(30, h.targetTemp + 0.5); break;
    case "temp-down": h.targetTemp = Math.max(16, h.targetTemp - 0.5); break;
    case "fan-up":    h.fan = Math.min(h.maxFan, h.fan + 1); break;
    case "fan-down":  h.fan = Math.max(0, h.fan - 1); break;
    case "toggle-ac":    h.ac = !h.ac; break;
    case "toggle-power": h.power = !h.power; break;
  }
  updateHVACUI();
}

function updateHVACUI() {
  const h = state.hvac;

  document.getElementById("hvac-temp").textContent = h.targetTemp.toFixed(1);
  document.getElementById("hvac-current").textContent = h.currentTemp.toFixed(1);
  document.getElementById("mini-temp").textContent = h.targetTemp.toFixed(1);

  // Fan dots
  const dotsEl = document.getElementById("fan-dots");
  dotsEl.innerHTML = "";
  for (let i = 0; i < h.maxFan; i++) {
    const dot = document.createElement("span");
    dot.className = "dot" + (i < h.fan ? " active" : "");
    dotsEl.appendChild(dot);
  }
  document.getElementById("fan-level").textContent = `${h.fan} / ${h.maxFan}`;
  document.getElementById("mini-fan").textContent = `Fan ${h.fan}/${h.maxFan}`;

  // Toggles
  document.getElementById("btn-ac").classList.toggle("active", h.ac);
  document.getElementById("btn-power").classList.toggle("active", h.power);
  document.getElementById("mini-ac").textContent = h.ac ? "A/C ON" : "A/C OFF";
  document.getElementById("mini-ac").className = "tag" + (h.ac ? " tag-active" : "");

  // Temperature ring
  const range = 30 - 16; // 14 degrees
  const pct = (h.targetTemp - 16) / range;
  const dashoffset = 534 - (534 * pct);
  document.getElementById("temp-ring").style.strokeDashoffset = dashoffset;
}

// ── Vehicle Simulation ────────────────────────────────────
function simulateVehicle() {
  const v = state.vehicle;
  v.speed = Math.max(0, Math.min(220, v.speed + (Math.random() * 10 - 4)));
  v.rpm = Math.max(600, Math.min(7000, 800 + v.speed * 30 + (Math.random() * 200 - 100)));
  v.fuel = Math.max(0, v.fuel - Math.random() * 0.05);
  v.engineTemp = 85 + Math.random() * 15;

  const doorRoll = Math.random();
  v.doors = doorRoll < 0.05 ? ["Motorista"] : doorRoll < 0.08 ? ["Passageiro"] : [];

  v.parkingBrake = v.speed < 5;
  v.headlights = v.speed > 0;

  v.alerts = [];
  if (v.speed > 120) v.alerts.push({ level: "WARNING", msg: `Velocidade alta: ${v.speed.toFixed(0)} km/h` });
  if (v.fuel < 15)   v.alerts.push({ level: "CRITICAL", msg: `Combustível baixo: ${v.fuel.toFixed(1)}%` });
  if (v.engineTemp > 110) v.alerts.push({ level: "CRITICAL", msg: `Temperatura alta: ${v.engineTemp.toFixed(0)}°C` });
  if (v.doors.length > 0) v.alerts.push({ level: "WARNING", msg: `Porta aberta: ${v.doors.join(", ")}` });

  updateVehicleUI();
  updateDashboardUI();
}

function refreshVehicle() { simulateVehicle(); }

function updateVehicleUI() {
  const v = state.vehicle;

  document.getElementById("v-speed").textContent = v.speed.toFixed(0);
  document.getElementById("v-rpm").textContent = Math.round(v.rpm);
  document.getElementById("v-fuel").textContent = v.fuel.toFixed(0);
  document.getElementById("v-engine-temp").textContent = v.engineTemp.toFixed(0);

  // Circle gauges (stroke-dashoffset: 314 = empty, 0 = full)
  const speedPct = v.speed / 220;
  document.getElementById("v-speed-gauge").style.strokeDashoffset = 314 - 314 * speedPct;
  if (v.speed > 120) document.getElementById("v-speed-gauge").style.stroke = "var(--red)";
  else document.getElementById("v-speed-gauge").style.stroke = "";

  const rpmPct = v.rpm / 7000;
  document.getElementById("v-rpm-gauge").style.strokeDashoffset = 314 - 314 * rpmPct;

  const fuelPct = v.fuel / 100;
  document.getElementById("v-fuel-gauge").style.strokeDashoffset = 314 - 314 * fuelPct;
  if (v.fuel < 15) document.getElementById("v-fuel-gauge").style.stroke = "var(--red)";
  else document.getElementById("v-fuel-gauge").style.stroke = "";

  const tempPct = (v.engineTemp - 60) / 80;
  document.getElementById("v-temp-gauge").style.strokeDashoffset = 314 - 314 * Math.min(1, tempPct);
  if (v.engineTemp > 110) document.getElementById("v-temp-gauge").style.stroke = "var(--red)";
  else document.getElementById("v-temp-gauge").style.stroke = "";

  // Info cards
  const doorsEl = document.getElementById("v-doors");
  doorsEl.textContent = v.doors.length > 0 ? v.doors.join(", ") : "Todas fechadas";
  doorsEl.className = "info-value" + (v.doors.length > 0 ? " warning" : "");

  const brakeEl = document.getElementById("v-brake");
  brakeEl.textContent = v.parkingBrake ? "ATIVADO" : "Desativado";
  brakeEl.className = "info-value" + (v.parkingBrake ? " warning" : "");

  const lightsEl = document.getElementById("v-lights");
  lightsEl.textContent = v.headlights ? "ACESOS" : "Apagados";
  lightsEl.className = "info-value" + (v.headlights ? "" : "");

  // Alerts
  const alertsEl = document.getElementById("vehicle-alerts");
  alertsEl.innerHTML = v.alerts.map(a => {
    const cls = a.level === "CRITICAL" ? "alert-critical" : a.level === "WARNING" ? "alert-warning" : "alert-info";
    const icon = a.level === "CRITICAL" ? "🚨" : a.level === "WARNING" ? "⚠️" : "ℹ️";
    return `<div class="alert-item ${cls}">${icon} ${a.msg}</div>`;
  }).join("");
}

function updateDashboardUI() {
  const v = state.vehicle;

  // Speed gauge arc
  const speedPct = Math.min(v.speed / 220, 1);
  const dashOffset = 251 - 251 * speedPct;
  const arc = document.getElementById("speed-arc");
  arc.style.strokeDashoffset = dashOffset;
  if (v.speed > 120) arc.style.stroke = "var(--red)";
  else if (v.speed > 80) arc.style.stroke = "var(--yellow)";
  else arc.style.stroke = "";

  document.getElementById("dash-speed").textContent = v.speed.toFixed(0);
  document.getElementById("dash-rpm").textContent = Math.round(v.rpm);

  // RPM bar
  const rpmPct = (v.rpm / 7000) * 100;
  document.getElementById("rpm-bar").style.width = `${rpmPct}%`;

  // Fuel
  document.getElementById("fuel-level").style.width = `${v.fuel}%`;
  const fuelText = document.getElementById("fuel-text");
  fuelText.textContent = `${v.fuel.toFixed(1)}%`;
  fuelText.style.color = v.fuel < 15 ? "var(--red)" : v.fuel < 30 ? "var(--yellow)" : "var(--green)";

  // Status bar icons
  const btIcon = document.getElementById("bt-icon");
  btIcon.style.color = state.connectivity.btDevice ? "var(--accent2)" : "var(--text-dim)";
  const wifiIcon = document.getElementById("wifi-icon");
  wifiIcon.style.color = state.connectivity.wifiNetwork ? "var(--accent)" : "var(--text-dim)";

  const signalText = document.getElementById("signal-text");
  if (state.connectivity.wifiNetwork) {
    signalText.textContent = state.connectivity.wifiNetwork.ssid;
  } else {
    signalText.textContent = "---";
  }
}

// ── Connectivity ──────────────────────────────────────────
function connAction(action) {
  const c = state.connectivity;
  switch (action) {
    case "bt-scan":
      c.btState = "scanning";
      document.getElementById("bt-status").textContent = "Escaneando...";
      setTimeout(() => {
        c.btDevices = MOCK_BT_DEVICES;
        c.btState = "ready";
        document.getElementById("bt-status").textContent = "Dispositivos encontrados";
        renderBtDevices();
      }, 1500);
      break;

    case "bt-pair":
      if (c.btDevices.length === 0) { connAction("bt-scan"); return; }
      const btDev = c.btDevices[0];
      c.btState = "pairing";
      document.getElementById("bt-status").textContent = "Pareando...";
      setTimeout(() => {
        c.btDevice = btDev;
        c.btState = "connected";
        updateConnUI();
      }, 2000);
      break;

    case "bt-disconnect":
      c.btDevice = null;
      c.btState = "off";
      c.btDevices = [];
      document.getElementById("bt-devices").innerHTML = "";
      updateConnUI();
      break;

    case "wifi-scan":
      c.wifiState = "scanning";
      document.getElementById("wifi-status").textContent = "Escaneando...";
      setTimeout(() => {
        c.wifiNetworks = MOCK_WIFI_NETWORKS;
        c.wifiState = "ready";
        document.getElementById("wifi-status").textContent = "Redes encontradas";
        renderWifiNetworks();
      }, 1500);
      break;

    case "wifi-connect":
      if (c.wifiNetworks.length === 0) { connAction("wifi-scan"); return; }
      const net = c.wifiNetworks[0];
      c.wifiState = "connecting";
      document.getElementById("wifi-status").textContent = "Conectando...";
      setTimeout(() => {
        c.wifiNetwork = net;
        c.wifiState = "connected";
        updateConnUI();
      }, 2000);
      break;

    case "wifi-disconnect":
      c.wifiNetwork = null;
      c.wifiState = "off";
      c.wifiNetworks = [];
      document.getElementById("wifi-networks").innerHTML = "";
      updateConnUI();
      break;
  }
}

function renderBtDevices() {
  const el = document.getElementById("bt-devices");
  el.innerHTML = state.connectivity.btDevices.map(d =>
    `<div class="device-item" onclick="pairBtDevice('${d.address}')">
       <span>${d.name}</span>
       <span class="device-detail">${d.address}</span>
     </div>`
  ).join("");
}

function renderWifiNetworks() {
  const el = document.getElementById("wifi-networks");
  el.innerHTML = state.connectivity.wifiNetworks.map(n =>
    `<div class="device-item" onclick="connectWifi('${n.ssid}')">
       <span>${n.ssid} ${n.secured ? "🔒" : "🔓"}</span>
       <span class="device-detail">${n.signal}%</span>
     </div>`
  ).join("");
}

function pairBtDevice(address) {
  const dev = state.connectivity.btDevices.find(d => d.address === address);
  if (!dev) return;
  state.connectivity.btDevice = dev;
  state.connectivity.btState = "connected";
  updateConnUI();
}

function connectWifi(ssid) {
  const net = state.connectivity.wifiNetworks.find(n => n.ssid === ssid);
  if (!net) return;
  state.connectivity.wifiNetwork = net;
  state.connectivity.wifiState = "connected";
  updateConnUI();
}

function updateConnUI() {
  const c = state.connectivity;

  const btStatus = document.getElementById("bt-status");
  const btDevice = document.getElementById("bt-device");
  if (c.btDevice) {
    btStatus.textContent = "Conectado";
    btStatus.className = "conn-status connected";
    btDevice.innerHTML = `<span class="device-name">${c.btDevice.name}</span><br><span class="device-detail">${c.btDevice.address}</span>`;
  } else {
    btStatus.textContent = "Desconectado";
    btStatus.className = "conn-status";
    btDevice.innerHTML = '<span class="device-name">Nenhum dispositivo</span>';
  }

  const wifiStatus = document.getElementById("wifi-status");
  const wifiDevice = document.getElementById("wifi-device");
  if (c.wifiNetwork) {
    wifiStatus.textContent = "Conectado";
    wifiStatus.className = "conn-status connected";
    wifiDevice.innerHTML = `<span class="device-name">${c.wifiNetwork.ssid}</span> <span class="device-detail">(${c.wifiNetwork.signal}%)</span>`;
  } else {
    wifiStatus.textContent = "Desconectado";
    wifiStatus.className = "conn-status";
    wifiDevice.innerHTML = '<span class="device-name">Nenhuma rede</span>';
  }

  updateDashboardUI();
}

// ── Initialization ────────────────────────────────────────
updateMediaUI();
updateHVACUI();
simulateVehicle();
setInterval(simulateVehicle, 3000);

// Simulate HVAC current temp approaching target
setInterval(() => {
  const h = state.hvac;
  if (h.power) {
    const diff = h.targetTemp - h.currentTemp;
    h.currentTemp += diff * 0.05;
    document.getElementById("hvac-current").textContent = h.currentTemp.toFixed(1);
  }
}, 2000);
