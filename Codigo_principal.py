import cv2
import numpy as np
import face_recognition
import os
import urllib.request
import mediapipe as mp
import serial
from datetime import datetime

# === CONFIGURACIONES ===
ESP32CAM_URL = "http://192.168.243.3/cam-hi.jpg"
IMAGE_FOLDER = "image_folder"
SERIAL_PORT = "COM3"
BAUD_RATE = 9600

# === SERIAL ===
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print(f"[INFO] Conectado al puerto serial {SERIAL_PORT}")
except Exception as e:
    print(f"[ERROR] No se pudo conectar al puerto serial: {e}")
    ser = None

# === CARGAR ROSTROS ===
print("[INFO] Cargando rostros conocidos...")
known_encodings = []
known_names = []

for filename in os.listdir(IMAGE_FOLDER):
    path = os.path.join(IMAGE_FOLDER, filename)
    img = cv2.imread(path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(img_rgb)

    if encodings:
        known_encodings.append(encodings[0])
        known_names.append(os.path.splitext(filename)[0])
    else:
        print(f"[ADVERTENCIA] No se detectó rostro en {filename}")

# === FUNCIÓN PARA DETECTAR GESTO ===
def detectar_gesto():
    cap = cv2.VideoCapture(0)  # O usar ESP32-CAM si es preferible
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils

    def contar_dedos(landmarks):
        dedos = [8, 12, 16, 20]
        count = 0
        for d in dedos:
            if landmarks[d].y < landmarks[d - 2].y:
                count += 1
        if landmarks[4].x < landmarks[3].x:
            count += 1
        return count

    print("[INFO] Iniciando reconocimiento de señas...")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
                lm = handLms.landmark
                dedos = contar_dedos(lm)

                if dedos == 0:
                    comando = "ENCENDER"
                elif dedos == 5:
                    comando = "APAGAR"
                elif dedos == 1:
                    comando = "INVERTIR"
                else:
                    comando = None

                if comando and ser:
                    ser.write((comando + "\n").encode())
                    print(f"[ENVÍO] {comando}")

        cv2.imshow("Señas", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# === CAPTURAR IMAGEN DE ESP32-CAM ===
print("[INFO] Capturando imagen desde ESP32-CAM...")
try:
    resp = urllib.request.urlopen(ESP32CAM_URL)
    image_np = np.asarray(bytearray(resp.read()), dtype=np.uint8)
    frame = cv2.imdecode(image_np, -1)
except Exception as e:
    print(f"[ERROR] No se pudo capturar imagen de la ESP32-CAM: {e}")
    exit()

# === VERIFICACIÓN FACIAL ===
print("[INFO] Procesando reconocimiento facial...")
img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
faces = face_recognition.face_locations(img_rgb)
encodings = face_recognition.face_encodings(img_rgb, faces)

recognized = False
for encoding in encodings:
    matches = face_recognition.compare_faces(known_encodings, encoding)
    face_distances = face_recognition.face_distance(known_encodings, encoding)
    best_match_index = np.argmin(face_distances)

    if matches[best_match_index]:
        name = known_names[best_match_index]
        print(f"[ACCESO PERMITIDO] Usuario reconocido: {name}")
        recognized = True
        detectar_gesto()
        break

if not recognized:
    print("[ACCESO DENEGADO] Usuario no reconocido.")

