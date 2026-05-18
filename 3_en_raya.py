import sys
import copy
import time
import pygame

# --- CONFIGURACIÓN DE PYGAME ---
pygame.init()
pygame.font.init()

# Dimensiones
TABLERO_ANCHO, TABLERO_ALTO = 300, 300
PANEL_ANCHO = 200
ANCHO = TABLERO_ANCHO + PANEL_ANCHO
ALTO = TABLERO_ALTO

LINEA_ANCHO = 5
FILAS, COLUMNAS = 3, 3
TAMANO_CUADRANTE = TABLERO_ANCHO // COLUMNAS

# Colores
BG_COLOR = (28, 170, 156)
PANEL_COLOR = (23, 145, 135)
LINEA_COLOR = (20, 125, 115)
TEXT_COLOR = (255, 255, 255)
X_COLOR = (84, 84, 84)
O_COLOR = (242, 235, 211)

# Inicializar ventana, reloj y fuentes
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tres en Raya - IA Animada")
reloj = pygame.time.Clock()  # Para controlar los FPS de la animación
FUENTE = pygame.font.SysFont("Arial", 22, bold=True)
FUENTE_TITULO = pygame.font.SysFont("Arial", 18, bold=True)

# --- CONSTANTES DEL JUEGO ---
X = "X"
O = "O"
EMPTY = None

# Diccionario para controlar la animación de cada casilla
# Guardará {(fila, columna): progreso_de_0_a_1}
progreso_animacion = {}
VELOCIDAD_ANIM = 0.08  # Qué tan rápido se dibuja (a 60 FPS)

def initial_state():
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

# --- MÉTODOS LÓGICOS ---

def player(board):
    count_x = sum(row.count(X) for row in board)
    count_o = sum(row.count(O) for row in board)
    return O if count_x > count_o else X

def actions(board):
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] == EMPTY}

def result(board, action):
    i, j = action
    if board[i][j] is not EMPTY:
        raise Exception("Casilla ocupada.")
    nuevo_tablero = copy.deepcopy(board)
    nuevo_tablero[i][j] = player(board)
    return nuevo_tablero

def winner(board):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not EMPTY:
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not EMPTY:
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not EMPTY:
        return board[0][2]
    return None

def terminal(board):
    if winner(board) is not None:
        return True
    return not any(EMPTY in row for row in board)

def utility(board):
    ganador = winner(board)
    if ganador == X:
        return 1
    elif ganador == O:
        return -1
    return 0

# --- ALGORITMO MINIMAX ---

def minimax(board):
    if terminal(board):
        return None
    
    if player(board) == X:
        mejor_valor = -float('inf')
        mejor_accion = None
        for action in actions(board):
            valor = min_value(result(board, action))
            if valor > mejor_valor:
                mejor_valor, mejor_accion = valor, action
        return mejor_accion
    else:
        mejor_valor = float('inf')
        mejor_accion = None
        for action in actions(board):
            valor = max_value(result(board, action))
            if valor < mejor_valor:
                mejor_valor, mejor_accion = valor, action
        return mejor_accion

def max_value(board):
    if terminal(board): return utility(board)
    v = -float('inf')
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    if terminal(board): return utility(board)
    v = float('inf')
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

# --- INTERFAZ GRÁFICA Y ANIMACIONES ---

def dibujar_lineas():
    pygame.draw.line(pantalla, LINEA_COLOR, (0, TAMANO_CUADRANTE), (TABLERO_ANCHO, TAMANO_CUADRANTE), LINEA_ANCHO)
    pygame.draw.line(pantalla, LINEA_COLOR, (0, 2 * TAMANO_CUADRANTE), (TABLERO_ANCHO, 2 * TAMANO_CUADRANTE), LINEA_ANCHO)
    pygame.draw.line(pantalla, LINEA_COLOR, (TAMANO_CUADRANTE, 0), (TAMANO_CUADRANTE, ALTO), LINEA_ANCHO)
    pygame.draw.line(pantalla, LINEA_COLOR, (2 * TAMANO_CUADRANTE, 0), (2 * TAMANO_CUADRANTE, ALTO), LINEA_ANCHO)

