# config.py
import pygame

# TELA e DISPLAY 
LARGURA_TELA = 1280
ALTURA_TELA = 720
FPS = 60
TAMANHO_TILE = 64

#define tamanho do mapa
LARGURA_MUNDO = 3000
ALTURA_MUNDO = 3000

# CORES (RGB) 
COR_PRETA = (0, 0, 0)
COR_BRANCA = (255, 255, 255)
COR_VERMELHA = (200, 50, 50) 
COR_VERDE_CLARO = (50, 255, 50) 
COR_AZUL = (50, 50, 255)
COR_DOURADA = (255, 215, 0)

# UI & COMBATE
BARRA_VIDA_LARGURA = 200
BARRA_VIDA_ALTURA = 20
COR_UI_BORDA = COR_BRANCA
COR_UI_FUNDO = (50, 50, 50) # Cinza escuro
COR_VIDA = COR_VERMELHA

# Dano que o jogador leva ao encostar no inimigo
DANO_INIMIGO = 10
# Tempo que fica invencível (em milissegundos)
TEMPO_INVENCIVEL = 500