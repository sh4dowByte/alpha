import os
import pyperclip
import importlib.util
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion

from app.utils.style import Colors

class PayloadGenerator:
    def __init__(self, folder_path='app/payloads'):
        """
        Initialize the PayloadGenerator with the given folder path to search for payload files.

        :param folder_path: The path to the folder containing payload files.
        """
        self.payloads = self.get_payloads_from_folder(folder_path)
        self.payload_completer = PayloadCompleter(self.payloads)
        self.prompt_session = PromptSession(completer=self.payload_completer, auto_suggest=AutoSuggestFromHistory())

    def extract_description_from_file(self, file_path):
        """
        Extract the description of a payload from a Python file.

        :param file_path: The path to the Python file.
        :return: The description of the payload if available, otherwise a default message.
        """
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'Payload'):
            payload_class = getattr(module, 'Payload')
            if hasattr(payload_class, 'info'):
                info = getattr(payload_class, 'info')
                if isinstance(info, dict):
                    return info.get('Description', 'No description available')
        
        return 'No description available'

    def get_payloads_from_folder(self, folder_path='app/payloads'):
        """
        Retrieve a list of payloads from the specified folder.

        :param folder_path: The path to the folder containing payload files.
        :return: A list of dictionaries containing payload paths and their descriptions.
        """
        payloads = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                    payload_name = os.path.splitext(relative_path)[0].replace(os.path.sep, '/')
                    
                    file_path = os.path.join(root, file)
                    description = self.extract_description_from_file(file_path)
                    
                    payloads.append({
                        'path': payload_name,
                        'description': description
                    })
        return payloads

    def load_payload(self, module_name, class_name='Payload'):
        """
        Load a payload class from a Python module.

        :param module_name: The name of the module containing the payload class.
        :param class_name: The name of the payload class.
        :return: An instance of the payload class or None if the module or class is not found.
        """
        module_name = module_name.replace('.', '/')
        module_path = f'app/payloads/{module_name}.py'
        if not os.path.exists(module_path):
            print(f"Payload module {module_name} not found.")
            return None

        spec = importlib.util.spec_from_file_location(class_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return getattr(module, class_name)()

    def configure_payload(self):
        """
        Configure a payload by prompting the user to enter parameters and generate the final payload.
        """
        print("Available payloads:")
        payload_name = self.prompt_session.prompt("Enter payload (e.g., linux/tcp/bash_linux): ").strip()

        payload = self.load_payload(payload_name.replace('/', '.'))
        if payload is None:
            return

        for param, default_value in payload.parameters.items():
            value = input(f"Enter {param} (default {default_value}): ").strip()
            if value == "":
                value = default_value
            payload.parameters[param] = value

        final_payload = payload.data
        for param, value in payload.parameters.items():
            final_payload = final_payload.replace(f'*{param.upper()}*', value)

        print(f"Generated Payload: {Colors.text(final_payload)}")

        pyperclip.copy(final_payload)
        print(Colors.text("Payload has been copied to the clipboard!", Colors.WHITE))

class PayloadCompleter(Completer):
    def __init__(self, payloads):
        """
        Initialize the PayloadCompleter with a list of payloads.

        :param payloads: A list of payloads to be used for autocompletion.
        """
        self.payloads = payloads

    def get_completions(self, document, complete_event):
        """
        Generate autocompletion suggestions based on the text before the cursor.

        :param document: The current document being edited.
        :param complete_event: Event triggered by autocompletion.
        :return: An iterator of Completion objects based on available payloads.
        """
        text = document.text_before_cursor
        for payload in self.payloads:
            if payload['path'].startswith(text):
                description = payload['description']
                # Format description with color
                formatted_description = HTML(f'<style fg="cyan">{description}</style>')
                yield Completion(payload['path'], start_position=-len(text), display_meta=formatted_description)
