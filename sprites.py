import pygame
import os
import math
from config import *

# CONFIGURAÇÃO DE DIRETÓRIOS
DIRETORIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sprites')

# CARREGAMENTO DE IMAGENS

# BYTE (PERSONAGEM)
try:
    path = os.path.join(DIRETORIO, 'bytesspritesheet.png')
    img_original = pygame.image.load(path).convert_alpha()
    # Força o tamanho correto
    sheet_byte = pygame.transform.scale(img_original, (320, 128))
except:
    print("ERRO: Byte não encontrado")
    sheet_byte = pygame.Surface((320, 128)); sheet_byte.fill((255, 0, 255))

# MAPA chao
try:
    path_mapa = os.path.join(DIRETORIO, 'mapajogoip.jpg')
    img_tile = pygame.image.load(path_mapa).convert()
    imagem_fundo = pygame.Surface((LARGURA_MUNDO, ALTURA_MUNDO))
    tile_w = img_tile.get_width()
    tile_h = img_tile.get_height()
    # Preenche o chão vulgo Tiling
    for x in range(0, LARGURA_MUNDO, tile_w):
        for y in range(0, ALTURA_MUNDO, tile_h):
            imagem_fundo.blit(img_tile, (x, y))
except:
    print("ERRO: Mapa não encontrado")
    imagem_fundo = pygame.Surface((LARGURA_MUNDO, ALTURA_MUNDO)); imagem_fundo.fill((30, 30, 30))
# CLASSES

class GrupoCamera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.DisplaySurface = pygame.display.get_surface()
        self.HalfWidth = self.DisplaySurface.get_size()[0] // 2
        self.HalfHeight = self.DisplaySurface.get_size()[1] // 2
        self.Offset = pygame.math.Vector2()
        self.chao_rect = imagem_fundo.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        self.Offset.x = player.rect.centerx - self.HalfWidth
        self.Offset.y = player.rect.centery - self.HalfHeight

        #limitar camera no limite do mapa
        if self.Offset.x < 0: self.Offset.x = 0
        if self.Offset.y < 0: self.Offset.y = 0
        
        if self.Offset.x > LARGURA_MUNDO - LARGURA_TELA:
            self.Offset.x = LARGURA_MUNDO - LARGURA_TELA
        if self.Offset.y > ALTURA_MUNDO - ALTURA_TELA:
            self.Offset.y = ALTURA_MUNDO - ALTURA_TELA

        # Chão
        pos_chao = self.chao_rect.topleft - self.Offset
        self.DisplaySurface.blit(imagem_fundo, pos_chao)

        # Sprites (Y-Sort) p fazer o efeito de ficar na frente ou atras 
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            OffsetPos = sprite.rect.topleft - self.Offset
            self.DisplaySurface.blit(sprite.image, OffsetPos)

