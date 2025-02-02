from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread
from valclient.client import Client
from internal import ValorantInternal
import pyautogui
import pygetwindow as gw
import time
import sys
import os
import subprocess
import psutil

client = Client(region="ap")
valorant_internal = ValorantInternal()

try:
    client.activate()
except Exception as e:
    print(f"Failed to activate client: {e}")


class AutoVCThread(QThread):
    def __init__(self):
        super().__init__()
        self.running = False
        self.v_key_pressed = False

    def run(self):
        while self.running:
            valorant_windows = gw.getWindowsWithTitle("VALORANT")
            if valorant_windows and valorant_windows[0].isActive:
                if not self.v_key_pressed:
                    pyautogui.keyDown('v')
                    self.v_key_pressed = True
            else:
                if self.v_key_pressed:
                    pyautogui.keyUp('v')
                    self.v_key_pressed = False
            time.sleep(0.1)

    def stop(self):
        if self.v_key_pressed:
            pyautogui.keyUp('v')
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VALORANT Helper")
        self.setGeometry(200, 200, 400, 450)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)


        self.check_button = QPushButton("Check Side")
        self.check_button.setFont(QFont("Arial", 12))
        self.check_button.clicked.connect(self.check_side)
        self.layout.addWidget(self.check_button)

        self.dodge_button = QPushButton("Dodge Game")
        self.dodge_button.setFont(QFont("Arial", 12))
        self.dodge_button.setStyleSheet("background-color: #EBCB8B; color: #2E3440;") # Nord Theme の黄色
        self.dodge_button.clicked.connect(self.dodge_game)
        self.layout.addWidget(self.dodge_button)

        self.remove_friends_button = QPushButton("Remove All Friends")
        self.remove_friends_button.setFont(QFont("Arial", 12))
        self.remove_friends_button.setStyleSheet("background-color: #8FBCBB; color: #2E3440;") # Nord Theme のシアン
        self.remove_friends_button.clicked.connect(self.remove_all_friends)
        self.layout.addWidget(self.remove_friends_button)

        self.autovc_button = QPushButton("AutoVC: OFF")
        self.autovc_button.setFont(QFont("Arial", 12))
        self.autovc_button.setStyleSheet("background-color: green; color: white;")
        self.autovc_button.clicked.connect(self.toggle_autovc)
        self.layout.addWidget(self.autovc_button)

        self.kill_valorant_button = QPushButton("Kill Valorant")
        self.kill_valorant_button.setFont(QFont("Arial", 12))
        self.kill_valorant_button.setStyleSheet("background-color: #D08770; color: white;")
        self.kill_valorant_button.clicked.connect(self.kill_bootstrap)
        self.layout.addWidget(self.kill_valorant_button)


        self.result_label = QLabel("Result will appear here")
        self.result_label.setFont(QFont("Arial", 14))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.layout.addWidget(self.result_label)
        self.result_label.setStyleSheet("color: #A3BE8C;")


        self.set_custom_style()
        self.autovc_thread = AutoVCThread()


    def set_result_text(self, text, is_error=False):
        self.result_label.setText(text)
        if is_error:
            self.result_label.setStyleSheet("color: #BF616A;")
        else:
            self.result_label.setStyleSheet("color: #A3BE8C;")


    def check_side(self):
        try:
            ally = client.pregame_fetch_match()['AllyTeam']
            ally_result = "Null"
            ally_team = ally['TeamID']
            if ally_team == 'Red':
                ally_result = 'Attacker'
            elif ally_team == 'Blue':
                ally_result = 'Defender'
            else:
                ally_result = 'Unknown'

            self.set_result_text(f"Your side: {ally_result}")
        except Exception as e:
            self.set_result_text(f"Error: {e}", is_error=True)


    def dodge_game(self):
        try:
            client.pregame_quit_match()
            self.set_result_text("Successfully dodged the game!")
        except Exception as e:
            self.set_result_text(f"Error: {e}", is_error=True)


    def remove_all_friends(self):
        try:
            friends = valorant_internal.get_friends().friends
            if not friends:
                self.set_result_text("No friends to remove.")
                return

            for friend in friends:
                status_code = valorant_internal.remove_friend(friend)
                if status_code == 200:
                    print(f"Removed friend: {friend.gamename}")
                else:
                    print(f"Failed to remove friend: {friend.gamename}, Status Code: {status_code}")

            self.set_result_text("All friends removed successfully.")
        except Exception as e:
            self.set_result_text(f"Error: {e}", is_error=True)


    def toggle_autovc(self):
        if self.autovc_thread.running:
            self.autovc_thread.stop()
            self.autovc_button.setText("AutoVC: OFF")
            self.autovc_button.setStyleSheet("background-color: green; color: white;")
        else:
            self.autovc_thread.running = True
            self.autovc_thread.start()
            self.autovc_button.setText("AutoVC: ON")
            self.autovc_button.setStyleSheet("background-color: red; color: white;")


    def kill_bootstrap(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "VALORANT.exe":
                    proc.kill()
                    self.set_result_text("VALORANT process killed successfully.")
                    return
            self.set_result_text("VALORANT process not found.", is_error=True)
        except Exception as e:
            self.set_result_text(f"Error: {e}", is_error=True)


    def set_custom_style(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#2E3440"))
        palette.setColor(QPalette.WindowText, QColor("#D8DEE9"))
        self.setPalette(palette)

        self.central_widget.setStyleSheet("background-color: #2E3440; color: #D8DEE9;")
        self.check_button.setStyleSheet(f"background-color: #4C566A; color: #D8DEE9; border: 1px solid #4C566A; border-radius: 5px; padding: 8px;")
        self.dodge_button.setStyleSheet(f"background-color: #EBCB8B; color: #2E3440; border: 1px solid #EBCB8B; border-radius: 5px; padding: 8px;")
        self.remove_friends_button.setStyleSheet(f"background-color: #8FBCBB; color: #2E3440; border: 1px solid #8FBCBB; border-radius: 5px; padding: 8px;")
        self.autovc_button.setStyleSheet(f"QPushButton{{background-color: green; color: white; border: 1px solid green; border-radius: 5px; padding: 8px;}} QPushButton:hover{{background-color: #A3BE8C; border: 1px solid #A3BE8C;}} QPushButton:checked{{background-color: red;}}") # ホバー時の色変更と AutoVC ON 時の色を CSS で定義
        self.kill_valorant_button.setStyleSheet(f"background-color: #D08770; color: white; border: 1px solid #D08770; border-radius: 5px; padding: 8px;")
        self.result_label.setStyleSheet(f"color: #A3BE8C;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())