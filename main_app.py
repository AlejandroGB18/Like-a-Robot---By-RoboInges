import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QApplication, QDesktopWidget
from intro import Ui_MainWindow
from juego import Ui_Form
from resultados import Ui_ResultWindow  # Ensure this import matches the filename and class

import pygame

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.question_counter = 0
        self.max_questions = 5  # Set the number of questions
        self.good_ans_count = 0
        self.bad_ans_count = 0
        self.partial_ans_count = 0
        self.not_ans_count = 0

        # Get screen resolution
        screen_resolution = QApplication.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setGeometry(0, 0, width, height)

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialize Pygame mixer with specific settings
        pygame.mixer.pre_init(44100, -16, 2, 512)  # Sample rate, size, channels, buffer
        pygame.init()

        # Initialize the first window
        self.main_window = QtWidgets.QMainWindow()
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self.main_window)
        self.stack.addWidget(self.main_window)

        # Initialize the second window
        self.second_window = QtWidgets.QWidget()
        self.second_ui = Ui_Form()
        self.second_ui.setupUi(self.second_window)
        self.stack.addWidget(self.second_window)

        # Initialize the third window for results
        self.result_window = QtWidgets.QWidget()
        self.result_ui = Ui_ResultWindow()
        self.result_ui.setupUi(self.result_window)
        self.stack.addWidget(self.result_window)

        # Connect button to change window
        self.main_ui.pushButton.clicked.connect(self.show_second_window)

        # Connect signal from app_p1 to a method in MainApp
        self.second_ui.thread.respuesta_correcta.connect(self.handle_r_correct)
        self.second_ui.thread.respuesta_parcial.connect(self.handle_r_partial)
        self.second_ui.thread.respuesta_incorrecta.connect(self.handle_r_incorrect)
        self.second_ui.thread.sin_respuesta.connect(self.handle_r_not)

        # Play the initial music
        self.main_music = pygame.mixer.Sound('main_theme.wav')
        self.game_music = pygame.mixer.Sound('app_music.wav')
        self.result_music = pygame.mixer.Sound('result_music.wav')
        self.play_main_music()

    def play_main_music(self):
        pygame.mixer.stop()
        self.main_music.play(loops=-1)

    def play_game_music(self):
        pygame.mixer.stop()
        self.game_music.play(loops=-1)

    def play_result_music(self):
        pygame.mixer.stop()
        self.result_music.play(loops=-1)

    def show_second_window(self):
        self.stack.setCurrentWidget(self.second_window)
        self.play_game_music()
        self.reset_counters()  # Reset counters at the start of the game

    def reset_counters(self):
        self.question_counter = 0
        self.good_ans_count = 0
        self.bad_ans_count = 0
        self.partial_ans_count = 0
        self.not_ans_count = 0

    def handle_r_correct(self):
        self.good_ans_count += 1
        self.check_questions()

    def handle_r_partial(self):
        self.partial_ans_count += 1
        self.check_questions()

    def handle_r_incorrect(self):
        self.bad_ans_count += 1
        self.check_questions()

    def handle_r_not(self):
        self.not_ans_count += 1
        self.check_questions()

    def check_questions(self):
        self.question_counter += 1
        if self.question_counter >= self.max_questions:
            self.show_result_window()

    def show_result_window(self):
        self.result_ui.update_results(self.good_ans_count, self.partial_ans_count, self.bad_ans_count, self.not_ans_count)
        self.stack.setCurrentWidget(self.result_window)
        self.play_result_music()  #

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
    pygame.quit()
