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
NEGRO    = (0, 0, 0)
BLANCO   = (255, 255, 255)
ROJO     = (255, 0, 0)
VERDE    = (0, 255, 0)
AZUL     = (0, 0, 255)
AMARILLO = (255, 255, 0)
CIAN     = (0, 255, 255)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Disparos 2D - 2 Jugadores (Pygame)")
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
    sonido_disparo = sonido_explosion = sonido_game_over = None

# ---------------------------------------------------------------------------
# Jugador 1 (izquierda) - cuadrado azul
# ---------------------------------------------------------------------------
JUGADOR_TAM = 50
jugador1_x = 100
jugador1_y = ALTO - JUGADOR_TAM - 15
jugador1_vel = 7
jugador1_disparo_enfriamiento = 0

# ---------------------------------------------------------------------------
# Jugador 2 (derecha) - cuadrado verde
# ---------------------------------------------------------------------------
jugador2_x = ANCHO - 100 - JUGADOR_TAM
jugador2_y = ALTO - JUGADOR_TAM - 15
jugador2_vel = 7
jugador2_disparo_enfriamiento = 0

# ---------------------------------------------------------------------------
# Disparos (rectĆˇngulos que suben)
# ---------------------------------------------------------------------------
DISPARO_ANCHO = 6
DISPARO_ALTO = 15
DISPARO_VEL = -9
disparos_p1 = []  # amarillos
disparos_p2 = []  # cian

# ---------------------------------------------------------------------------
# Enemigos (cĆ­rculos rojos que caen desde arriba)
# ---------------------------------------------------------------------------
ENEMIGO_RADIO = 20
ENEMIGO_VEL = 4
enemigos = []
enemigo_timer = 0
ENEMIGO_TIEMPO_SPAWN = 45  # frames entre apariciones

# ---------------------------------------------------------------------------
# Puntuaciones
# ---------------------------------------------------------------------------
puntuacion1 = 0
puntuacion2 = 0
juego_activo = True


def spawn_enemigo():
    """Crea un nuevo enemigo en una posiciĆ³n X aleatoria en la parte superior."""
    x = random.randint(ENEMIGO_RADIO, ANCHO - ENEMIGO_RADIO)
    y = -ENEMIGO_RADIO
    rect = pygame.Rect(x - ENEMIGO_RADIO, y - ENEMIGO_RADIO,
                       ENEMIGO_RADIO * 2, ENEMIGO_RADIO * 2)
    return {"rect": rect, "radio": ENEMIGO_RADIO}


def disparar_jugador1():
    """Crea un nuevo disparo desde la posiciĆ³n del jugador 1."""
    bx = jugador1_x + JUGADOR_TAM // 2 - DISPARO_ANCHO // 2
    by = jugador1_y
    rect = pygame.Rect(bx, by, DISPARO_ANCHO, DISPARO_ALTO)
    disparos_p1.append(rect)


def disparar_jugador2():
    """Crea un nuevo disparo desde la posiciĆ³n del jugador 2."""
    bx = jugador2_x + JUGADOR_TAM // 2 - DISPARO_ANCHO // 2
    by = jugador2_y
    rect = pygame.Rect(bx, by, DISPARO_ANCHO, DISPARO_ALTO)
    disparos_p2.append(rect)


def colision_circulo_rect(cx, cy, radio, rect):
    """Detecta colisiĆ³n entre un cĆ­rculo y un rectĆˇngulo."""
    cx_cercano = max(rect.left, min(cx, rect.right))
    cy_cercano = max(rect.top, min(cy, rect.bottom))
    dx = cx - cx_cercano
    dy = cy - cy_cercano
    return dx * dx + dy * dy <= radio * radio


