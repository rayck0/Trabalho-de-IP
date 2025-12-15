import pygame
import math

# Não precisamos de os/sys/math aqui, pois não estamos mais usando recurso_caminho
# math será necessário se você quiser a lógica de flutuação, 
# mas não está sendo usada no update() atual.

class Coletaveis(pygame.sprite.Sprite):
    def __init__(self, tipo, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []
        tamanho_item = (35, 35)
        
        # --- Carregamento de quadros para XP e Moeda (agora corrigido) ---
        if tipo == 'xp':
            for ii in range(2,5):
                # CORREÇÃO: Carrega a imagem diretamente com o caminho relativo (usando '/')
                caminho_img = f'recursos/xp_{ii}-removebg-preview.png' 
                img = pygame.image.load(caminho_img).convert_alpha()
                self.sprites.append(pygame.transform.scale(img, tamanho_item))
                
        elif tipo =='moeda':
            for ii in range(1,5):
                # CORREÇÃO: Carregamento direto
                caminho_img = f'recursos/moeda_{ii}-removebg-preview.png'
                img = pygame.image.load(caminho_img).convert_alpha()
                self.sprites.append(pygame.transform.scale(img, tamanho_item))
                
        elif tipo == 'vida':
            # CORREÇÃO: Carregamento direto
            caminho_img = 'recursos/coracao-removebg-preview.png'
            img = pygame.image.load(caminho_img).convert_alpha()
            self.sprites.append(pygame.transform.scale(img, tamanho_item))
        
        # Variáveis de Animação
        self.indice_atual = 0.0 # Usamos float para controle de velocidade
        self.velocidade_animacao = 0.2
        self.image = self.sprites[0] if self.sprites else pygame.Surface(tamanho_item)
        
        self.rect = self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.tipo = tipo
        
        # Variáveis de Flutuação
        self.posicao_y_inicial = y         
        self.flutuacao_amplitude = 5  
        self.flutuacao_velocidade = 0.05   
        self.angulo_atual = 0
    
    def update(self):
        # Lógica de Animação de Quadros: só troca se houver mais de um quadro
        if len(self.sprites) > 1:
            self.indice_atual += self.velocidade_animacao
            
            # Se o índice passar do número de quadros, ele volta para o início (loop)
            if self.indice_atual >= len(self.sprites):
                self.indice_atual = 0.0
                
            # Atualiza a imagem com o quadro atual (convertendo para inteiro)
            self.image = self.sprites[int(self.indice_atual)]
        
        # Lógica de Flutuação (esta parte também está OK)
        self.angulo_atual += self.flutuacao_velocidade
        offset_y = math.sin(self.angulo_atual) * self.flutuacao_amplitude
        self.rect.y = self.posicao_y_inicial + offset_y
        
        center = self.rect.center
        # CORREÇÃO 3: Ajustando o rect após a troca de imagem e flutuação
        self.rect = self.image.get_rect(center=center)