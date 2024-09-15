from app.config import Alpha
from app.utils.style import Colors, TextFormat

def banner():
    """
    Display a banner with a version number and random text.

    This function prints a stylized banner including a version number and a randomly chosen text
    in different colors.

    Returns:
        None
    """
    banner = rf"""
    {Colors.YELLOW}
        ___    __      __         
       /   |  / /___  / /_  ____ _
      / /| | / / __ \/ __ \/ __ `/
     / ___ |/ / /_/ / / / / /_/ / 
    /_/  |_/_/ .___/_/ /_/\__,_/    v{Alpha.version}
            /_/                     {Colors.RESET}
                         {TextFormat.text('Reverse Shell')}
 
    """
    print(banner)
