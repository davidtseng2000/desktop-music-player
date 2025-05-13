import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QFileDialog, QListWidget, QHBoxLayout, QMessageBox, QSlider, QStyle, QFrame,
    QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QIcon
import vlc

# 設定 VLC DLL 路徑
os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop Music Player")
        self.setMinimumSize(400, 500)  # 設定最小視窗大小
        self.setAttribute(Qt.WA_TranslucentBackground)  # 開啟透明背景
        self.setWindowFlags(Qt.FramelessWindowHint)  # 無邊框
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 可拉伸
        logo_path = os.path.join(os.path.dirname(__file__), "dmp_logo.png")
        self.setWindowIcon(QIcon(logo_path))

        # 主題相關變數
        self.current_theme = "translucent"  # 預設主題
        self.themes = {
            "translucent": {
                "background": "rgba(30, 30, 30, 150)",
                "text": "white",
                "button_hover": "rgba(255, 255, 255, 30)",
                "slider_bg": "rgba(255, 255, 255, 30)",
                "combo_bg": "rgba(255, 255, 255, 30)",
                "selected_bg": "rgba(0, 0, 0, 100)"
            },
            "dark": {
                "background": "rgb(30, 30, 30)",
                "text": "white",
                "button_hover": "rgba(255, 255, 255, 20)",
                "slider_bg": "rgba(255, 255, 255, 20)",
                "combo_bg": "rgba(255, 255, 255, 20)",
                "selected_bg": "rgba(0, 0, 0, 100)"
            },
            "gentle_blue": {
                "background": "rgb(41, 50, 65)",
                "text": "rgb(220, 220, 220)",
                "button_hover": "rgba(100, 149, 237, 30)",
                "slider_bg": "rgba(100, 149, 237, 20)",
                "combo_bg": "rgba(100, 149, 237, 20)",
                "selected_bg": "rgba(100, 149, 237, 50)"
            }
        }

        # 主題切換按鈕
        self.theme_button = QPushButton("🎨 Theme")
        self.theme_button.clicked.connect(self.toggle_theme)

        # 設置初始主題
        self.apply_theme(self.current_theme)

        # VLC 播放器
        self.player = vlc.MediaPlayer('--quiet')   
        self.song_list = []
        self.current_index = -1
        self.repeat = False
        self.shuffle = False
        self.current_speed = 1.0
        self.is_sliding = False
        self.last_position = 0
        self.position_unchanged_count = 0

        # 自訂標題欄
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("title_bar")  # 設置物件名稱以應用樣式
        self.title_bar.setFixedHeight(30)
        self.title_bar.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # 用於視窗拖曳的變數
        self.dragging = False
        self.offset = QPoint()

        self.title_label = QLabel("Desktop Music Player", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 14px;")
        self.title_label.move(10, 5)

        # 關閉、最小化按鈕
        self.close_button = QPushButton("×", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.close)

        self.minimize_button = QPushButton("−", self.title_bar)
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.clicked.connect(self.showMinimized)

        # 按鈕位置調整 - 使用相對位置
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        button_layout.addStretch()
        button_layout.addWidget(self.minimize_button)
        button_layout.addWidget(self.close_button)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)
        title_layout.addWidget(self.title_label)
        title_layout.addLayout(button_layout)

        # VLC 播放器控制元件
        self.label = QLabel("No song loaded", self)
        self.label.setObjectName("songLabel")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumHeight(25)  # 增加高度以適應更大的字體
        self.label.setContentsMargins(0, 0, 0, 0)
        
        # 時間顯示標籤
        self.time_label = QLabel("00:00 / 00:00", self)
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setMinimumHeight(20)  # 增加高度以適應更大的字體
        self.time_label.setContentsMargins(0, 0, 0, 0)

        # 進度條
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        self.progress_slider.setContentsMargins(0, 0, 0, 0)

        # 創建一個容器來包含這三個元素
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(0)  # 移除元素之間的間距
        info_layout.addWidget(self.label)
        info_layout.addWidget(self.time_label)
        info_layout.addWidget(self.progress_slider)

        # 播放速度控制
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(['0.5x', '0.75x', '1.0x', '1.25x', '1.5x', '2.0x'])
        self.speed_combo.setCurrentText('1.0x')
        self.speed_combo.currentTextChanged.connect(self.change_speed)

        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_song)

        self.toggle_playlist_button = QPushButton("▲ Files")
        self.toggle_playlist_button.setCheckable(True)
        self.toggle_playlist_button.setChecked(True)
        self.toggle_playlist_button.clicked.connect(self.toggle_playlist_visibility)

        # 播放控制按鈕
        self.play_button = QPushButton("▶️")  # 播放圖示
        self.play_button.setFixedSize(35, 35)  # 調整為與其他按鈕相同大小
        self.play_button.setObjectName("playButton")  # 添加物件名稱
        self.play_button.setStyleSheet("""
            QPushButton#playButton {
                font-size: 20px;
                border-radius: 17px;
                background: transparent;
                border: none;
                padding: 0px;
                text-align: center;
            }
            QPushButton#playButton:hover {
                background: rgba(255, 255, 255, 30);
                border-radius: 17px;
            }
        """)
        self.play_button.clicked.connect(self.toggle_play)

        self.prev_button = QPushButton("◀◀")  # 上一首圖示
        self.prev_button.setFixedSize(35, 35)
        self.prev_button.setObjectName("prevButton")  # 添加物件名稱
        self.prev_button.setStyleSheet("""
            QPushButton#prevButton {
                font-size: 18px;
                border-radius: 17px;
                background: transparent;
                border: none;
            }
            QPushButton#prevButton:hover {
                background: rgba(255, 255, 255, 30);
                border-radius: 17px;
            }
        """)
        self.prev_button.clicked.connect(self.play_previous)

        self.next_button = QPushButton("▶▶")  # 下一首圖示
        self.next_button.setFixedSize(35, 35)
        self.next_button.setObjectName("nextButton")  # 添加物件名稱
        self.next_button.setStyleSheet("""
            QPushButton#nextButton {
                font-size: 18px;
                border-radius: 17px;
                background: transparent;
                border: none;
            }
            QPushButton#nextButton:hover {
                background: rgba(255, 255, 255, 30);
                border-radius: 17px;
            }
        """)
        self.next_button.clicked.connect(self.play_next)

        self.repeat_button = QPushButton("↻")  # 重播圖示
        self.repeat_button.setObjectName("repeatButton")
        self.repeat_button.setCheckable(True)
        self.repeat_button.setFixedSize(35, 35)
        self.repeat_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                border-radius: 17px;
            }
        """)
        self.repeat_button.clicked.connect(self.toggle_repeat)

        self.shuffle_button = QPushButton("⇄")  # 隨機播放圖示
        self.shuffle_button.setObjectName("shuffleButton")
        self.shuffle_button.setCheckable(True)
        self.shuffle_button.setFixedSize(35, 35)
        self.shuffle_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                border-radius: 17px;
            }
        """)
        self.shuffle_button.clicked.connect(self.toggle_shuffle)

        self.add_folder_button = QPushButton("📁 Add Folder")
        self.add_folder_button.clicked.connect(self.add_folder)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.player.audio_set_volume(50)

        # 音量控制容器
        volume_container = QWidget()
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(10)
        
        volume_label = QLabel("🔊")
        volume_label.setStyleSheet("font-size: 16px;")
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)

        # 排版
        controls = QHBoxLayout()
        controls.addWidget(self.prev_button)
        controls.addWidget(self.play_button)
        controls.addWidget(self.next_button)
        controls.addWidget(self.repeat_button)
        controls.addWidget(self.shuffle_button)
        controls.addWidget(self.speed_combo)
        controls.addWidget(self.theme_button)  # 添加主題切換按鈕

        layout = QVBoxLayout()
        layout.addWidget(self.title_bar)
        layout.addWidget(info_container)  # 使用新的容器
        layout.addLayout(controls)
        layout.addWidget(volume_container)  # 移動音量控制到這裡
        layout.addWidget(self.add_folder_button)
        layout.addWidget(self.toggle_playlist_button)
        layout.addWidget(self.playlist_widget)

        self.setLayout(layout)

        # 自動更新進度條的 timer
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

    def update_ui(self):
        
        # 檢查歌曲是否播放完畢
        if not self.player.is_playing() and not self.is_sliding:
            state = self.player.get_state()
            if state == vlc.State.Ended:
                self.play_next()
            return

        try:
            # 更新進度條
            length = self.player.get_length()
            if length > 0:
                time = self.player.get_time()
            if time >= 0:
                current_position = int(time * 1000 / length)
                self.progress_slider.setValue(current_position)
                # 更新時間顯示
                current_time = self.format_time(time)
                total_time = self.format_time(length)
                self.time_label.setText(f"{current_time} / {total_time}")
        except Exception as e:
            print(f"Error updating UI: {e}")
    
    def format_time(self, ms):
        seconds = int(ms / 1000)
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def set_position(self, position):
        if not self.player.is_playing() or not self.is_sliding:
            return
        try:
            length = self.player.get_length()
            if length > 0:
                # 計算新的播放位置
                new_time = int(position * length / 1000)
                # 設置新的播放位置
                self.player.set_time(new_time)
        except Exception as e:
            print(f"Error setting position: {e}")

    def slider_pressed(self):
        self.is_sliding = True
        self.timer.stop()

    def slider_released(self):
        self.is_sliding = False
        self.timer.start()
        # 在釋放時重新設置位置
        try:
            position = self.progress_slider.value()
            length = self.player.get_length()
            if length > 0:
                new_time = int(position * length / 1000)
                self.player.set_time(new_time)
        except Exception as e:
            print(f"Error setting final position: {e}")

    def change_speed(self, speed_text):
        speed = float(speed_text.replace('x', ''))
        self.player.set_rate(speed)
        self.current_speed = speed

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.song_list = [os.path.join(folder, f) for f in os.listdir(folder)
                              if f.endswith(('.mp3', '.wav', '.flac'))]
            self.playlist_widget.clear()
            for song in self.song_list:
                self.playlist_widget.addItem(os.path.basename(song))
            if self.song_list:
                self.current_index = 0
                self.load_and_play(self.current_index)

    def load_and_play(self, index):
        if not self.song_list or not (0 <= index < len(self.song_list)):
            return
        try:
            self.player.set_media(vlc.Media(self.song_list[index]))
            song_name = os.path.basename(self.song_list[index])
            self.label.setText(song_name)
            # 更新視窗標題
            self.setWindowTitle(f"Desktop Music Player - {song_name}")
            self.player.play()
            self.play_button.setText("⏸")  # 顯示暫停圖示
            
            # 更新播放列表中的當前歌曲高亮
            for i in range(self.playlist_widget.count()):
                item = self.playlist_widget.item(i)
                if i == index:
                    item.setBackground(Qt.black)
                else:
                    item.setBackground(Qt.transparent)
            
            # 設置播放速度
            self.player.set_rate(self.current_speed)
        except Exception as e:
            print(f"Error loading song: {e}")
            self.label.setText("Error loading song")
            self.setWindowTitle("Desktop Music Player")  # 發生錯誤時恢復預設標題

    def toggle_play(self):
        if not self.song_list:  # 如果播放列表為空
            return
        if self.player.is_playing():
            self.player.pause()
            self.play_button.setText("▶️")  # 顯示播放圖示
        else:
            self.player.play()
            self.play_button.setText("⏸️")  # 顯示暫停圖示

    def play_selected_song(self, item):
        self.current_index = self.playlist_widget.row(item)
        self.load_and_play(self.current_index)

    def play_next(self):
        if not self.song_list:  # 如果播放列表為空
            return
        if self.player.is_playing():
            # 暫停當前歌曲，再播放下一首
            self.player.stop()
        
        if self.repeat:
            self.current_index = self.current_index
        elif self.shuffle:
            self.current_index = random.randint(0, len(self.song_list) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.song_list)
            
        self.load_and_play(self.current_index)

    def play_previous(self):
        if not self.song_list:  # 如果播放列表為空
            return
        if self.repeat:
            self.current_index = self.current_index
        elif self.shuffle:
            self.current_index = random.randint(0, len(self.song_list) - 1)
        else:
            self.current_index = (self.current_index - 1 + len(self.song_list)) % len(self.song_list)            
        self.load_and_play(self.current_index)
            
    def toggle_repeat(self):
        self.repeat = not self.repeat
        self.repeat_button.setChecked(self.repeat)

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self.shuffle_button.setChecked(self.shuffle)

    def set_volume(self, value):
        self.player.audio_set_volume(value)

    def toggle_playlist_visibility(self):
        if self.toggle_playlist_button.isChecked():
            self.toggle_playlist_button.setText("▲ Files")
            self.playlist_widget.show()
            self.add_folder_button.show()
            # 恢復最小高度
            self.setMinimumHeight(500)
            # 如果當前高度小於最小高度，則調整到最小高度
            if self.height() < 500:
                self.resize(self.width(), 500)
        else:
            self.toggle_playlist_button.setText("▼ Files")
            self.playlist_widget.hide()
            self.add_folder_button.hide()
            # 設置較小的最小高度，但保持足夠空間給其他元素
            self.setMinimumHeight(250)
            # 調整視窗高度到較小的高度，但保持足夠空間
            self.resize(self.width(), 250)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.title_bar.geometry().contains(event.pos()):
                self.dragging = True
                self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def on_song_end(self, event):
        try:
            self.play_next
        except Exception as e:
            print(f"Error during song change: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load the next song: {e}")

    def toggle_theme(self):
        # 切換主題
        if self.current_theme == "translucent":
            self.current_theme = "dark"
        elif self.current_theme == "dark":
            self.current_theme = "gentle_blue"
        else:
            self.current_theme = "translucent"
        
        self.apply_theme(self.current_theme)

    def apply_theme(self, theme_name):
        theme = self.themes[theme_name]
        
        # 更新視窗背景
        if theme_name == "translucent":
            self.setAttribute(Qt.WA_TranslucentBackground)
        else:
            self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # 設置樣式表
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QWidget#title_bar {{
                background-color: {theme['background']};
            }}
            QPushButton {{
                background: transparent;
                color: {theme['text']};
                border: none;
                font-size: 16px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background: {theme['button_hover']};
                border-radius: 3px;
            }}
            QPushButton#repeatButton:checked,
            QPushButton#shuffleButton:checked {{
                color: #4CAF50;
                background: {theme['selected_bg']};
                border-radius: 3px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {theme['text']};
                height: 8px;
                background: {theme['slider_bg']};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {theme['text']};
                border: 1px solid {theme['background']};
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }}
            QComboBox {{
                background: {theme['combo_bg']};
                border: none;
                border-radius: 3px;
                padding: 2px 5px;
                color: {theme['text']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QListWidget::item:selected {{
                background: {theme['selected_bg']};
                color: {theme['text']};
            }}
            QListWidget::item {{
                padding: 5px;
            }}
            QLabel#songLabel {{
                color: {theme['text']};
                font-size: 18px;
                qproperty-alignment: AlignCenter;
            }}
            QLabel#timeLabel {{
                color: {theme['text']};
                font-size: 16px;
                qproperty-alignment: AlignCenter;
            }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())