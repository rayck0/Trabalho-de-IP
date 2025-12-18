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
    def __init__(self, pos, grupos, sheet, frames, larg_orig, alt_orig, tam_final, velocidade, vida, inverter_olhar=False):
        super().__init__(grupos)
        self.sprites_direita = [] 
        self.sprites_esquerda = [] 
        
        # Recorte e Escala
        for x in range(frames):
            corte = sheet.subsurface((x * larg_orig, 0), (larg_orig, alt_orig))
            img_redim = pygame.transform.scale(corte, (tam_final, tam_final))
        
            if inverter_olhar:
                # Se o desenho original olha para a ESQUERDA:
                # A lista 'direita' precisa ser a imagem flipada
                self.sprites_direita.append(pygame.transform.flip(img_redim, True, False))
                # A lista 'esquerda' é a imagem original
                self.sprites_esquerda.append(img_redim)
            else:
                # Se o desenho original olha para a DIREITA (Padrão):
                # A lista 'direita' é a original
                self.sprites_direita.append(img_redim)
                # A lista 'esquerda' é a flipada
                self.sprites_esquerda.append(pygame.transform.flip(img_redim, True, False))
            
        self.index = 0
        self.olhando_direita = True 
        self.image = self.sprites_direita[0]
        self.rect = self.image.get_rect(topleft=pos)
        
        # Física e Vida
        self.pos_real = pygame.math.Vector2(self.rect.topleft)
        self.velocidade = velocidade
        self.vida = vida
        self.vida_maxima = vida 
        
        self.hit_timer = 0 

    def cacar_jogador(self, player):
        direcao = player.PosicaoReal - self.pos_real
        if direcao.magnitude() > 0:
            # Decide para onde olhar
            if direcao.x > 0:
                self.olhando_direita = True
            elif direcao.x < 0:
                self.olhando_direita = False

            direcao = direcao.normalize()
            self.pos_real += direcao * self.velocidade
            self.rect.center = round(self.pos_real.x), round(self.pos_real.y)

    def receber_dano(self, quantidade):
        self.vida -= quantidade
        self.hit_timer = 5 
        
        if self.vida <= 0:
            self.kill() 
            return True 
        return False 

    def update(self):
        self.index += 0.15
        
        sprites_atuais = self.sprites_direita if self.olhando_direita else self.sprites_esquerda
        
        if self.index >= len(sprites_atuais): self.index = 0
        
        imagem_atual = sprites_atuais[int(self.index)]
        
        if self.hit_timer > 0:
            self.hit_timer -= 1
            imagem_flash = imagem_atual.copy()
            imagem_flash.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
            self.image = imagem_flash
        else:
            self.image = imagem_atual

# CONFIGURAÇÃO DOS INIMIGOS

class RoboVoador(InimigoPadrao):
    def __init__(self, pos, grupos):
        # Padrão: inverter_olhar=False
        super().__init__(pos, grupos, sheet_voador, 8, 88, 64, 64, velocidade=3.0, vida=30)

class RoboBola(InimigoPadrao): 
    def __init__(self, pos, grupos):
        # A Bola precisava inverter
        super().__init__(pos, grupos, sheet_bola, 4, 64, 64, 64, velocidade=2.5, vida=40, inverter_olhar=True)

class RoboZangao(InimigoPadrao): 
    def __init__(self, pos, grupos):
        # O Zangão precisava inverter
        super().__init__(pos, grupos, sheet_zangao, 4, 64, 64, 64, velocidade=2.0, vida=60, inverter_olhar=True)

class RoboCobra(InimigoPadrao): 
    def __init__(self, pos, grupos):
        super().__init__(pos, grupos, sheet_cobra, 5, 64, 64, 256, velocidade=1.5, vida=150)

class RoboDragao(InimigoPadrao): 
    def __init__(self, pos, grupos):
        super().__init__(pos, grupos, sheet_dragao, 6, 256, 256, 570, velocidade=1.0, vida=500)
