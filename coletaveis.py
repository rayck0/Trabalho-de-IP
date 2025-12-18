import pygame
import math
import os
from config import *

DIRETORIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sprites')

# Carrega as imagens
img_vida = pygame.image.load(os.path.join(DIRETORIO, 'Coletavel_vida.png')).convert_alpha()
img_xp = pygame.image.load(os.path.join(DIRETORIO, 'Coletavel_experiencia.png')).convert_alpha()
img_moeda = pygame.image.load(os.path.join(DIRETORIO, 'Coletavel_moeda.png')).convert_alpha()

class Coletavel(pygame.sprite.Sprite):
    def __init__(self, tipo, pos, grupos):
        super().__init__(grupos)
        self.tipo = tipo
        self.sprites = []
        
        # CONFIGURAÇÃO DE TAMANHO
        # Aumenta o tamanho original em 3 vezes (Mude para 2 ou 4 se quiser)
        ESCALA = 3
        
        if self.tipo == 'vida':
            sheet = img_vida; frames_total = 4
        elif self.tipo == 'xp':
            sheet = img_xp; frames_total = 4
        else:
            sheet = img_moeda; frames_total = 4
            
        # Descobre tamanho original
        largura_sheet = sheet.get_width()
        altura_sheet = sheet.get_height()
        
        # CORTE + AUMENTO (SCALE)
        if largura_sheet > altura_sheet: # Horizontal
            largura_frame = largura_sheet // frames_total
            altura_frame = altura_sheet
            for x in range(frames_total):
                # Corta o pedacinho pequeno
                corte = sheet.subsurface((x * largura_frame, 0), (largura_frame, altura_frame))
                # Aumenta ele
                novo_tamanho = (largura_frame * ESCALA, altura_frame * ESCALA)
                img_grande = pygame.transform.scale(corte, novo_tamanho)
                self.sprites.append(img_grande)
                
        else: # Vertical
            largura_frame = largura_sheet
            altura_frame = altura_sheet // frames_total
            for y in range(frames_total):
                corte = sheet.subsurface((0, y * altura_frame), (largura_frame, altura_frame))
                # Aumenta ele
                novo_tamanho = (largura_frame * ESCALA, altura_frame * ESCALA)
                img_grande = pygame.transform.scale(corte, novo_tamanho)
                self.sprites.append(img_grande)

        if not self.sprites: self.sprites.append(sheet)

        self.index = 0
        self.image = self.sprites[self.index]
        self.rect = self.image.get_rect(center=pos)
        self.y_original = self.rect.centery
        self.timer_animacao = 0

    def update(self):
        # Animação
        self.index += 0.15
        if self.index >= len(self.sprites): self.index = 0
        self.image = self.sprites[int(self.index)]
        
        # Flutuar
        self.timer_animacao += 0.1
        self.rect.centery = self.y_original + math.sin(self.timer_animacao) * 5