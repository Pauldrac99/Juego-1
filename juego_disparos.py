import pygame
import random
import sys
import array
import math

# ---------------------------------------------------------------------------
# InicializaciĆ³n de Pygame
# ---------------------------------------------------------------------------
pygame.init()

# ---------------------------------------------------------------------------
# Constantes y configuraciĆ³n de la ventana
# ---------------------------------------------------------------------------
ANCHO = 800
ALTO = 600
FPS = 60

# Colores (RGB)
NEGRO   = (0, 0, 0)
BLANCO  = (255, 255, 255)
ROJO    = (255, 0, 0)
VERDE   = (0, 255, 0)
AZUL    = (0, 0, 255)
AMARILLO= (255, 255, 0)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Disparos 2D - Pygame")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("arial", 28)
fuente_grande = pygame.font.SysFont("arial", 48)

# ---------------------------------------------------------------------------
# Audio (sonidos generados sinteticamente, sin archivos externos)
# ---------------------------------------------------------------------------
SAMPLE_RATE = 22050
sonido_disparo = None
sonido_explosion = None
sonido_game_over = None

try:
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)

    def generar_tono(frecuencia, duracion, volumen=0.5, decay=True):
        n_samples = int(SAMPLE_RATE * duracion)
        buf = array.array('h', [0]) * n_samples
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            valor = int(volumen * 32767 * math.sin(2 * math.pi * frecuencia * t))
            if decay:
                fade = 1.0 - (i / n_samples)
                valor = int(valor * fade * fade)
            buf[i] = valor
        return buf.tobytes()

    def generar_ruido(duracion, volumen=0.4):
        n_samples = int(SAMPLE_RATE * duracion)
        buf = array.array('h', [0]) * n_samples
        for i in range(n_samples):
            valor = int(volumen * 32767 * (2.0 * random.random() - 1.0))
            fade = 1.0 - (i / n_samples)
            buf[i] = int(valor * fade * fade)
        return buf.tobytes()

    sonido_disparo = pygame.mixer.Sound(buffer=generar_tono(880, 0.12, 0.4))
    sonido_explosion = pygame.mixer.Sound(buffer=generar_ruido(0.25, 0.5))
    sonido_game_over = pygame.mixer.Sound(buffer=generar_tono(220, 0.8, 0.5, decay=False))
except Exception:
    # Si no hay dispositivo de audio, el juego sigue funcionando sin sonidos
    sonido_disparo = sonido_explosion = sonido_game_over = None

# ---------------------------------------------------------------------------
# Jugador (cuadrado en la parte inferior)
# ---------------------------------------------------------------------------
JUGADOR_TAM = 50
jugador_x = ANCHO // 2 - JUGADOR_TAM // 2
jugador_y = ALTO - JUGADOR_TAM - 15
jugador_vel = 7

# ---------------------------------------------------------------------------
# Disparos (rectĆˇngulos que suben)
# ---------------------------------------------------------------------------
DISPARO_ANCHO = 6
DISPARO_ALTO = 15
DISPARO_VEL = -9
disparos = []
disparo_enfriamiento = 0  # frames entre disparos

# ---------------------------------------------------------------------------
# Enemigos (cĆ­rculos que caen desde arriba)
# ---------------------------------------------------------------------------
ENEMIGO_RADIO = 20
ENEMIGO_VEL = 4
enemigos = []
enemigo_timer = 0
ENEMIGO_TIEMPO_SPAWN = 45  # frames entre apariciones

# ---------------------------------------------------------------------------
# PuntuaciĆ³n
# ---------------------------------------------------------------------------
puntuacion = 0
juego_activo = True


def spawn_enemigo():
    """Crea un nuevo enemigo en una posiciĆ³n X aleatoria en la parte superior."""
    x = random.randint(ENEMIGO_RADIO, ANCHO - ENEMIGO_RADIO)
    y = -ENEMIGO_RADIO
    rect = pygame.Rect(x - ENEMIGO_RADIO, y - ENEMIGO_RADIO,
                       ENEMIGO_RADIO * 2, ENEMIGO_RADIO * 2)
    return {"rect": rect, "radio": ENEMIGO_RADIO}


def disparar():
    """Crea un nuevo disparo desde la posiciĆ³n del jugador."""
    bx = jugador_x + JUGADOR_TAM // 2 - DISPARO_ANCHO // 2
    by = jugador_y
    rect = pygame.Rect(bx, by, DISPARO_ANCHO, DISPARO_ALTO)
    disparos.append(rect)
    if sonido_disparo:
        sonido_disparo.play()


