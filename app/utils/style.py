class Colors:
    """
    A class to define ANSI color codes for terminal text formatting.
    """

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    ORANGE = "\033[33m"
    CYAN = "\033[36m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[35m"
    WHITE = "\033[97m"
    RESET = "\033[0m"

    @staticmethod
    def text(text, color=GREEN):
        """
        Apply the specified color to the text.

        Args:
            text (str): The text to colorize.
            color (str): The color code to apply. Default is GREEN.

        Returns:
            str: The colorized text formatting.
        """
        return f"{color}{text}{Colors.RESET}"

class TextFormat:
    """
    A class to define text formatting options for terminal text.
    """

    ITALIC = "\033[3m"
    RESET = "\033[0m"

    @staticmethod
    def text(text, format=ITALIC):
        """
        Apply the specified format to the text.

        Args:
            text (str): The text to format.
            format (str): The format code to apply. Default is ITALIC.

        Returns:
            str: The formatted text.
        """
        return f"{format}{text}{TextFormat.RESET}"
