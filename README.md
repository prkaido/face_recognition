# face_recognition
# 🎯 Reconocimiento Facial con Python + Arduino/PLC

Este proyecto implementa un sistema de **reconocimiento facial en tiempo real** utilizando Python, OpenCV y la librería `face_recognition`, con la capacidad de enviar comandos por puerto serial a un microcontrolador (como Arduino o ESP32), que puede actuar directamente o servir de intermediario para controlar un **PLC Siemens S7-1200** mediante protocolo Modbus TCP.

## ⚙️ Tecnologías Utilizadas

- Python 3.x
- OpenCV
- face_recognition
- PySerial
- Arduino UNO / ESP32
- PLC Siemens (opcional)

## 🔄 Flujo de Trabajo

1. La cámara detecta un rostro en tiempo real.
2. Se compara con imágenes previamente registradas en la carpeta `image_folder/`.
3. Si el rostro coincide:
   - Se envía el comando `"encender"` por el puerto serial.
4. Si no coincide:
   - Se puede enviar `"apagar"` o ignorar la acción.
5. Arduino recibe el comando y ejecuta una acción (encender LED, activar relé, etc.).
6. Opcionalmente, Arduino puede comunicar el estado a un PLC vía Modbus TCP/IP.

## 📂 Estructura del Proyecto
   ```bash
      face_recognition/
      ├── Codigo_principal.py # Script principal de detección facial
      ├── requirements.txt # Librerías necesarias
      ├── image_folder/ # Imágenes de rostros autorizados
      ├── Others/
                |───Arduino_Ethernet.ino # Código para el microcontrolador
                |───reconocimiento_facial.ino # Código para el ESP32
      └── README.md
```
## 🧰 Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/prkaido/face_recognition.git
   cd face_recognition
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
5. Ejecutar programa:
   ```bash
   python Codigo_principal.py
Desarrollado por @prkaido
