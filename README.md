# 🖐️ Teclado Virtual Accesible por Seguimiento de Mano

Este proyecto es un prototipo de **teclado virtual accesible** pensado para personas con discapacidad motriz. Permite escribir, borrar y usar sugerencias de palabras usando solo el movimiento del dedo índice frente a una cámara web, sin hardware especial.

---

## 📋 Requisitos

- Python 3.8 o superior
- MediaPipe
- OpenCV (`opencv-python`)
- PyTorch
- Pygame
- NumPy

Puedes instalar todas las dependencias ejecutando:
- pip install mediapipe opencv-python torch pygame numpy


---

## 📁 Archivos principales

- `main.py`: Archivo principal para ejecutar el prototipo.
- `KeyboardLogic.py`: Lógica del teclado virtual y autocompletado.
- `KeyboardUI.py`: Interfaz gráfica del teclado.
- `config.py`: Parámetros de configuración visual.
- `palabras.txt`: Archivo de palabras para entrenar el modelo de autocompletado.
- `sounds/`: Carpeta que contiene los archivos de sonido para la retroalimentación al presionar teclas.

---

## 🚀 ¿Cómo ejecutar el prototipo?

1. **Clona este repositorio o descarga los archivos en tu computadora.**
2. **Asegúrate de tener una cámara web conectada y funcionando.**
3. **Instala las dependencias necesarias** (ver sección de requisitos).
4. **Ejecuta el archivo principal:**



5. **Al iniciar, el sistema entrenará el modelo de autocompletado**  
(esto puede tardar unos minutos la primera vez).  
En la consola se mostrarán mensajes sobre el avance del entrenamiento.

6. **Cuando aparezca la interfaz gráfica:**
- Mueve el dedo índice frente a la cámara para seleccionar teclas.
- Mantén el dedo sobre una tecla para escribir el carácter.
- Para borrar una palabra completa, junta el dedo índice y el pulgar sobre la tecla de borrar durante 4 segundos.
- Usa las sugerencias de palabras para escribir más rápido.

---

## 📝 Notas

- Si el modelo ya fue entrenado antes, se cargará automáticamente y el inicio será más rápido.
- Puedes modificar el archivo `palabras.txt` para personalizar el vocabulario del autocompletado.
- El sistema está pensado para funcionar en Windows, pero puede adaptarse a otros sistemas operativos con Python.

---

## 👨‍💻 Créditos

Desarrollado como prototipo de accesibilidad para personas con discapacidad motriz.

---