def dibujar_figuras_animadas(board):
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            jugador = board[fila][col]
            if jugador is not EMPTY:
                # Registrar nueva figura para animar si no existe
                if (fila, col) not in progreso_animacion:
                    progreso_animacion[(fila, col)] = 0.0
                
                # Aumentar el progreso de la animación
                if progreso_animacion[(fila, col)] < 1.0:
                    progreso_animacion[(fila, col)] = min(1.0, progreso_animacion[(fila, col)] + VELOCIDAD_ANIM)
                
                p = progreso_animacion[(fila, col)]
                
                # Calcular coordenadas base
                cx = col * TAMANO_CUADRANTE + TAMANO_CUADRANTE // 2
                cy = fila * TAMANO_CUADRANTE + TAMANO_CUADRANTE // 2
                offset = TAMANO_CUADRANTE // 2 - 20

                if jugador == X:
                    # Animar X dibujando la primera línea y luego la segunda
                    if p <= 0.5:
                        # Primera línea parcial
                        p1 = p * 2
                        fin_x = cx - offset + int(p1 * 2 * offset)
                        fin_y = cy - offset + int(p1 * 2 * offset)
                        pygame.draw.line(pantalla, X_COLOR, (cx - offset, cy - offset), (fin_x, fin_y), 12)
                    else:
                        # Primera línea completa
                        pygame.draw.line(pantalla, X_COLOR, (cx - offset, cy - offset), (cx + offset, cy + offset), 12)
                        # Segunda línea parcial
                        p2 = (p - 0.5) * 2
                        fin_x = cx - offset + int(p2 * 2 * offset)
                        fin_y = cy + offset - int(p2 * 2 * offset)
                        pygame.draw.line(pantalla, X_COLOR, (cx - offset, cy + offset), (fin_x, fin_y), 12)

                elif jugador == O:
                    # Animar O expandiendo el radio
                    radio_maximo = offset
                    radio_actual = max(1, int(radio_maximo * p))
                    grosor = min(12, radio_actual)
                    pygame.draw.circle(pantalla, O_COLOR, (cx, cy), radio_actual, grosor)

def dibujar_panel(board, ia_pensando):
    pygame.draw.rect(pantalla, PANEL_COLOR, (TABLERO_ANCHO, 0, PANEL_ANCHO, ALTO))
    pygame.draw.line(pantalla, LINEA_COLOR, (TABLERO_ANCHO, 0), (TABLERO_ANCHO, ALTO), LINEA_ANCHO)

    if terminal(board):
        ganador = winner(board)
        if ganador is None:
            texto_estado = "EMPATE"
        else:
            texto_estado = f"GANADOR: {ganador}"
    else:
        if ia_pensando:
            texto_estado = "PENSANDO..."
        else:
            turno_actual = player(board)
            texto_estado = f"TURNO: {turno_actual}"

    txt_titulo = FUENTE_TITULO.render("TRES EN RAYA", True, TEXT_COLOR)
    txt_info = FUENTE.render(texto_estado, True, TEXT_COLOR)
    
    pantalla.blit(txt_titulo, (TABLERO_ANCHO + (PANEL_ANCHO - txt_titulo.get_width()) // 2, 40))
    pantalla.blit(txt_info, (TABLERO_ANCHO + (PANEL_ANCHO - txt_info.get_width()) // 2, 130))

# --- BUCLE PRINCIPAL ---

def main():
    tablero = initial_state()
    user = X  
    
    reinicio_pendiente = False
    tiempo_final = 0

    ia_pensando = False
    tiempo_inicio_ia = 0
    accion_ia_pendiente = None

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Click del usuario (Solo si la IA no está pensando)
            if evento.type == pygame.MOUSEBUTTONDOWN and not terminal(tablero) and not ia_pensando:
                if player(tablero) == user:
                    pos_x, pos_y = evento.pos
                    if pos_x < TABLERO_ANCHO:
                        fila_click = pos_y // TAMANO_CUADRANTE
                        col_click = pos_x // TAMANO_CUADRANTE
                        if (fila_click, col_click) in actions(tablero):
                            tablero = result(tablero, (fila_click, col_click))

        # Lógica del turno de la IA (Simulación de pensamiento)
        if not terminal(tablero) and player(tablero) != user:
            if not ia_pensando:
                # Comienza a "pensar"
                ia_pensando = True
                tiempo_inicio_ia = time.time()
                # Calcula la jugada óptima inmediatamente, pero no la aplica aún
                accion_ia_pendiente = minimax(tablero)
            else:
                # Espera 1 segundo (1.0) simulando pensamiento
                if time.time() - tiempo_inicio_ia > 1.0:
                    if accion_ia_pendiente is not None:
                        tablero = result(tablero, accion_ia_pendiente)
                    ia_pensando = False
                    accion_ia_pendiente = None

        # Renderizado
        pantalla.fill(BG_COLOR)
        dibujar_lineas()
        dibujar_figuras_animadas(tablero)
        dibujar_panel(tablero, ia_pensando)
        pygame.display.update()

        # Lógica de reinicio
        if terminal(tablero):
            if not reinicio_pendiente:
                reinicio_pendiente = True
                tiempo_final = time.time()
            
            # Espera 3 segundos al finalizar y limpia todo
            if time.time() - tiempo_final > 3.0:
                tablero = initial_state()
                progreso_animacion.clear()  # Limpia las animaciones para el nuevo juego
                reinicio_pendiente = False

        # Fija los cuadros por segundo a 60 para que la animación sea fluida
        reloj.tick(60)

if __name__ == "__main__":
    main()