import sys
import cv2
import random
from pyzbar.pyzbar import decode
import pyrebase
import time
import os
import pygame
from pygame.locals import *
from PyQt5 import QtCore, QtGui, QtWidgets

# Firebase configuration
config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_AUTH_DOMAIN",
    "databaseURL": "YOUR_DATABASE_URL",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_STORAGE_BUCKET",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId": "YOUR_APP_ID"
}

# Load audio files
pygame.mixer.init()
good_ans = pygame.mixer.Sound('good_answer.wav')
regular_ans = pygame.mixer.Sound('regular_answer.wav')
wrong_ans = pygame.mixer.Sound('wrong_ans.wav')
time_over = pygame.mixer.Sound('bad_answer.wav')

# Global counters
good_ans_counter = 0
partial_ans_counter = 0
bad_ans_counter = 0
not_ans_counter = 0
question_counter = 0
max_questions = 5

# Function to calculate the error percentage
def calcular_porcentaje_error(valor_esperado, valor_obtenido):
    global good_ans_counter, partial_ans_counter, bad_ans_counter

    error_absoluto = abs(valor_esperado - valor_obtenido)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    porcentaje_error = (error_absoluto / valor_esperado) * 100

    if porcentaje_error == 0:
        db.child("eduprotect").update({"mover": "f"})
        time.sleep(5)
        good_ans.play()
        db.child("eduprotect").update({"mover": "s"})
        return 'Valor real'
    elif porcentaje_error < 5:
        db.child("eduprotect").update({"mover": "f"})
        regular_ans.play()
        time.sleep(3)
        db.child("eduprotect").update({"mover": "s"})
        return 'Valor cercano al real'
    elif porcentaje_error < 50:
        db.child("eduprotect").update({"mover": "f"})
        regular_ans.play()
        time.sleep(1)
        db.child("eduprotect").update({"mover": "s"})
        return 'Valor algo alejado al real'
    else:
        wrong_ans.play()
        return 'Valor lejano al real'

# Function to obtain a random question
def obtener_pregunta():
    preguntas_list = [
        ('¿Cuál es el resultado de la operación 12 x 6?', 72),
        ('¿Cuál es el resultado de la operación 25 - 13?', 12),
        ('Dividir a 50 entre 2 nos da como resultado...', 25),
        ('¿Cuál es el resultado de sumarle 39 a 41?', 80),
        ('¿Cuánto es 15 + 27?', 42),
        ('Si cada caja contiene 24 chocolates, ¿cuántos chocolates hay en 5 cajas?', 120),
        ('Si un libro tiene 100 páginas y ya leíste 85 páginas, ¿cuántas páginas te faltan por leer?', 15),
        ('Si un pastel tiene 16 rebanadas y quieres dividirlo entre 4 personas, ¿cuántas rebanadas le tocan a cada persona?', 4),
        ('Si tienes 23 manzanas y compras 12 más, ¿cuántas manzanas tienes en total?', 35),
        ('Si tienes 34 pesos y gastas 28 pesos, ¿cuánto dinero te queda?', 6),
        ('Cuentas con 90 minutos en un examen que tienes 45 preguntas, ¿cuántos minutos tendrás para responder cada pregunta?', 2),
        ('En una granja, hay 35 patos en un estanque y 14 patos en otro. ¿Cuántos patos hay en total?', 49),
        ('Un agricultor tenía 85 manzanas en su huerto. Después de la cosecha, vendió 42 manzanas. ¿Cuántas manzanas le quedan?', 43),
        ('Un estudiante necesita comprar 5 cuadernos para la escuela. Cada cuaderno cuesta $15. ¿Cuánto gastará en total?', 75),
        ('Si tienes 60 caramelos y quieres repartirlos en partes iguales entre 3 amigos, ¿cuántos caramelos recibirá cada amigo?', 20),
        ('Tenemos 4 arboles de naranjas, cada árbol produce 12 naranjas, ¿Cuántas naranjas tenemos en total?', 48)
    ]
    return random.choice(preguntas_list)