def colision_circulo_rect(cx, cy, radio, rect):
    """Detecta colisiĆ³n entre un cĆ­rculo y un rectĆˇngulo."""
    cx_cercano = max(rect.left, min(cx, rect.right))
    cy_cercano = max(rect.top, min(cy, rect.bottom))
    dx = cx - cx_cercano
    dy = cy - cy_cercano
    return dx * dx + dy * dy <= radio * radio


def reiniciar_juego():
    """Reinicia todas las variables del juego para volver a jugar."""
    global jugador_x, disparos, enemigos, puntuacion, juego_activo
    global enemigo_timer, disparo_enfriamiento
    jugador_x = ANCHO // 2 - JUGADOR_TAM // 2
    disparos.clear()
    enemigos.clear()
    puntuacion = 0
    juego_activo = True
    enemigo_timer = 0
    disparo_enfriamiento = 0


# ---------------------------------------------------------------------------
# Bucle principal del juego
# ---------------------------------------------------------------------------
while True:
    # --- Eventos -----------------------------------------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if not juego_activo and evento.key == pygame.K_r:
                reiniciar_juego()

    if juego_activo:
        # --- Movimiento del jugador ----------------------------------------
        teclas = pygame.key.get_pressed()
        if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and jugador_x > 0:
            jugador_x -= jugador_vel
        if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and jugador_x < ANCHO - JUGADOR_TAM:
            jugador_x += jugador_vel

        # --- Disparar con la barra espaciadora -----------------------------
        if teclas[pygame.K_SPACE] and disparo_enfriamiento <= 0:
            disparar()
            disparo_enfriamiento = 12  # pequeĆ±a pausa entre disparos
        if disparo_enfriamiento > 0:
            disparo_enfriamiento -= 1

        # --- Actualizar disparos -------------------------------------------
        for disparo in disparos[:]:
            disparo.y += DISPARO_VEL
            if disparo.bottom < 0:
                disparos.remove(disparo)

        # --- Actualizar enemigos -------------------------------------------
        enemigo_timer += 1
        if enemigo_timer >= ENEMIGO_TIEMPO_SPAWN:
            enemigos.append(spawn_enemigo())
            enemigo_timer = 0
            # Hacer el juego progresivamente mĆˡs difĆ­cil
            if ENEMIGO_TIEMPO_SPAWN > 20:
                ENEMIGO_TIEMPO_SPAWN -= 1

        for enemigo in enemigos[:]:
            enemigo["rect"].y += ENEMIGO_VEL

            # Si un enemigo llega al fondo, termina el juego
            if enemigo["rect"].top > ALTO:
                juego_activo = False
                if sonido_game_over:
                    sonido_game_over.play()
                enemigos.remove(enemigo)
                continue

            # ColisiĆ³n disparo vs enemigo
            golpeado = False
            for disparo in disparos[:]:
                if colision_circulo_rect(enemigo["rect"].centerx,
                                         enemigo["rect"].centery,
                                         enemigo["radio"], disparo):
                    if disparo in disparos:
                        disparos.remove(disparo)
                    enemigos.remove(enemigo)
                    puntuacion += 10
                    if sonido_explosion:
                        sonido_explosion.play()
                    golpeado = True
                    break
            if golpeado:
                continue

    # --- Dibujado ----------------------------------------------------------
    pantalla.fill(NEGRO)

    # Jugador (cuadrado azul)
    pygame.draw.rect(pantalla, AZUL,
                     (jugador_x, jugador_y, JUGADOR_TAM, JUGADOR_TAM))

    # Disparos (rectĆˇngulos amarillos)
    for disparo in disparos:
        pygame.draw.rect(pantalla, AMARILLO, disparo)

    # Enemigos (cĆ­rculos rojos)
    for enemigo in enemigos:
        pygame.draw.circle(pantalla, ROJO,
                           enemigo["rect"].center, enemigo["radio"])

    # PuntuaciĆ³n (esquina superior izquierda)
    texto_puntuacion = fuente.render(f"PuntuaciĆ³n: {puntuacion}", True, BLANCO)
    pantalla.blit(texto_puntuacion, (10, 10))

    if not juego_activo:
        texto_game_over = fuente_grande.render("GAME OVER", True, ROJO)
        texto_reiniciar = fuente.render("Presiona R para reiniciar", True, BLANCO)
        pantalla.blit(texto_game_over,
                      (ANCHO // 2 - texto_game_over.get_width() // 2,
                       ALTO // 2 - 40))
        pantalla.blit(texto_reiniciar,
                      (ANCHO // 2 - texto_reiniciar.get_width() // 2,
                       ALTO // 2 + 20))

    pygame.display.flip()
    reloj.tick(FPS)
