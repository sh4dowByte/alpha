from setuptools import setup, find_namespace_packages

setup(
    name="alpha", 
    version="1.0.0", 
    packages=find_namespace_packages(),
    py_modules=["alpha"], 
    install_requires=[
        "rich",
        "pyperclip",
        "tabulate",
        "prompt_toolkit",
    ],
    entry_points={
        'console_scripts': [
            'alpha=alpha:main', 
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12', 
    author="sh4dowByte", 
    author_email="Ahmad Juhdi <ahmadjuhdi007@gmail.com>",
    long_description="""
        If you're on Linux, make sure to install 'xclip' or 'xsel' for clipboard functionality.
        You can install these with the following commands:
        
        sudo apt-get install xclip
        # or
        sudo apt-get install xsel
        
        These are required for pyperclip to function properly.
    """,
)
