import sys
import socket
import json
import threading
import time
import random
import string
#messegas = [" ", " ", " ", " ", " "]

class ChatClient:
    def __init__(self, host='localhost', port=5000, callback=None):
        self.server_address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('',0))
        self.client_address = self.socket.getsockname()
        self.running = False
        self.username = None
        self.callback = callback
        self.messegas = [" ", " ", " ", " ", " "]

    def connect(self, username):
        print("Starting Connect")
        """Send connection request to server"""
        self.username = username
        connect_message = {
            "type": "connect",
            "client_name": self.username,
            "client_port": self.client_address[1],
            "content": ""
        }
        self._send_message(connect_message)
        print("Connected")

    def start(self):
        """Start the client and listen for messages"""
        self.running = True
        # Start receive thread
        receive_thread = threading.Thread(target=self._receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

    def chat_message(self, text):
        """send chat message to server"""
        message_dict = {
            "type": "chat",
            "client_name": self.username,
            "content": text
        }
        self._send_message(message_dict)


    def _send_message(self, message_dict):
        """Send JSON message to server"""
        try:

            message_bytes = json.dumps(message_dict).encode('utf-8')

            self.socket.sendto(message_bytes, self.server_address)
        except Exception as e:
            print(f"Error sending message: {e}")

    def _receive_messages(self):
        print("recive function")
        """Receive and handle incoming messages"""
        while self.running:
            try:
                print("befor data recive")
                data, _  = self.socket.recvfrom(1024)
                print("recived messag converting to json")
                message = json.loads(data.decode('utf-8'))
                print("converted to json" )

                if self.callback:
                    self.callback(message)
                else:
                    # Default handling if no callback provided
                    if message['type'] == 'connection_ack':
                        print(f"Connected successfully. {message['active_clients']} active clients")
                    elif message['type'] == 'chat':
                        print("chat1")
                        del self.messegas[0]
                        self.messegas.append(message['content'])
                        print("chat2")
                        print("recived message")
                        print(f"{message['from']}: {message['message']}")
                    elif message['type'] == 'message_ack':
                        print(f"Message sent to {message['message']}")
                    elif message['type'] == 'error':
                        print(f"Error: {message['message']}")

            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")

