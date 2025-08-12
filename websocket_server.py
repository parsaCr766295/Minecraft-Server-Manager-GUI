import asyncio
import websockets
import json
import threading
import queue
import socket
import time

class WebSocketServer:
    def __init__(self, host='localhost', port=8765, max_retry_ports=10):
        self.host = host
        self.port = port
        self.max_retry_ports = max_retry_ports
        self.clients = set()
        self.message_queue = queue.Queue()
        self.running = False
        self.server = None
        self.thread = None
    
    async def handler(self, websocket):
        # Register client
        self.clients.add(websocket)
        try:
            # Handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    # Process message if needed
                    print(f"Received message: {data}")
                    
                    # Echo back for testing
                    await websocket.send(json.dumps({"type": "echo", "data": data}))
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Unregister client
            self.clients.remove(websocket)
    
    async def broadcast(self, message):
        if not self.clients:
            return
        
        # Convert message to JSON string if it's a dict
        if isinstance(message, dict):
            message = json.dumps(message)
        
        # Send to all connected clients
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.clients.remove(client)
    
    async def message_sender(self):
        while self.running:
            try:
                # Check for messages in the queue with a timeout
                try:
                    message = self.message_queue.get(timeout=0.1)
                    await self.broadcast(message)
                    self.message_queue.task_done()
                except queue.Empty:
                    # No message in queue, just wait a bit
                    await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error in message sender: {e}")
    
    def send_message(self, message):
        """Add message to queue to be sent to all clients"""
        self.message_queue.put(message)
    
    async def start_server(self):
        self.running = True
        
        # Try to start the server with the initial port
        current_port = self.port
        retry_count = 0
        
        while retry_count < self.max_retry_ports:
            try:
                self.server = await websockets.serve(self.handler, self.host, current_port)
                # Start the message sender task
                asyncio.create_task(self.message_sender())
                print(f"WebSocket server started at ws://{self.host}:{current_port}")
                # Update the port if it changed
                self.port = current_port
                await self.server.wait_closed()
                break
            except OSError as e:
                if e.errno == 10048:  # Address already in use
                    print(f"Port {current_port} is already in use, trying next port...")
                    current_port += 1
                    retry_count += 1
                else:
                    print(f"Failed to start WebSocket server: {e}")
                    break
        
        if retry_count >= self.max_retry_ports:
            print(f"Failed to find an available port after {self.max_retry_ports} attempts")
    
    def start(self):
        """Start the WebSocket server in a separate thread"""
        def run_server():
            try:
                asyncio.run(self.start_server())
            except Exception as e:
                print(f"WebSocket server error: {e}")
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the WebSocket server"""
        self.running = False
        if self.server:
            self.server.close()
            # Give it a moment to close connections
            asyncio.run(asyncio.sleep(0.5))
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        print("WebSocket server stopped")

    def get_port(self):
        """Return the actual port the server is running on"""
        return self.port

# Example usage
if __name__ == "__main__":
    server = WebSocketServer()
    server.start()
    
    try:
        # Keep the main thread running
        while True:
            cmd = input("Enter a message to broadcast (or 'exit' to quit): ")
            if cmd.lower() == 'exit':
                break
            server.send_message({"type": "broadcast", "message": cmd})
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()