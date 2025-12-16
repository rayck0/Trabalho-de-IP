import pygame
import os

#diretorios
diretorio_principal = os.path.dirname(__file__)
diretorio_imagens = os.path.join(diretorio_principal, 'Sprites')

#robo voador-----------------------------------------------------------------------------------------------------
inimigo_RoboVoador = pygame.image.load(os.path.join(diretorio_imagens, 'enemy_roboVoador.png')).convert_alpha()
class Robo_voador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []
        for x in range(8): #8 frames (88x64)
            img = inimigo_RoboVoador.subsurface((88*x, 64), (88,64))
            #caso precise aumentar o tamanho --------------
            #img = pygame.transform.scale(img, (88*, 64*))
            self.sprites.append(img)
        self.index = 0
        self.image = self.sprites[self.index]
    def update(self):
        if self.index > 7:
            self.index = 0
        self.index += 0.25
        self.image = self.sprites[int(self.index)]

#robo dragão----------------------------------------------------------------------------------------------------
inimigo_RoboDragao = pygame.image.load(os.path.join(diretorio_imagens, 'enemy_roboDragao.png')).convert_alpha()
class Robo_dragao(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []
        for x in range(6): #6 frames (256x256)
            img = inimigo_RoboVoador.subsurface((256*x, 256), (256,256))
            #caso precise aumentar o tamanho --------------
            #img = pygame.transform.scale(img, (256*, 256*))
            self.sprites.append(img)
        self.index = 0
        self.image = self.sprites[self.index]
    def update(self):
        if self.index > 5:
            self.index = 0
        self.index += 0.20
        self.image = self.sprites[int(self.index)]
        
#robo cobra----------------------------------------------------------------------------------------------------
inimigo_RoboCobra = pygame.image.load(os.path.join(diretorio_imagens, 'enemy_roboCobra.png')).convert_alpha()
class Robo_cobra(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []
        for x in range(5): #5 frames (64x64)
            img = inimigo_RoboVoador.subsurface((64*x, 64), (64,64))
            #caso precise aumentar o tamanho --------------
            #img = pygame.transform.scale(img, (64*, 64*))
            self.sprites.append(img)
        self.index = 0
        self.image = self.sprites[self.index]
    def update(self):
        if self.index > 4:
            self.index = 0
        self.index += 0.20
        self.image = self.sprites[int(self.index)]

#robo bola-----------------------------------------------------------------------------------------------------
inimigo_RoboBola = pygame.image.load(os.path.join(diretorio_imagens, 'enemy_roboBola.png')).convert_alpha()
class Robo_bola(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []
        for x in range(4): #4 frames (64x64)
            img = inimigo_RoboVoador.subsurface((64*x, 64), (64,64))
            #caso precise aumentar o tamanho --------------
            #img = pygame.transform.scale(img, (64*, 64*))
            self.sprites.append(img)
        self.index = 0
        self.image = self.sprites[self.index]
    def update(self):
        if self.index > 3:
            self.index = 0
        self.index += 0.15
        self.image = self.sprites[int(self.index)]

#robo Zangão----------------------------------------------------------------------------------------------------
inimigo_RoboZangao = pygame.image.load(os.path.join(diretorio_imagens, 'enemy_roboZangao.png')).convert_alpha()
class Robo_zangao(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []
        for x in range(4): #4 frames (64x64)
            img = inimigo_RoboVoador.subsurface((64*x, 64), (64,64))
            #caso precise aumentar o tamanho --------------
            #img = pygame.transform.scale(img, (64*, 64*))
            self.sprites.append(img)
        self.index = 0
        self.image = self.sprites[self.index]
    def update(self):
        if self.index > 3:
            self.index = 0
        self.index += 0.15
        self.image = self.sprites[int(self.index)]