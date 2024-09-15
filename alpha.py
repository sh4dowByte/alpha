import socket
import threading
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import HTML

from app.utils.style import Colors
from app.utils.helper import banner

from app.config import Tcp
from app.payloads import PayloadGenerator
from app.sessions import SessionsManager

def show_help():
    """
    Display help information for the available commands.
    """
    help_text = """
    Available Commands:
    - sessions: Show the list of active sessions.
    - shell <session_id>: Connect to a session by specifying the session ID.
    - kill <session_id>: Terminate a session by specifying the session ID.
    - payload: Generate the payload.
    - help: Display this help message.
    """
    print(help_text)

def main():
    """
    Main function to start the Alpha application.

    This function initializes the TCP server, sets up the sessions manager and payload generator,
    starts background threads to accept and monitor connections, and handles user input from
    the command prompt.

    The application performs the following tasks:
    - Displays the application banner.
    - Configures the TCP listener on the specified port.
    - Starts threads for accepting incoming connections and monitoring existing sessions.
    - Provides a command prompt for user interaction to manage sessions and configure payloads.
    """
    # Show banner app
    banner()

    # Create and configure the TCP listener
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('0.0.0.0', Tcp.port))
    listener.listen(5)

    # Initialize session manager and payload generator
    sessions_manager = SessionsManager()
    payload_generator = PayloadGenerator()

    print(f"[{Colors.text('0.0.0.0', Colors.YELLOW)}:{Colors.text(Tcp.port, Colors.YELLOW)}]::TCP Multi-Handler\n")

    # Start thread to accept incoming connections
    threading.Thread(target=sessions_manager.accept_connections, args=(listener,), daemon=True).start()
    # Start thread to monitor all active sessions
    threading.Thread(target=sessions_manager.monitor_all_connections, daemon=True).start()

    # Create a prompt session for user input
    prompt = PromptSession(history=InMemoryHistory())

    while True:
        try:
            # Wait for user input from the prompt
            command = prompt.prompt(HTML('<style fg="#FFBD4A">Alpha# </style>')).strip()

            if not command:
                # If the command is empty, skip to the next loop iteration
                continue

            if command == "sessions":
                # Show the list of active sessions
                sessions_manager.show_sessions()
            elif command.startswith("shell "):
                # Connect to a session based on the provided session ID
                session_id = command.split(" ")[1]
                sessions_manager.connect_to_session(session_id)
            elif command.startswith("kill "):
                # Terminate a session based on the provided session ID
                session_id = command.split(" ")[1]
                sessions_manager.kill_session(session_id)
            elif command == "payload":
                # Configure payload settings
                payload_generator.configure_payload()
            elif command == "help":
                # Display help information
                show_help()
            else:
                # If the command is not recognized, print an error message
                print('Error: Command not recognized.')

        except (EOFError, KeyboardInterrupt):
            # Handle end-of-file and keyboard interrupt exceptions
            break

if __name__ == "__main__":
    main()
