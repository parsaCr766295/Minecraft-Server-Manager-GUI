from flask import Flask, render_template, request, jsonify, Response
import json
import threading
import queue
import time
from mc_server_setup import (
    fetch_json, get_version_info, ensure_dir, sha1_file, 
    download_file, write_eula, write_start_script, 
    check_java_version, start_server, PISTON_META_MANIFEST
)
import os
import subprocess
from websocket_server import WebSocketServer

app = Flask(__name__)

# Global state for progress tracking
progress_queue = queue.Queue()
server_process = None

# Initialize WebSocket server with auto port selection
websocket_server = WebSocketServer(host='0.0.0.0', port=8765, max_retry_ports=20)

# Start the WebSocket server
websocket_server.start()

# Get the actual port being used
websocket_port = websocket_server.get_port()

# Store WebSocket info for the frontend
websocket_info = {
    "host": "0.0.0.0",
    "port": websocket_port
}

def get_available_versions():
    """Get list of available Minecraft versions"""
    try:
        manifest = fetch_json(PISTON_META_MANIFEST)
        versions = manifest.get("versions", [])
        latest_release = manifest.get("latest", {}).get("release", "")
        latest_snapshot = manifest.get("latest", {}).get("snapshot", "")
        
        # Filter to releases and recent snapshots for GUI
        releases = [v for v in versions if v.get("type") == "release"][:20]  # Last 20 releases
        snapshots = [v for v in versions if v.get("type") == "snapshot"][:10]  # Last 10 snapshots
        
        return {
            "latest_release": latest_release,
            "latest_snapshot": latest_snapshot,
            "releases": releases,
            "snapshots": snapshots
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    # Pass WebSocket port to the template
    return render_template('index.html', websocket_port=websocket_port)

# Add a new route to get WebSocket info
@app.route('/api/websocket-info')
def api_websocket_info():
    return jsonify({
        "host": websocket_info["host"] if websocket_info["host"] != "0.0.0.0" else request.host.split(':')[0],
        "port": websocket_info["port"]
    })

@app.route('/api/versions')
def api_versions():
    return jsonify(get_available_versions())

@app.route('/api/java-check')
def api_java_check():
    ok, output = check_java_version()
    return jsonify({"ok": ok, "output": output})

# Helper function to send updates via WebSocket
def send_websocket_update(data):
    """Send update via WebSocket"""
    try:
        websocket_server.send_message(data)
    except Exception as e:
        print(f"WebSocket error: {e}")

# Modified report_progress function to send updates via both SSE and WebSocket
def report_progress(data):
    """Report progress via both SSE and WebSocket"""
    progress_queue.put(data)
    send_websocket_update(data)

# Setup worker function that uses WebSocket for updates
def setup_worker_with_websocket(data):
    try:
        report_progress({"type": "progress", "message": "Starting setup...", "percent": 0})
        
        # Parse parameters
        version = data.get('version', 'latest')
        server_dir = os.path.abspath(data.get('serverDir', os.path.join(os.getcwd(), "mc_server")))
        min_memory = data.get('minMemory', '1G')
        max_memory = data.get('maxMemory', '2G')
        accept_eula = data.get('acceptEula', False)
        force_download = data.get('forceDownload', False)
        
        ensure_dir(server_dir)
        report_progress({"type": "progress", "message": f"Created directory: {server_dir}", "percent": 10})
        
        # Get version info
        report_progress({"type": "progress", "message": f"Resolving version '{version}'...", "percent": 20})
        version_id, server_download = get_version_info(version)
        url = server_download.get("url")
        expected_sha1 = server_download.get("sha1")
        
        report_progress({"type": "progress", "message": f"Resolved version: {version_id}", "percent": 30})
        
        # Download server.jar
        jar_path = os.path.join(server_dir, "server.jar")
        if os.path.exists(jar_path) and not force_download:
            report_progress({"type": "progress", "message": "server.jar already exists, skipping download", "percent": 60})
        else:
            report_progress({"type": "progress", "message": "Downloading server.jar...", "percent": 40})
            download_file(url, jar_path)
            report_progress({"type": "progress", "message": "Download complete", "percent": 60})
        
        # Verify SHA1
        if expected_sha1 and os.path.exists(jar_path):
            report_progress({"type": "progress", "message": "Verifying SHA1...", "percent": 70})
            actual_sha1 = sha1_file(jar_path)
            if actual_sha1.lower() != expected_sha1.lower():
                raise RuntimeError(f"SHA1 mismatch for server.jar")
            report_progress({"type": "progress", "message": "SHA1 verified", "percent": 80})
        
        # Write EULA
        eula_path = write_eula(server_dir, accept_eula)
        report_progress({"type": "progress", "message": f"EULA written to {os.path.basename(eula_path)}", "percent": 90})
        
        # Write start scripts
        bat_path, sh_path = write_start_script(server_dir, min_memory, max_memory, True)  # Always nogui for web
        report_progress({"type": "progress", "message": "Created start scripts", "percent": 95})
        
        report_progress({"type": "success", "message": "Setup complete!", "percent": 100})
        
    except Exception as e:
        report_progress({"type": "error", "message": str(e), "percent": 0})

@app.route('/api/setup', methods=['POST'])
def api_setup():
    data = request.json
    
    # Start setup in background thread
    threading.Thread(target=lambda: setup_worker_with_websocket(data), daemon=True).start()
    
    return jsonify({"status": "started"})

@app.route('/api/progress')
def api_progress():
    def generate():
        while True:
            try:
                # Get progress update with timeout
                progress = progress_queue.get(timeout=1)
                yield f"data: {json.dumps(progress)}\\n\\n"
                if progress.get("type") in ["success", "error"]:
                    break
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'type': 'heartbeat'})}\\n\\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/start-server', methods=['POST'])
def api_start_server():
    global server_process
    
    data = request.json
    server_dir = os.path.abspath(data.get('serverDir', os.path.join(os.getcwd(), "mc_server")))
    min_memory = data.get('minMemory', '1G')
    max_memory = data.get('maxMemory', '2G')
    
    if server_process and server_process.poll() is None:
        return jsonify({"error": "Server is already running"}), 400
    
    jar_path = os.path.join(server_dir, "server.jar")
    if not os.path.isfile(jar_path):
        return jsonify({"error": "server.jar not found. Run setup first."}), 400
    
    try:
        cmd = [
            "java",
            f"-Xms{min_memory}",
            f"-Xmx{max_memory}",
            "-jar",
            "server.jar",
            "nogui"
        ]
        
        server_process = subprocess.Popen(
            cmd,
            cwd=server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        return jsonify({"status": "started", "pid": server_process.pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop-server', methods=['POST'])
def api_stop_server():
    global server_process
    
    if not server_process or server_process.poll() is not None:
        return jsonify({"error": "Server is not running"}), 400
    
    try:
        server_process.terminate()
        server_process.wait(timeout=10)
        return jsonify({"status": "stopped"})
    except subprocess.TimeoutExpired:
        server_process.kill()
        return jsonify({"status": "force_stopped"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/server-status')
def api_server_status():
    global server_process
    
    if server_process is None:
        return jsonify({"status": "not_started"})
    elif server_process.poll() is None:
        return jsonify({"status": "running", "pid": server_process.pid})
    else:
        return jsonify({"status": "stopped", "exit_code": server_process.returncode})

@app.route('/api/server-logs')
def api_server_logs():
    global server_process
    
    def generate():
        if server_process and server_process.stdout:
            for line in iter(server_process.stdout.readline, ''):
                if line:
                    yield f"data: {json.dumps({'log': line.strip()})}\\n\\n"
                if server_process.poll() is not None:
                    break
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/properties', methods=['GET', 'POST'])
def api_properties():
    if request.method == 'POST':
        data = request.json
        server_dir = data.get('serverDir', '')
        properties = data.get('properties', {})
        
        if not server_dir:
            return jsonify({'error': 'Server directory is required'}), 400
        
        server_dir = os.path.abspath(server_dir)
        properties_path = os.path.join(server_dir, 'server.properties')
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(server_dir, exist_ok=True)
            
            # Write properties to file
            with open(properties_path, 'w') as f:
                for key, value in properties.items():
                    f.write(f"{key}={value}\n")
            
            return jsonify({'status': 'ok'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:  # GET
        server_dir = request.args.get('serverDir', '')
        if not server_dir:
            return jsonify({'error': 'Server directory is required'}), 400
        
        server_dir = os.path.abspath(server_dir)
        properties_path = os.path.join(server_dir, 'server.properties')
        
        if not os.path.exists(properties_path):
            return jsonify({'error': 'Properties file not found'}), 404
        
        try:
            properties = {}
            with open(properties_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        properties[key.strip()] = value.strip()
            
            return jsonify({'properties': properties})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Helper function to send updates via WebSocket
def send_websocket_update(data):
    """Send update to all connected WebSocket clients"""
    websocket_server.send_message(data)

# Update progress reporting to also send via WebSocket
def report_progress(data):
    """Report progress via both SSE and WebSocket"""
    progress_queue.put(data)
    send_websocket_update(data)

# Update setup_worker to use the new report_progress function
def setup_worker_with_websocket(data):
    try:
        report_progress({"type": "progress", "message": "Starting setup...", "percent": 0})
        
        # Parse parameters
        version = data.get('version', 'latest')
        server_dir = os.path.abspath(data.get('serverDir', os.path.join(os.getcwd(), "mc_server")))
        min_memory = data.get('minMemory', '1G')
        max_memory = data.get('maxMemory', '2G')
        accept_eula = data.get('acceptEula', False)
        force_download = data.get('forceDownload', False)
        
        ensure_dir(server_dir)
        report_progress({"type": "progress", "message": f"Created directory: {server_dir}", "percent": 10})
        
        # Get version info
        report_progress({"type": "progress", "message": f"Resolving version '{version}'...", "percent": 20})
        version_id, server_download = get_version_info(version)
        url = server_download.get("url")
        expected_sha1 = server_download.get("sha1")
        
        report_progress({"type": "progress", "message": f"Resolved version: {version_id}", "percent": 30})
        
        # Download server.jar
        jar_path = os.path.join(server_dir, "server.jar")
        if os.path.exists(jar_path) and not force_download:
            report_progress({"type": "progress", "message": "server.jar already exists, skipping download", "percent": 60})
        else:
            report_progress({"type": "progress", "message": "Downloading server.jar...", "percent": 40})
            download_file(url, jar_path)
            report_progress({"type": "progress", "message": "Download complete", "percent": 60})
        
        # Verify SHA1
        if expected_sha1 and os.path.exists(jar_path):
            report_progress({"type": "progress", "message": "Verifying SHA1...", "percent": 70})
            actual_sha1 = sha1_file(jar_path)
            if actual_sha1.lower() != expected_sha1.lower():
                raise RuntimeError(f"SHA1 mismatch for server.jar")
            report_progress({"type": "progress", "message": "SHA1 verified", "percent": 80})
        
        # Write EULA
        eula_path = write_eula(server_dir, accept_eula)
        report_progress({"type": "progress", "message": f"EULA written to {os.path.basename(eula_path)}", "percent": 90})
        
        # Write start scripts
        bat_path, sh_path = write_start_script(server_dir, min_memory, max_memory, True)  # Always nogui for web
        report_progress({"type": "progress", "message": "Created start scripts", "percent": 95})
        
        report_progress({"type": "success", "message": "Setup complete!", "percent": 100})
        
    except Exception as e:
        report_progress({"type": "error", "message": str(e), "percent": 0})

# Update the api_setup route to use the new setup worker
# Function is already defined above

# Update server log handling to also send via WebSocket
def handle_server_output(process):
    """Handle server output and send to both SSE and WebSocket"""
    if process and process.stdout:
        for line in iter(process.stdout.readline, ''):
            if line:
                log_data = {"log": line.strip()}
                progress_queue.put({"type": "log", "data": log_data})
                send_websocket_update({"type": "log", "data": log_data})
            if process.poll() is not None:
                break

# Update server start to use the new output handler
# Function is already defined above
        


if __name__ == '__main__':
    print("Starting Minecraft Server Setup Web GUI...")
    print("Starting WebSocket server on ws://0.0.0.0:8765")
    websocket_server.start()
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)