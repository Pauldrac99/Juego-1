# Contexto del Proyecto - Juego de Disparos 2D

## Descripción
Juego de disparos en 2D desarrollado en Python utilizando Pygame, con gráficos basados únicamente en figuras geométricas simples (rectángulos y círculos).

## Repositorio
- GitHub: https://github.com/Pauldrac99/Juego-1.git

## Ubicación de archivos
- `juego_disparos.py` - Script principal del juego (único archivo, contiene todo el código)
- `context.md` - Este archivo, registro de avances y cambios

## Características implementadas
- Multijugador para 2 jugadores en la misma pantalla
- Jugador 1 (cuadrado azul, izquierda): movimiento con A / D, dispara con ESPACIO
- Jugador 2 (cuadrado verde, derecha): movimiento con flechas izquierda / derecha, dispara con K
- Disparos (rectángulos) de colores distintos por jugador (amarillo y cian)
- Enemigos (círculos rojos) que caen desde la parte superior en posiciones X aleatorias
- Colisión disparo-círculo (algoritmo círculo-rectángulo): enemigo y disparo desaparecen, +10 puntos para el jugador que disparó
- Puntuaciones individuales mostradas en las esquinas superiores (P1 izquierda, P2 derecha)
- Game Over si un enemigo llega al fondo; se reinicia con la tecla R
- Dificultad progresiva: los enemigos aparecen cada vez más rápido
- Ventana 800x600, 60 FPS
- Sonidos generados sintéticamente (sin archivos externos): disparo, explosión y game over

## Dependencias
- Python 3.14.2
- pygame-ce 2.5.8 (reemplazo directo del módulo `pygame`; install con `pip install pygame-ce`)

## Historial de cambios

### v1.0.0 (actual)
- Creación inicial del juego completo en un único script
- Implementación de jugador, disparos, enemigos, colisiones, puntuación y game over
- Instalación de pygame-ce debido a problemas de compilación de pygame estándar desde código fuente en Windows/Python 3.14

## Pendientes / Mejoras futuras
- Añadir sonidos y música (requeriría archivos de audio)
- Añadir niveles, vidas del jugador, power-ups
- Guardar puntuación máxima (high score)
- Menú principal y pantalla de opciones
- Soporte para gamepad / control