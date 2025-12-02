import os
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl


class Music():
    def __init__(self):
        self.audio_output = QAudioOutput()
        self.music_player = QMediaPlayer()
        self.music_player.setAudioOutput(self.audio_output)

        music_file = "sounds/background_music.mp3"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        music_file = os.path.join(current_dir, "..", "sounds", "background_music.mp3")
        self.music_player.setSource(QUrl.fromLocalFile(music_file))
        self.music_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.audio_output.setVolume(0.8)
        self.music_player.play()

    def play(self):
        self.music_player.play()

    def pause(self):
        self.music_player.pause()

    def set_volume(self, vol):
        self.audio_output.setVolume(vol / 100)