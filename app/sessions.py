import re
import socket
import threading
import uuid
import time
from tabulate import tabulate

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text

from app.utils.style import Colors, TextFormat

class Session:
    def __init__(self, conn, server_name='', os='', user='', ip=''):
        """
        Initialize a new session.

        Args:
            conn (socket.socket): The connection object for this session.
            server_name (str): The name of the server.
            os (str): The operating system name.
            user (str): The user name.
            ip (str): The IP address of the client.
        """
        self.uuid = str(uuid.uuid4())
        self.conn = conn
        self.server_name = server_name
        self.os = os
        self.user = user
        self.ip = ip
        self.active = False  # Active status for the session
        self.is_online = True  # Online status for the session

class SessionsManager:
    def __init__(self):
        """
        Initialize the SessionsManager with an empty session dictionary and a lock.
        """
        self.sessions = {}
        self.sessions_lock = threading.Lock()

    def handle_session(self, session):
        """
        Handle an active session, allowing command input and processing.

        Args:
            session (Session): The session object to handle.
        """
        prompt_session = PromptSession(history=InMemoryHistory())
        
        with self.sessions_lock:
            session.active = True  # Mark session as active
        
        first = True
        shell_prompt_detected = False
        shell_prompt = None
        
        # List of dangerous commands to watch out for
        dangerous_commands = ['rm -rf', 'dd if=', 'mkfs', 'chmod 777', 'shutdown', 'reboot', 'as', 'htop']
        
        while True:
            try:
                if first:
                    first = False
                    command = ''
                else:
                    command = prompt_session.prompt('')
                    command = command.strip()
                    
                    # Check for dangerous commands
                    if any(dangerous_command in command for dangerous_command in dangerous_commands):
                        print("Dangerous input detected. This command may break the shell session.")
                        continue  # Skip sending this command
                    
                if command == "exit":
                    print(f"Exiting session {session.uuid}")
                    break

                session.conn.sendall((command + "\n").encode())
                buffer = ""
                while True:
                    response = session.conn.recv(1048).decode()
                    if not response:
                        print(f"Connection lost with {session.uuid}")
                        break
                    
                    buffer += response
                    print(response, end='')

                    # Detect shell prompt based on common patterns
                    if not shell_prompt_detected:
                        if '#' in buffer:
                            shell_prompt = '#'
                            shell_prompt_detected = True
                        elif '$' in buffer:
                            shell_prompt = '$'
                            shell_prompt_detected = True
                    
                    # Break the loop if shell prompt detected
                    if shell_prompt_detected and shell_prompt in buffer:
                        break
            
            except (EOFError, KeyboardInterrupt):
                break
            except (TimeoutError):
                print('TIMEOUT')
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        with self.sessions_lock:
            session.active = False  # Mark session as inactive

    def is_duplicate_session(self, ip, os_name, user_name, server_name):
        """
        Check if a session with the same IP, OS, user, and server name already exists.

        Args:
            ip (str): The IP address of the client.
            os_name (str): The operating system name.
            user_name (str): The user name.
            server_name (str): The server name.

        Returns:
            bool: True if a duplicate session is found, otherwise False.
        """
        with self.sessions_lock:
            for session in self.sessions.values():
                if session.ip == ip and session.os == os_name and session.user == user_name and session.server_name == server_name:
                    return True
        return False

    def get_os_and_user(self, output):
        """
        Extract the OS, user, and server name from the output.

        Args:
            output (str): The output string to parse.

        Returns:
            tuple: A tuple containing OS name, user name, and server name.
        """
        match = re.search(r'hostname="([^"]+)",user="([^"]+)",server="([^"]+)"', output)

        if match:
            server_name, user_name, os_name = match.groups()
            return os_name, user_name, server_name
        else:
            return "", "", ""

    def accept_connections(self, listener):
        """
        Accept new connections and manage existing sessions.

        Args:
            listener (socket.socket): The socket object used to listen for incoming connections.
        """
        while True:
            conn, addr = listener.accept()
            ip, port = addr

            command = 'echo hostname=\\"$(hostname)\\",'
            command += 'user=\\"$(whoami)\\",'
            command += 'server=\\"$(uname)\\"'
            command += '\n'
            conn.sendall(command.encode())

            time.sleep(1)

            response = conn.recv(2048).decode(errors='ignore')
            os, user, server_name = self.get_os_and_user(response)

            for session_id, session in self.sessions.items():
                if session.ip == ip and session.os == os and session.user == user and session.server_name == server_name:
                    if not session.is_online:  # If session exists and is offline
                        session.conn.close()  # Close old connection
                        session.conn = conn  # Update connection
                        session.is_online = True  # Mark as online
                        self.update_dynamic_text(f"[+] Connection updated for session {session_id} {os} {user}@{server_name} {ip}")
                        break

            if self.is_duplicate_session(ip, os, user, server_name):
                continue

            session_id = str(uuid.uuid4())
            session = Session(conn, server_name, os, user, ip)
            with self.sessions_lock:
                self.sessions[session_id] = session

            self.update_dynamic_text(f"[+] Connection accepted from <style fg=\"lime\">{session_id}</style> {os} {user}@{server_name} {ip}")

    def show_sessions(self):
        """
        Display the current active sessions in a tabulated format.
        """
        with self.sessions_lock:
            table = [(uuid, session.ip, session.server_name, session.user, session.os, Colors.text('Online') if session.is_online else Colors.text('Offline', Colors.RED)) for uuid, session in self.sessions.items()]
            print('\n')
            print(tabulate(table, headers=["UUID", "Ip Address", "Server Name", "User", "OS", "Status"], tablefmt="pipe"))
            print('\n')

    def connect_to_session(self, session_id):
        """
        Connect to a specific session based on its UUID.

        Args:
            session_id (str): The UUID of the session to connect to.
        """
        with self.sessions_lock:
            session = self.sessions.get(session_id)
        
        if not session:
            print(f"Session with UUID {session_id} not found.")
            return

        if session.is_online == False:
            print(f"Session with UUID {session_id} is offline.")
            return

        print(TextFormat.text(Colors.text(f"Connected")))
        self.handle_session(session)

    def kill_session(self, session_id):
        """
        Terminate a specific session based on its UUID.

        Args:
            session_id (str): The UUID of the session to terminate.
        """
        with self.sessions_lock:
            session = self.sessions.pop(session_id, None)

        if session:
            session.conn.close()
            print(f"Session with UUID {session_id} has been terminated.")
        else:
            print(f"Session with UUID {session_id} not found.")

    def monitor_all_connections(self):
        """
        Monitor all active sessions to check for lost connections and update their status.
        """
        while True:
            time.sleep(5)  # Check interval
            
            with self.sessions_lock:
                for session_id, session in list(self.sessions.items()):
                    # Skip active sessions
                    if session.active:
                        continue

                    # Check offline sessions
                    if not session.is_online:
                        continue
                    
                    try:
                        session.conn.settimeout(4)  # Timeout 4 seconds
                        session.conn.sendall(b'\n')  # Send dummy data

                        time.sleep(1)  # Check interval
                        
                        # Receive data to ensure connection is still active
                        response = session.conn.recv(2024).decode(errors='ignore').strip()
                        
                        # If no response, assume connection is lost
                        if not response:
                            raise ConnectionError("No response received")

                    except (socket.error, socket.timeout, ConnectionError) as e:
                        self.update_dynamic_text(f"[-] Connection lost with {session_id}: {e}")
                        session.is_online = False  # Mark session as not online
                        session.conn.close()  # Close connection

    def update_dynamic_text(self, dynamic_text):
        """
        Update and display dynamic text without disrupting user input.

        Args:
            dynamic_text (str): The text to display dynamically.
        """
        print_formatted_text(HTML(f'\n{dynamic_text}\n'))
