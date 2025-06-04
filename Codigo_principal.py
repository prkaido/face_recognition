import cv2
import numpy as np
import face_recognition
import os
import urllib.request
import mediapipe as mp
import serial

# === CONFIGURACIONES ===
ESP32CAM_URL = "http://192.168.243.3/cam-hi.jpg"
IMAGE_FOLDER = "image_folder"
SERIAL_PORT = "COM3"
BAUD_RATE = 9600

# === SERIAL ===
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
except Exception as e:
    print(f"[ERROR] Serial: {e}")
    ser = None

# === CARGAR ROSTROS ===
known_encodings = []
known_names = []

for filename in os.listdir(IMAGE_FOLDER):
    path = os.path.join(IMAGE_FOLDER, filename)
    img = cv2.imread(path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    enc = face_recognition.face_encodings(img_rgb)
    if enc:
        known_encodings.append(enc[0])
        known_names.append(os.path.splitext(filename)[0])

# === FUNCIÓN DE GESTOS ===
def detectar_gesto():
    cap = cv2.VideoCapture(0)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils

    def contar_dedos(landmarks):
        dedos = 0
        if landmarks[4].x < landmarks[3].x: dedos += 1  # Pulgar
        for tip in [8, 12, 16, 20]:
            if landmarks[tip].y < landmarks[tip - 2].y:
                dedos += 1
        return dedos

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                lm = handLms.landmark
                dedos = contar_dedos(lm)

                # Dibujar contorno azul
                h, w, _ = frame.shape
                coords = [(int(l.x * w), int(l.y * h)) for l in handLms.landmark]
                x_vals, y_vals = zip(*coords)
                xmin, xmax = min(x_vals), max(x_vals)
                ymin, ymax = min(y_vals), max(y_vals)
                cv2.rectangle(frame, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (255, 0, 0), 2)

                # Mostrar número de dedos
                cv2.putText(frame, f"Dedos detectados: {dedos}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                # Enviar comando por serial
                if ser:
                    if dedos == 0:
                        ser.write(b"ENCENDER\n")
                    elif dedos == 1:
                        ser.write(b"INVERTIR\n")
                    elif dedos == 5:
                        ser.write(b"APAGAR\n")

                mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

        cv2.imshow("Gestos de mano", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# === CAPTURA ESP32-CAM ===
try:
    resp = urllib.request.urlopen(ESP32CAM_URL)
    img_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
    frame = cv2.imdecode(img_array, -1)
except Exception as e:
    print(f"[ERROR] Imagen ESP32-CAM: {e}")
    exit()

# === RECONOCIMIENTO FACIAL ===
img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
faces = face_recognition.face_locations(img_rgb)
encodings = face_recognition.face_encodings(img_rgb, faces)

recognized = False

for (top, right, bottom, left), encoding in zip(faces, encodings):
    matches = face_recognition.compare_faces(known_encodings, encoding)
    distances = face_recognition.face_distance(known_encodings, encoding)
    best_match = np.argmin(distances)

    if matches[best_match]:
        name = known_names[best_match]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        recognized = True
        detectar_gesto()
    else:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, "Desconocido", (left, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

if not recognized:
    print("[ACCESO DENEGADO] Usuario no reconocido.")

cv2.imshow("Reconocimiento Facial", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
