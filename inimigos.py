import pygame
import os
from config import *

DIRETORIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sprites')

# Carregamento
sheet_voador = pygame.image.load(os.path.join(DIRETORIO, 'enemy_roboVoador.png')).convert_alpha()
sheet_dragao = pygame.image.load(os.path.join(DIRETORIO, 'enemy_roboDragao.png')).convert_alpha()
sheet_cobra  = pygame.image.load(os.path.join(DIRETORIO, 'enemy_roboCobra.png')).convert_alpha()
sheet_bola   = pygame.image.load(os.path.join(DIRETORIO, 'enemy_roboBola.png')).convert_alpha()
sheet_zangao = pygame.image.load(os.path.join(DIRETORIO, 'enemy_roboZangao.png')).convert_alpha()

class InimigoPadrao(pygame.sprite.Sprite):
    def __init__(self, pos, grupos, sheet, frames, larg_orig, alt_orig, tam_final, velocidade, vida):
        super().__init__(grupos)
        self.sprites = []
        
        # Recorte e Escala
        for x in range(frames):
            corte = sheet.subsurface((x * larg_orig, 0), (larg_orig, alt_orig))
            img_redim = pygame.transform.scale(corte, (tam_final, tam_final))
            self.sprites.append(img_redim)
            
        self.index = 0
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(topleft=pos)
        
        # Física e Vida
        self.pos_real = pygame.math.Vector2(self.rect.topleft)
        self.velocidade = velocidade
        self.vida = vida
        self.vida_maxima = vida # Útil se quisermos desenhar barra de vida depois
        
        # Controle do Pisca-Pisca flash do dano
        self.hit_timer = 0 

    def cacar_jogador(self, player):
        direcao = player.PosicaoReal - self.pos_real
        if direcao.magnitude() > 0:
            direcao = direcao.normalize()
            self.pos_real += direcao * self.velocidade
            self.rect.center = round(self.pos_real.x), round(self.pos_real.y)

    def receber_dano(self, quantidade):
        # Reduz a vida e ativa o flash branco
        self.vida -= quantidade
        self.hit_timer = 5 # Fica branco por 5 frames
        
        if self.vida <= 0:
            self.kill() # Remove do jogo
            return True # Retorna Verdadeiro (Morreu)
        return False # Retorna Falso (Ainda vivo)

    def update(self):
        # Animação Normal
        self.index += 0.15
        if self.index >= len(self.sprites): self.index = 0
        
        # Pega a imagem original do frame atual
        imagem_atual = self.sprites[int(self.index)]
        
        # Efeito de Dano (Piscar Branco)
        if self.hit_timer > 0:
            self.hit_timer -= 1
            # Cria uma cópia para não estragar a original
            imagem_flash = imagem_atual.copy()
            # Pinta de branco (BLEND_ADD soma cor, branco + cor = muito branco)
            imagem_flash.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
            self.image = imagem_flash
        else:
            # Se não tomou dano, mostra a imagem normal
            self.image = imagem_atual

# CONFIGURAÇÃO DE VIDA (HP)
# Player dá 10 de dano por tiro 

class RoboVoador(InimigoPadrao): # Morre em 3 tiros
    def __init__(self, pos, grupos):
        super().__init__(pos, grupos, sheet_voador, 8, 88, 64, 64, velocidade=3.0, vida=30)

class RoboBola(InimigoPadrao): # Morre em 4 tiros
    def __init__(self, pos, grupos):
        super().__init__(pos, grupos, sheet_bola, 4, 64, 64, 64, velocidade=2.5, vida=40)

class RoboZangao(InimigoPadrao): # Morre em 6 tiros
    def __init__(self, pos, grupos):
        super().__init__(pos, grupos, sheet_zangao, 4, 64, 64, 64, velocidade=2.0, vida=60)

class RoboCobra(InimigoPadrao): #MINI BOSS: Morre em 15 tiros
    def __init__(self, pos, grupos):
        super().__init__(pos, grupos, sheet_cobra, 5, 64, 64, 256, velocidade=1.5, vida=150)

class RoboDragao(InimigoPadrao): # BOSS: Morre em 50 tiros
    def __init__(self, pos, grupos):
        super().__init__(pos, grupos, sheet_dragao, 6, 256, 256, 570, velocidade=1.0, vida=500)