class Jogador(pygame.sprite.Sprite):
    def __init__(self, Posicao, Grupos):
        super().__init__(Grupos)
        
        # SPRITES
        self.sprites_direita = []
        self.sprites_esquerda = []
        for x in range(5): 
            img = sheet_byte.subsurface((x * 64, 0), (64, 64))
            self.sprites_direita.append(img)
            self.sprites_esquerda.append(pygame.transform.flip(img, True, False))

        self.index = 0
        self.olhando_direita = True
        self.image = self.sprites_direita[0]
        self.rect = self.image.get_rect(topleft=Posicao)
        
        # MOVIMENTO
        self.Direcao = pygame.math.Vector2()
        self.PosicaoReal = pygame.math.Vector2(self.rect.center)
        self.Velocidade = 4

        # COMBATE & VIDA
        self.vida_maxima = 100
        self.vida_atual = 100
        self.invencivel = False
        self.tempo_invencivel = 0 
        
        # Atributos de RPG p os upgrades
        self.dano_base = 10
        self.cooldown_tiro = 500 # ms
        
        # Sistema de XP
        self.nivel = 1
        self.xp_atual = 0
        self.xp_necessario = 100

    def Input(self):
        Keys = pygame.key.get_pressed()
        self.Direcao.x = 0; self.Direcao.y = 0
        if Keys[pygame.K_UP] or Keys[pygame.K_w]: self.Direcao.y = -1
        elif Keys[pygame.K_DOWN] or Keys[pygame.K_s]: self.Direcao.y = 1
        if Keys[pygame.K_RIGHT] or Keys[pygame.K_d]: self.Direcao.x = 1; self.olhando_direita = True
        elif Keys[pygame.K_LEFT] or Keys[pygame.K_a]: self.Direcao.x = -1; self.olhando_direita = False

    def Mover(self):
        if self.Direcao.magnitude() != 0:
            self.Direcao = self.Direcao.normalize()
        nova_pos = self.PosicaoReal + (self.Direcao * self.Velocidade)
        if 0 < nova_pos.x < 3000 and 0 < nova_pos.y < 3000:
            self.PosicaoReal = nova_pos
            self.rect.center = round(self.PosicaoReal.x), round(self.PosicaoReal.y)

    def Animar(self):
        if self.Direcao.magnitude() != 0:
            self.index += 0.25
            if self.index >= len(self.sprites_direita): self.index = 0
        else: self.index = 0

        if self.olhando_direita: frame_base = self.sprites_direita[int(self.index)]
        else: frame_base = self.sprites_esquerda[int(self.index)]

        # Piscar se estiver invencível
        if self.invencivel:
            if math.sin(pygame.time.get_ticks()) > 0:
                flash = frame_base.copy()
                flash.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = flash
            else: self.image = frame_base
        else: self.image = frame_base

    def receber_dano(self):
        if not self.invencivel:
            self.vida_atual -= DANO_INIMIGO
            self.invencivel = True
            self.tempo_invencivel = pygame.time.get_ticks()
            return True
        return False

    def checar_invencibilidade(self):
        if self.invencivel:
            if pygame.time.get_ticks() - self.tempo_invencivel > TEMPO_INVENCIVEL:
                self.invencivel = False
                
    def ganhar_xp(self, quantidade):
        # Soma XP e verifica se upou
        self.xp_atual += quantidade
        if self.xp_atual >= self.xp_necessario:
            self.xp_atual -= self.xp_necessario
            self.xp_necessario = int(self.xp_necessario * 1.5) # Aumenta a dificuldade
            self.nivel += 1
            return True # Avisa o main.py que teve Level UP
        return False

    def update(self):
        self.Input(); self.Mover(); self.Animar(); self.checar_invencibilidade()

class Projetil(pygame.sprite.Sprite):
    def __init__(self, pos_inicial, direcao, grupos):
        super().__init__(grupos)
        self.image = pygame.Surface((10, 10)) 
        self.image.fill(COR_AZUL) 
        self.rect = self.image.get_rect(center=pos_inicial)
        self.pos_real = pygame.math.Vector2(self.rect.center)
        self.direcao = direcao.normalize()
        self.velocidade = 12 
        self.tempo_vida = 1000 
        self.nascimento = pygame.time.get_ticks()

    def update(self):
        self.pos_real += self.direcao * self.velocidade
        self.rect.center = round(self.pos_real.x), round(self.pos_real.y)
        if pygame.time.get_ticks() - self.nascimento > self.tempo_vida: self.kill()

class TextoDano(pygame.sprite.Sprite):
    def __init__(self, valor, pos, grupos, cor):
        super().__init__(grupos)
        font = pygame.font.SysFont("arial", 30, bold=True)
        self.image = font.render(str(valor), True, cor)
        self.rect = self.image.get_rect(center=pos)
        self.pos_real = pygame.math.Vector2(self.rect.center)
        self.velocidade = -2 
        self.timer = 0
        self.tempo_vida = 40 

    def update(self):
        self.pos_real.y += self.velocidade
        self.rect.center = round(self.pos_real.x), round(self.pos_real.y)
        self.timer += 1
        if self.timer >= self.tempo_vida: self.kill()