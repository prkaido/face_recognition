#include <WebServer.h>  // Incluir la librería para el servidor web
#include <WiFi.h>      // Incluir la librería para la conexión WiFi
#include <esp32cam.h>  // Incluir la librería para manejar la cámara ESP32

// Definir el SSID y la contraseña de la red WiFi
const char* WIFI_SSID = "proyecto";
const char* WIFI_PASS = "sergio123";

// Crear un servidor web en el puerto 80
WebServer server(80);

// Definir las resoluciones de la cámara
static auto loRes = esp32cam::Resolution::find(320, 240);   // Resolución baja
static auto midRes = esp32cam::Resolution::find(640, 480);   // Resolución media
static auto hiRes = esp32cam::Resolution::find(800, 600);    // Resolución alta

// Función para servir una imagen JPEG
void serveJpg() {
  auto frame = esp32cam::capture();  // Capturar un fotograma de la cámara
  if (frame == nullptr) {  // Si la captura falla
    Serial.println("CAPTURE FAIL");  // Imprimir error
    server.send(503, "", "");  // Enviar respuesta 503 (Servicio no disponible)
    return;  // Salir de la función
  }
  
  // Imprimir información sobre el fotograma capturado
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(), 
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());  // Establecer la longitud del contenido
  server.send(200, "image/jpeg");  // Enviar respuesta 200 (OK) con tipo de contenido JPEG
  WiFiClient client = server.client();  // Obtener el cliente de WiFi
  frame->writeTo(client);  // Escribir el fotograma en el cliente
}

// Manejar la solicitud de imagen de resolución baja
void handleJpgLo() {
  if (!esp32cam::Camera.changeResolution(loRes)) {  // Cambiar a resolución baja
    Serial.println("SET-LO-RES FAIL");  // Imprimir error
  }
  serveJpg();  // Servir la imagen
}

// Manejar la solicitud de imagen de resolución alta
void handleJpgHi() {
  if (!esp32cam::Camera.changeResolution(hiRes)) {  // Cambiar a resolución alta
    Serial.println("SET-HI-RES FAIL");  // Imprimir error
  }
  serveJpg();  // Servir la imagen
}

// Manejar la solicitud de imagen de resolución media
void handleJpgMid() {
  if (!esp32cam::Camera.changeResolution(midRes)) {  // Cambiar a resolución media
    Serial.println("SET-MID-RES FAIL");  // Imprimir error
  }
  serveJpg();  // Servir la imagen
}

// Configuración inicial
void setup() {
  Serial.begin(115200);  // Iniciar la comunicación serial a 115200 baudios
  Serial.println();

  {
    using namespace esp32cam;  // Usar el espacio de nombres esp32cam
    Config cfg;  // Crear un objeto de configuración
    cfg.setPins(pins::AiThinker);  // Configurar los pines para la cámara AiThinker
    cfg.setResolution(hiRes);  // Establecer la resolución inicial en alta
    cfg.setBufferCount(2);  // Establecer el número de búferes
    cfg.setJpeg(80);  // Establecer la calidad JPEG

    bool ok = Camera.begin(cfg);  // Iniciar la cámara con la configuración
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");  // Imprimir el estado de la cámara
  }

  // Configurar WiFi
  WiFi.persistent(false);  // Deshabilitar la persistencia del WiFi
  WiFi.mode(WIFI_STA);  // Establecer el modo de WiFi en estación
  WiFi.begin(WIFI_SSID, WIFI_PASS);  // Conectar a la red WiFi
  while (WiFi.status() != WL_CONNECTED) {  // Esperar hasta que se conecte
    delay(500);  // Esperar medio segundo
  }
  
  // Imprimir la dirección IP local del ESP32
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam-lo.jpg");  // URL para resolución baja
  Serial.println("  /cam-hi.jpg");  // URL para resolución alta
  Serial.println("  /cam-mid.jpg");  // URL para resolución media

  // Definir las rutas del servidor web
  server.on("/cam-lo.jpg", handleJpgLo);  // Ruta para la imagen de resolución baja
  server.on("/cam-hi.jpg", handleJpgHi);  // Ruta para la imagen de resolución alta
  server.on("/cam-mid.jpg", handleJpgMid);  // Ruta para la imagen de resolución media

  server.begin();  // Iniciar el servidor
}

// Bucle principal
void loop() {
  server.handleClient();  // Manejar las solicitudes del cliente
}
