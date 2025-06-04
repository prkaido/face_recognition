#include <EtherCard.h>   
#include <Modbus.h>
#include <ModbusIP_ENC28J60.h>

const int SENSOR_IREG1 = 60;  // Registro para estado
const int SENSOR_IREG2 = 70;  // Registro para comando recibido

ModbusIP mb;

String comando = "";  // Variable para guardar el comando recibido

void setup() {
  Serial.begin(9600);

  // Dirección MAC e IP del módulo ENC28J60
  byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED}; 
  byte ip[]  = {192, 168, 1, 22};

  mb.config(mac, ip);
  mb.addIreg(SENSOR_IREG1);  // Estado
  mb.addIreg(SENSOR_IREG2);  // Último comando recibido (como número)
}

void loop() {
  mb.task();

  // Verifica si hay datos disponibles en el puerto serial
  if (Serial.available()) {
    char c = Serial.read();
    
    // Fin de línea indica fin del comando
    if (c == '\n' || c == '\r') {
      comando.trim();  // Elimina espacios en blanco
      
      if (comando.equalsIgnoreCase("encender")) {
        mb.Ireg(SENSOR_IREG1, 1);
        mb.Ireg(SENSOR_IREG2, 1);
        Serial.println("Comando recibido: ENCENDER");
      }
      else if (comando.equalsIgnoreCase("apagar")) {
        mb.Ireg(SENSOR_IREG1, 0);
        mb.Ireg(SENSOR_IREG2, 2);
        Serial.println("Comando recibido: APAGAR");
      }
      else if (comando.equalsIgnoreCase("inversion")) {
        mb.Ireg(SENSOR_IREG1, 2);  // Usamos 2 para simbolizar "inversión"
        mb.Ireg(SENSOR_IREG2, 3);
        Serial.println("Comando recibido: INVERSION");
      }
      else {
        Serial.println("Comando no reconocido");
      }

      comando = "";  // Limpiar el comando para el próximo
    } 
    else {
      comando += c;  // Construir el comando carácter por carácter
    }
  }
}