def reiniciar_juego():
    """Reinicia todas las variables del juego para volver a jugar."""
    global jugador1_x, jugador2_x, disparos_p1, disparos_p2, enemigos
    global puntuacion1, puntuacion2, juego_activo
    global enemigo_timer, jugador1_disparo_enfriamiento, jugador2_disparo_enfriamiento

    jugador1_x = 100
    jugador2_x = ANCHO - 100 - JUGADOR_TAM
    disparos_p1.clear()
    disparos_p2.clear()
    enemigos.clear()
    puntuacion1 = 0
    puntuacion2 = 0
    juego_activo = True
    enemigo_timer = 0
    jugador1_disparo_enfriamiento = 0
    jugador2_disparo_enfriamiento = 0


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
        # --- Movimiento del jugador 1 (A / D) ------------------------------
        teclas = pygame.key.get_pressed()
        if (teclas[pygame.K_a] or teclas[pygame.K_LEFT]) and jugador1_x > 0:
            # SOLO jugador 1 usa A; flecha izquierda es compartida con P2 si
            # ambos la presionan, pero aquí priorizamos A para P1.
            if teclas[pygame.K_a]:
                jugador1_x -= jugador1_vel
        if (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) and jugador1_x < ANCHO - JUGADOR_TAM:
            if teclas[pygame.K_d]:
                jugador1_x += jugador1_vel

        # --- Movimiento del jugador 2 (flechas izquierda / derecha) -------
        if teclas[pygame.K_LEFT] and jugador2_x > 0:
            jugador2_x -= jugador2_vel
        if teclas[pygame.K_RIGHT] and jugador2_x < ANCHO - JUGADOR_TAM:
            jugador2_x += jugador2_vel

        # --- Disparar ------------------------------------------------------
        if teclas[pygame.K_SPACE] and jugador1_disparo_enfriamiento <= 0:
            disparar_jugador1()
            jugador1_disparo_enfriamiento = 12
        if jugador1_disparo_enfriamiento > 0:
            jugador1_disparo_enfriamiento -= 1

        if teclas[pygame.K_k] and jugador2_disparo_enfriamiento <= 0:
            disparar_jugador2()
            jugador2_disparo_enfriamiento = 12
        if jugador2_disparo_enfriamiento > 0:
            jugador2_disparo_enfriamiento -= 1

        # --- Actualizar disparos jugador 1 ---------------------------------
        for disparo in disparos_p1[:]:
            disparo.y += DISPARO_VEL
            if disparo.bottom < 0:
                disparos_p1.remove(disparo)

        # --- Actualizar disparos jugador 2 ---------------------------------
        for disparo in disparos_p2[:]:
            disparo.y += DISPARO_VEL
            if disparo.bottom < 0:
                disparos_p2.remove(disparo)

        # --- Actualizar enemigos -------------------------------------------
        enemigo_timer += 1
        if enemigo_timer >= ENEMIGO_TIEMPO_SPAWN:
            enemigos.append(spawn_enemigo())
            enemigo_timer = 0
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

            # ColisiĆ³n disparos jugador 1 vs enemigo
            golpeado = False
            for disparo in disparos_p1[:]:
                if colision_circulo_rect(enemigo["rect"].centerx,
                                         enemigo["rect"].centery,
                                         enemigo["radio"], disparo):
                    if disparo in disparos_p1:
                        disparos_p1.remove(disparo)
                    enemigos.remove(enemigo)
                    puntuacion1 += 10
                    if sonido_explosion:
                        sonido_explosion.play()
                    golpeado = True
                    break
            if golpeado:
                continue

            # ColisiĆ³n disparos jugador 2 vs enemigo
            for disparo in disparos_p2[:]:
                if colision_circulo_rect(enemigo["rect"].centerx,
                                         enemigo["rect"].centery,
                                         enemigo["radio"], disparo):
                    if disparo in disparos_p2:
                        disparos_p2.remove(disparo)
                    enemigos.remove(enemigo)
                    puntuacion2 += 10
                    if sonido_explosion:
                        sonido_explosion.play()
                    golpeado = True
                    break
            if golpeado:
                continue

    # --- Dibujado ----------------------------------------------------------
    pantalla.fill(NEGRO)

    # Jugador 1 (cuadrado azul)
    pygame.draw.rect(pantalla, AZUL,
                     (jugador1_x, jugador1_y, JUGADOR_TAM, JUGADOR_TAM))

    # Jugador 2 (cuadrado verde)
    pygame.draw.rect(pantalla, VERDE,
                     (jugador2_x, jugador2_y, JUGADOR_TAM, JUGADOR_TAM))

    # Disparos jugador 1 (amarillos)
    for disparo in disparos_p1:
        pygame.draw.rect(pantalla, AMARILLO, disparo)

    # Disparos jugador 2 (cian)
    for disparo in disparos_p2:
        pygame.draw.rect(pantalla, CIAN, disparo)

    # Enemigos (cĆ­rculos rojos)
    for enemigo in enemigos:
        pygame.draw.circle(pantalla, ROJO,
                           enemigo["rect"].center, enemigo["radio"])

    # Puntuaciones
    texto_p1 = fuente.render(f"Jugador 1: {puntuacion1}", True, AZUL)
    texto_p2 = fuente.render(f"Jugador 2: {puntuacion2}", True, VERDE)
    pantalla.blit(texto_p1, (10, 10))
    pantalla.blit(texto_p2, (ANCHO - texto_p2.get_width() - 10, 10))

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