class QRReaderThread(QtCore.QThread):
    respuesta_correcta = QtCore.pyqtSignal()
    respuesta_incorrecta = QtCore.pyqtSignal()
    respuesta_parcial = QtCore.pyqtSignal()
    sin_respuesta = QtCore.pyqtSignal()
    update_frame = QtCore.pyqtSignal(QtGui.QImage)
    update_question = QtCore.pyqtSignal(str)
    update_label = QtCore.pyqtSignal(str)
    update_gif = QtCore.pyqtSignal(str)
    update_timer = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.p = 0
        self.flag = max_questions
        self.time_limit = 30
        self.ultimo_valor = ""

    def run(self):
        global good_ans_counter, partial_ans_counter, bad_ans_counter, not_ans_counter
        pregunta_actual = obtener_pregunta()
        pregunta, valor_esperado = pregunta_actual
        question_start_time = time.time()

        self.update_question.emit(f"{pregunta}")
        self.update_label.emit(f"Pregunta {self.p + 1} de {self.flag}")

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("No se pudo acceder a la cámara.")
                break

            codigos_qr = decode(frame)

            if self.p < self.flag:
                for codigo in codigos_qr:
                    datos_qr = codigo.data.decode('utf-8')

                    try:
                        valor_obtenido = int(datos_qr)

                        # Check if the obtained value is the same as the last one and not the expected value
                        if valor_obtenido == self.ultimo_valor and valor_obtenido != valor_esperado:
                            continue

                        resultado = calcular_porcentaje_error(valor_esperado, valor_obtenido)
                        print(f"Porcentaje de error: {resultado}")

                        (x, y, w, h) = codigo.rect
                        cv2.rectangle(frame, (x, y), (x +  w, y + h),(0, 255, 0), 2)
                        cv2.putText(frame, f"{resultado}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                        self.ultimo_valor = valor_obtenido

                        if resultado == 'Valor real':
                            self.update_gif.emit('correcto.gif')
                            self.respuesta_correcta.emit()
                        elif resultado in ['Valor cercano al real', 'Valor algo alejado al real']:
                            self.update_gif.emit('parcial.gif')
                            self.respuesta_parcial.emit()
                        else:
                            self.update_gif.emit('incorrecto.gif')
                            self.respuesta_incorrecta.emit()

                        self.p += 1
                        print(f"PREGUNTA: {self.p}/{self.flag}")

                        # Get a new question and update the expected value
                        if self.p < self.flag:
                            pregunta_actual = obtener_pregunta()
                            if pregunta_actual:
                                pregunta, valor_esperado = pregunta_actual
                                question_start_time = time.time()
                                self.update_question.emit(f"{pregunta}")
                                self.update_label.emit(f"Pregunta {self.p + 1} de {self.flag}")

                    except ValueError:
                        print("Error: El valor del QR no es un número entero.")

            # Check if the time for the current question has elapsed
            elapsed_time = time.time() - question_start_time
            remaining_time = self.time_limit - int(elapsed_time)
            self.update_timer.emit(f"Tiempo restante: {remaining_time}s")

            if remaining_time <= 0:
                time_over.play()
                # Move to the next question
                not_ans_counter += 1  # Increment unanswered counter
                self.p += 1
                self.update_gif.emit('time_up.gif')
                self.sin_respuesta.emit()
                if self.p < self.flag:
                    pregunta_actual = obtener_pregunta()
                    if pregunta_actual:
                        pregunta, valor_esperado = pregunta_actual
                        question_start_time = time.time()
                        self.update_question.emit(f"{pregunta}")
                        self.update_label.emit(f"Pregunta {self.p + 1} de {self.flag}")
                else:
                    print("========= FIN DEL JUEGO =========")
                    print("Tu puntaje: ")
                    print(f"Preguntas correctas: {good_ans_counter}")
                    print(f"Preguntas incorrectas: {bad_ans_counter}")
                    print(f"Preguntas parciales: {partial_ans_counter}")
                    print(f"Preguntas sin contestar: {not_ans_counter}")
                    break

            # Convert the image to a format suitable for PyQt
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(320, 320, QtCore.Qt.KeepAspectRatio)
            self.update_frame.emit(p)

    def stop(self):
        self.running = False
        self.cap.release()
        self.quit()

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1920, 1000)
        self.thread = QRReaderThread()
        self.thread.respuesta_correcta.connect(self.handle_r_correct)
        self.thread.respuesta_parcial.connect(self.handle_r_partial)
        self.thread.respuesta_incorrecta.connect(self.handle_r_incorrect)
        self.thread.sin_respuesta.connect(self.handle_r_not)

        # Fondo de la app
        self.back_app = QtWidgets.QLabel(Form)
        self.back_app.setGeometry(QtCore.QRect(0, 0, 1920, 1000))
        self.movie = QtGui.QMovie('RoboInges_game.gif')
        self.back_app.setMovie(self.movie)
        self.movie.start()

        self.cam_view = QtWidgets.QLabel(Form)
        self.cam_view.setGeometry(QtCore.QRect(400, 200, 1280, 720))
        self.cam_view.setObjectName("cam_view")
        self.thread.update_frame.connect(self.set_image)

        self.question = QtWidgets.QLabel(Form)
        self.question.setGeometry(QtCore.QRect(100, 155, 1730, 101))
        self.question.setAutoFillBackground(True)
        self.question.setStyleSheet("color:rgb(0,0,0);\n"
"font-size: 35px;\n"
"font-family: Beton;\n"
"font-weight: bold;\n"
"text-align: center;")
        self.question.setWordWrap(True)
        self.question.setAlignment(QtCore.Qt.AlignCenter)
        self.question.setObjectName("question")

        self.gif_reactive = QtWidgets.QLabel(Form)
        self.gif_reactive.setGeometry(QtCore.QRect(1050, 320, 500, 500))
        #self.movie = QtGui.QMovie('C:/Users/Alejandro/Documents/vision_robot/robo_app/stand_by.gif')
        #self.gif_reactive.setMovie(self.movie)
        self.movie.start()
        self.gif_reactive.setPixmap(QtGui.QPixmap('C:/Users/Alejandro/Documents/vision_robot/robo_app/stand_by.png'))
        self.gif_reactive.setObjectName("gif_reactive")

        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(610, 50, 700, 100))
        self.label.setStyleSheet("color:rgb(0,0,0);\n"
"font-size: 80px;\n"
"font-family: Beton;\n"
"font-weight: bold;\n"
"text-align: center;")
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.timer_label = QtWidgets.QLabel(Form)  # Label to display the timer
        self.timer_label.setGeometry(QtCore.QRect(740, 250, 470, 80))
        self.timer_label.setStyleSheet("color:rgb(255,0,0);\n"
"font-size: 40px;\n"
"font-family: Beton;\n"
"font-weight: bold;\n"
"text-align: center;")
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_label.setObjectName("timer_label")

        self.thread.update_question.connect(self.update_question_label)
        self.thread.update_label.connect(self.update_question_count_label)
        self.thread.update_gif.connect(self.update_gif_label)
        self.thread.update_timer.connect(self.update_timer_label)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.thread.start()


    def handle_r_correct(self):
        global good_ans_counter
        good_ans_counter += 1

    def handle_r_incorrect(self):
        global bad_ans_counter
        bad_ans_counter += 1

    def handle_r_partial(self):
        global partial_ans_counter
        partial_ans_counter += 1

    def handle_r_not(self):
        global not_ans_counter
        not_ans_counter += 1

    def set_image(self, image):
        self.cam_view.setPixmap(QtGui.QPixmap.fromImage(image))

    def update_question_label(self, question_text):
        self.question.setText(question_text)

    def update_question_count_label(self, count_text):
        self.label.setText(count_text)

    def update_gif_label(self, gif_path):
        if gif_path:
            self.gif_reactive.setMovie(QtGui.QMovie(gif_path))
            self.gif_reactive.movie().start()
        else:
            self.gif_reactive.clear()

    def update_timer_label(self, timer_text):
        self.timer_label.setText(timer_text)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
