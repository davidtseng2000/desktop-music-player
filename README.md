# 🎵 Desktop Music Player (DMP)

A sleek, modern desktop music player built with **Python**, **PyQt5**, and **VLC**.  
This is a Vibe Coding practice project developed with the help of AI (ChatGPT).

---

## ✨ Features

- 🎧 Play music from a selected folder (`.mp3`, `.wav`, `.flac`)
- ⏯️ Play/Pause, ⏮️ Previous, ⏭️ Next track controls
- 🔁 Repeat and 🔀 Shuffle modes
- ⏱️ Track progress bar and time display
- 📁 Load folder with music files
- 🎚️ Volume control
- ⚡ Adjustable playback speed (0.5x ~ 2.0x)
- 📜 Playlist with double-click to play
- 🌈 Stylish and responsive GUI (Nord theme)

---

## 🖥️ Screenshot

![App Screenshot](screenshot.png)

---

## 🧩 Requirements

Before running or building this app, make sure you have the following:

### ✅ Python Packages
- Python 3.7 or later
- [`PyQt5`](https://pypi.org/project/PyQt5/)
- [`python-vlc`](https://pypi.org/project/python-vlc/)

### ✅ External Program
VLC media player — must be installed and accessible in:

Windows default:
`C:\Program Files\VideoLAN\VLC`

If VLC is installed elsewhere, modify the `os.add_dll_directory(...)` line in `dmp.py`.

## Build as Executable
You can build the program into a standalone `.exe` using **PyInstaller**:

`pip install pyinstaller
pyinstaller --noconfirm --windowed --onefile --icon=dmp_logo.ico --add-data "dmp_logo.png;." dmp.py`

After building, you’ll find the `.exe` inside the `dist/` directory.

If the app icon doesn’t show up on the desktop, make sure `.ico` file was specified correctly during packaging.

## 🧪 Development Mode
To run directly from Python:
`python dmp.py`

## 💡 About This Project
This project was created as a Vibe Coding practice — a coding style where humans and AI collaborate creatively.

Code generated with the help of OpenAI’s ChatGPT.

Feel free to fork, modify, and enhance it further!





