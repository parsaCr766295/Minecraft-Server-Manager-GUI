<?php
?><!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Minecraft Server Setup (PHP)</title>
  <style>
    :root { color-scheme: light dark; }
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; padding: 0; background: #0f172a; color: #e2e8f0; }
    .container { max-width: 1000px; margin: 0 auto; padding: 24px; }
    .card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 20px; box-shadow: 0 10px 20px rgba(0,0,0,.3); margin-bottom: 20px; }
    h1 { font-size: 28px; margin: 0 0 16px; }
    h2 { font-size: 20px; margin: 0 0 12px; }
    label { display: block; margin: 12px 0 6px; font-weight: 600; }
    input, select { width: 100%; padding: 10px 12px; border-radius: 8px; border: 1px solid #374151; background: #0b1220; color: #e5e7eb; }
    input[type="checkbox"] { width: auto; }
    .row { display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; }
    .col-6 { grid-column: span 6; }
    .col-4 { grid-column: span 4; }
    .col-8 { grid-column: span 8; }
    .btn { background: #2563eb; color: white; border: none; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: 700; }
    .btn.secondary { background: #374151; }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; }
    .progress { height: 10px; background: #1f2937; border-radius: 999px; overflow: hidden; }
    .progress-bar { height: 100%; background: linear-gradient(90deg, #22d3ee, #2563eb); width: 0%; transition: width .2s; }
    .logs { background: #0b1220; border: 1px solid #1f2937; border-radius: 8px; padding: 12px; height: 300px; overflow: auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; }
    .badge { display: inline-block; padding: 2px 8px; background: #0ea5e9; color: #082f49; border-radius: 999px; font-size: 12px; font-weight: 800; }
    .muted { color: #9ca3af; }
    .actions { display: flex; gap: 12px; flex-wrap: wrap; }
    .help { font-size: 12px; color: #9ca3af; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>MC Server Setup (PHP) <span class="badge" id="javaBadge">Checking Java...</span></h1>
      <div class="row">
        <div class="col-8">
          <label>Server Directory</label>
          <input id="serverDir" value="mc_server" />
        </div>
        <div class="col-4">
          <label>Version</label>
          <select id="version"></select>
        </div>
      </div>
      <div class="row">
        <div class="col-6">
          <label>Min Memory (Xms)</label>
          <input id="minMemory" value="1G" />
        </div>
        <div class="col-6">
          <label>Max Memory (Xmx)</label>
          <input id="maxMemory" value="2G" />
        </div>
      </div>
      <div class="row">
        <div class="col-6">
          <label><input type="checkbox" id="acceptEula" /> Accept EULA</label>
        </div>
        <div class="col-6">
          <label><input type="checkbox" id="forceDownload" /> Force re-download</label>
        </div>
      </div>
      <div class="row">
        <div class="col-8">
          <label>JVM Flags (optional)</label>
          <input id="jvmFlags" placeholder="e.g. -XX:+UseG1GC -XX:+ParallelRefProcEnabled" />
          <div class="help">Enter additional JVM arguments to tune performance. Leave blank for defaults.</div>
        </div>
        <div class="col-4">
          <label>Run with GUI?</label>
          <select id="guiMode">
            <option value="nogui" selected>Headless (nogui)</option>
            <option value="gui">With GUI</option>
          </select>
          <div class="help">On Windows, you can also start in a visible console via the Foreground option.</div>
        </div>
      </div>
      <div class="actions" style="margin-top: 12px;">
        <button class="btn" id="setupBtn">Run Setup</button>
        <button class="btn secondary" id="startBtn" disabled>Start Server</button>
        <button class="btn secondary" id="startForegroundBtn">Start in Foreground (Windows)</button>
        <button class="btn secondary" id="stopBtn" disabled>Stop Server</button>
        <button class="btn secondary" id="refreshStatusBtn">Refresh Status</button>
      </div>
      <div style="margin-top: 16px;">
        <div class="progress"><div class="progress-bar" id="progressBar"></div></div>
        <div class="muted" id="progressText" style="margin-top: 8px;">Waiting...</div>
        <div class="muted" id="statusText" style="margin-top: 8px;">Status: unknown</div>
      </div>
    </div>

    <div class="card">
      <h2>Server Logs</h2>
      <div class="row" style="margin-bottom:8px; align-items:center;">
        <div class="col-8">
          <div class="help">Choose which log file to display.</div>
        </div>
        <div class="col-4">
          <label for="logSource">Log Source</label>
          <select id="logSource">
            <option value="auto" selected>Auto (latest.log, fallback to PHP)</option>
            <option value="latest">latest.log (official)</option>
            <option value="php">server_php.log (background)</option>
          </select>
        </div>
      </div>
      <div class="logs" id="logs"></div>
    </div>

    <div class="card">
      <h2>Server Properties</h2>
      <div class="row">
        <div class="col-6">
          <label>Server MOTD</label>
          <input id="serverMotd" value="A Minecraft Server" />
        </div>
        <div class="col-6">
          <label>Server Port</label>
          <input id="serverPort" type="number" value="25565" />
        </div>
      </div>
      <div class="row">
        <div class="col-4">
          <label>Difficulty</label>
          <select id="difficulty">
            <option value="peaceful">Peaceful</option>
            <option value="easy" selected>Easy</option>
            <option value="normal">Normal</option>
            <option value="hard">Hard</option>
          </select>
        </div>
        <div class="col-4">
          <label>Gamemode</label>
          <select id="gamemode">
            <option value="survival" selected>Survival</option>
            <option value="creative">Creative</option>
            <option value="adventure">Adventure</option>
            <option value="spectator">Spectator</option>
          </select>
        </div>
        <div class="col-4">
          <label>Max Players</label>
          <input id="maxPlayers" type="number" value="20" />
        </div>
      </div>
      <div class="row">
        <div class="col-6">
          <label><input type="checkbox" id="pvp" checked /> Enable PvP</label>
        </div>
        <div class="col-6">
          <label><input type="checkbox" id="onlineMode" checked /> Online Mode (Authentication)</label>
        </div>
      </div>
      <div style="margin-top: 12px;">
        <button class="btn" id="savePropertiesBtn">Save Properties</button>
      </div>
    </div>
  </div>
  <script>
    const versionSelect = document.getElementById('version');
    const javaBadge = document.getElementById('javaBadge');
    const setupBtn = document.getElementById('setupBtn');
    const startBtn = document.getElementById('startBtn');
    const startForegroundBtn = document.getElementById('startForegroundBtn');
    const stopBtn = document.getElementById('stopBtn');
    const refreshStatusBtn = document.getElementById('refreshStatusBtn');
    const savePropertiesBtn = document.getElementById('savePropertiesBtn');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const statusText = document.getElementById('statusText');
    const logsEl = document.getElementById('logs');
    const logSourceSel = document.getElementById('logSource');

    function appendLog(text) {
      const div = document.createElement('div');
      div.textContent = text;
      logsEl.appendChild(div);
      logsEl.scrollTop = logsEl.scrollHeight;
    }

    function appendProgress(text) {
      progressText.textContent = text;
    }

    async function loadVersions() {
      const res = await fetch('api.php?action=versions');
      const data = await res.json();
      versionSelect.innerHTML = '';
      if (data.error) {
        versionSelect.innerHTML = `<option value="latest">latest</option>`;
        appendProgress('Error loading versions: ' + data.error);
        return;
      }
      versionSelect.insertAdjacentHTML('beforeend', `<option value="latest">latest (release: ${data.latest_release})</option>`);
      if (data.latest_snapshot) {
        versionSelect.insertAdjacentHTML('beforeend', `<option value="snapshot">latest snapshot (${data.latest_snapshot})</option>`);
      }
      const unique = new Set();
      data.releases.forEach(v => {
        if (!unique.has(v.id)) {
          versionSelect.insertAdjacentHTML('beforeend', `<option value="${v.id}">${v.id} (release)</option>`);
          unique.add(v.id);
        }
      });
      data.snapshots.forEach(v => {
        if (!unique.has(v.id)) {
          versionSelect.insertAdjacentHTML('beforeend', `<option value="${v.id}">${v.id} (snapshot)</option>`);
          unique.add(v.id);
        }
      });
    }

    async function checkJava() {
      const res = await fetch('api.php?action=java');
      const data = await res.json();
      if (data.ok) {
        javaBadge.textContent = 'Java OK';
        javaBadge.style.background = '#10b981';
        javaBadge.style.color = '#052e2b';
      } else {
        javaBadge.textContent = 'Java missing or old';
        javaBadge.style.background = '#ef4444';
        javaBadge.style.color = '#450a0a';
        appendProgress('Java check: ' + data.output);
      }
    }

    function collectCommonPayload() {
      return {
        version: document.getElementById('version').value,
        serverDir: document.getElementById('serverDir').value,
        minMemory: document.getElementById('minMemory').value,
        maxMemory: document.getElementById('maxMemory').value,
        acceptEula: document.getElementById('acceptEula').checked,
        forceDownload: document.getElementById('forceDownload').checked,
        jvmFlags: document.getElementById('jvmFlags').value.trim(),
        nogui: document.getElementById('guiMode').value === 'nogui'
      };
    }

    setupBtn.addEventListener('click', async () => {
      setupBtn.disabled = true;
      const payload = collectCommonPayload();
      const res = await fetch('api.php?action=setup', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      if (!res.ok) {
        progressBar.style.width = '0%';
        appendProgress('Error: ' + data.error);
      } else {
        progressBar.style.width = '100%';
        appendProgress('Setup complete for version ' + data.version);
        startBtn.disabled = false;
        startForegroundBtn.disabled = false;
      }
      setupBtn.disabled = false;
    });

    startBtn.addEventListener('click', () => startServer(false));
    startForegroundBtn.addEventListener('click', () => startServer(true));

    async function startServer(foreground) {
      startBtn.disabled = true;
      startForegroundBtn.disabled = true;
      const common = collectCommonPayload();
      const payload = {
        serverDir: common.serverDir,
        minMemory: common.minMemory,
        maxMemory: common.maxMemory,
        jvmFlags: common.jvmFlags,
        nogui: common.nogui,
        foreground
      };
      const res = await fetch('api.php?action=start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      if (!res.ok) {
        appendLog('Start error: ' + data.error);
        startBtn.disabled = false;
        startForegroundBtn.disabled = false;
        return;
      }
      appendLog('Server starting... Mode ' + (data.mode || 'background') + ', PID ' + (data.pid ?? 'unknown'));
      stopBtn.disabled = false;
      // begin polling logs
      pollLogs();
      // update status periodically
      startStatusPolling();
    }

    stopBtn.addEventListener('click', async () => {
      stopBtn.disabled = true;
      const payload = { serverDir: document.getElementById('serverDir').value };
      const res = await fetch('api.php?action=stop', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      if (!res.ok) {
        appendLog('Stop error: ' + data.error);
        stopBtn.disabled = false;
        return;
      }
      appendLog('Server stopped');
      startBtn.disabled = false;
      startForegroundBtn.disabled = false;
    });

    async function refreshStatus() {
      const serverDir = document.getElementById('serverDir').value;
      const res = await fetch('api.php?action=status&serverDir=' + encodeURIComponent(serverDir));
      const data = await res.json();
      statusText.textContent = 'Status: ' + data.status + (data.pid ? ' (PID ' + data.pid + ')' : '');
      startBtn.disabled = data.status === 'running';
      startForegroundBtn.disabled = data.status === 'running';
      stopBtn.disabled = data.status !== 'running';
    }

    function startStatusPolling() {
      refreshStatus();
      if (window._statusInterval) clearInterval(window._statusInterval);
      window._statusInterval = setInterval(refreshStatus, 3000);
    }

    async function pollLogs() {
      const serverDir = document.getElementById('serverDir').value;
      const source = logSourceSel.value;
      try {
        const res = await fetch('api.php?action=logs&serverDir=' + encodeURIComponent(serverDir) + '&lines=100&source=' + encodeURIComponent(source));
        const data = await res.json();
        logsEl.innerHTML = '';
        (data.logs || []).forEach(line => line && appendLog(line));
        if (data.source) {
          const info = document.createElement('div');
          info.className = 'muted';
          info.textContent = 'Source: ' + data.source;
          logsEl.appendChild(info);
        }
      } catch (e) { /* ignore */ }
      // keep polling every 2s if running
      if (!startBtn.disabled) return; // not running
      setTimeout(pollLogs, 2000);
    }

    logSourceSel.addEventListener('change', () => {
      // Immediately refresh logs when source changes
      pollLogs();
    });

    refreshStatusBtn.addEventListener('click', refreshStatus);

    loadVersions();
    checkJava();
    startStatusPolling();
    
    // Server properties functionality
    savePropertiesBtn.addEventListener('click', async () => {
      savePropertiesBtn.disabled = true;
      const payload = {
        serverDir: document.getElementById('serverDir').value,
        properties: {
          motd: document.getElementById('serverMotd').value,
          'server-port': document.getElementById('serverPort').value,
          difficulty: document.getElementById('difficulty').value,
          gamemode: document.getElementById('gamemode').value,
          'max-players': document.getElementById('maxPlayers').value,
          pvp: document.getElementById('pvp').checked.toString(),
          'online-mode': document.getElementById('onlineMode').checked.toString()
        }
      };
      
      try {
        const res = await fetch('api.php?action=properties', { 
          method: 'POST', 
          headers: { 'Content-Type': 'application/json' }, 
          body: JSON.stringify(payload) 
        });
        
        if (!res.ok) {
          throw new Error('Failed to save properties');
        }
        
        const data = await res.json();
        appendLog('Server properties saved successfully');
      } catch (error) {
        appendLog('Error saving server properties: ' + error.message);
      } finally {
        savePropertiesBtn.disabled = false;
      }
    });
    
    // Load server properties if server exists
    async function loadServerProperties() {
      try {
        const serverDir = document.getElementById('serverDir').value;
        const res = await fetch(`api.php?action=properties&serverDir=${encodeURIComponent(serverDir)}`);
        
        if (!res.ok) {
          return; // Server properties file might not exist yet
        }
        
        const data = await res.json();
        if (data.properties) {
          document.getElementById('serverMotd').value = data.properties.motd || 'A Minecraft Server';
          document.getElementById('serverPort').value = data.properties['server-port'] || '25565';
          document.getElementById('difficulty').value = data.properties.difficulty || 'easy';
          document.getElementById('gamemode').value = data.properties.gamemode || 'survival';
          document.getElementById('maxPlayers').value = data.properties['max-players'] || '20';
          document.getElementById('pvp').checked = data.properties.pvp === 'true';
          document.getElementById('onlineMode').checked = data.properties['online-mode'] === 'true';
        }
      } catch (error) {
        console.error('Error loading server properties:', error);
      }
    }
    
    // Try to load properties when server directory changes
    document.getElementById('serverDir').addEventListener('change', loadServerProperties);
  </script>
</body>
</html>