import pygame
import sys
import os
import random
from config import *

# Inicialização
pygame.init()
pygame.mixer.init()
pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Vampire Survivors - Projeto Final")

# Fontes
try:
    FONTE_UI = pygame.font.SysFont("arial", 18, bold=True)
    FONTE_TITULO = pygame.font.SysFont("arial", 30, bold=True)
    FONTE_GAMEOVER = pygame.font.SysFont("arial", 60, bold=True) # Fonte Gigante
    FONTE_CARTA = pygame.font.SysFont("arial", 20)
    FONTE_BOTAO = pygame.font.SysFont("arial", 25, bold=True)
except:
    FONTE_UI = pygame.font.Font(None, 24)
    FONTE_TITULO = pygame.font.Font(None, 40)
    FONTE_GAMEOVER = pygame.font.Font(None, 80)
    FONTE_CARTA = pygame.font.Font(None, 24)
    FONTE_BOTAO = pygame.font.Font(None, 30)

from sprites import *
from inimigos import *
from coletaveis import *

class Jogo:
    def __init__(self):
        self.Tela = pygame.display.get_surface()
        self.Relogio = pygame.time.Clock()
        
        # ESTADOS E CONFIGURAÇÕES
        self.estado = "JOGANDO" 
        self.opcoes_upgrade = [] 
        self.config_som = True     
        self.config_dano = True    
        
        # Grupos
        self.CameraGroup = GrupoCamera()
        self.GrupoInimigos = pygame.sprite.Group() 
        self.GrupoTiros = pygame.sprite.Group()
        self.GrupoItens = pygame.sprite.Group()

        # Timers
        self.evento_spawn = pygame.USEREVENT + 1
        pygame.time.set_timer(self.evento_spawn, 1000)
        self.ultimo_tiro = 0

        # Sons
        self.sons = {}
        self.carregar_sons_do_usuario()
        
        # Setup Inicial
        self.setup_do_mundo()
        self.tocar_musica()

    def carregar_sons_do_usuario(self):
        diretorio_sons = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sons')
        def carregar(nome, tipo="efeito"):
            caminho = os.path.join(diretorio_sons, nome)
            try:
                if tipo == "musica":
                    pygame.mixer.music.load(caminho)
                    return pygame.mixer.music
                else:
                    som = pygame.mixer.Sound(caminho)
                    som.set_volume(0.4)
                    return som
            except: return None

        self.sons["tiro"] = carregar("laserShoot.wav")
        self.sons["explosao"] = carregar("explosion.wav")
        self.sons["levelup"] = carregar("powerUp.wav")
        self.sons["moeda"] = carregar("pickupCoin.wav")
        self.sons["musica"] = carregar("byte-blast-8-bit-arcade-music-background-music-for-video-208780.mp3", tipo="musica")

    def tocar_som(self, nome):
        if self.config_som and self.sons.get(nome):
            self.sons[nome].play()

    def tocar_musica(self):
        if self.config_som and self.sons.get("musica"):
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

    def atualizar_volume_musica(self):
        if self.sons.get("musica"):
            if self.config_som:
                pygame.mixer.music.set_volume(0.3)
                if not pygame.mixer.music.get_busy(): pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.set_volume(0)

    def setup_do_mundo(self):
        self.Jogador = Jogador((1500, 1500), [self.CameraGroup])

    def reiniciar_jogo(self):
        # Zera tudo para começar de novo
        # Limpa todos os grupos (menos a câmera, que a gente reutiliza)
        self.GrupoInimigos.empty()
        self.GrupoTiros.empty()
        self.GrupoItens.empty()
        self.CameraGroup.empty() # Limpa sprites visuais antigos
        
        # Recria o mundo
        self.setup_do_mundo()
        self.estado = "JOGANDO"
        self.tocar_musica() # Volta a música

    def spawnar_inimigo(self):
        angulo = random.uniform(0, 360)
        distancia = random.randint(700, 1000)
        offset = pygame.math.Vector2(); offset.from_polar((distancia, angulo))
        pos_final = self.Jogador.PosicaoReal + offset
        
        grupos = [self.CameraGroup, self.GrupoInimigos]
        sorteio = random.randint(1, 100)
        if sorteio <= 40: RoboVoador(pos_final, grupos)
        elif sorteio <= 70: RoboBola(pos_final, grupos)
        elif sorteio <= 90: RoboCobra(pos_final, grupos)
        elif sorteio <= 98: RoboZangao(pos_final, grupos)
        else: RoboDragao(pos_final, grupos)

    def logica_tiro_automatico(self):
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_tiro > self.Jogador.cooldown_tiro:
            inimigo_mais_perto = None
            menor_distancia = 1000
            for inimigo in self.GrupoInimigos:
                dist = (inimigo.pos_real - self.Jogador.PosicaoReal).magnitude()
                if dist < menor_distancia:
                    menor_distancia = dist; inimigo_mais_perto = inimigo
            
            if inimigo_mais_perto:
                self.ultimo_tiro = agora
                direcao = inimigo_mais_perto.pos_real - self.Jogador.PosicaoReal
                Projetil(self.Jogador.rect.center, direcao, [self.CameraGroup, self.GrupoTiros])
                self.tocar_som("tiro")

    def gerar_opcoes_upgrade(self):
        catalogo = [
            {"nome": "Forca Bruta", "desc": "+10 Dano", "tipo": "dano", "valor": 10, "cor": (200, 50, 50)},
            {"nome": "Metralhadora", "desc": "-10% Tempo Tiro", "tipo": "cooldown", "valor": 0.9, "cor": (50, 200, 200)},
            {"nome": "Pe de Vento", "desc": "+1 Velocidade", "tipo": "speed", "valor": 1, "cor": (50, 200, 50)},
            {"nome": "Curativo", "desc": "Cura 50 Vida", "tipo": "cura", "valor": 50, "cor": (200, 100, 200)},
            {"nome": "Tanque", "desc": "+20 Vida Max", "tipo": "vida_max", "valor": 20, "cor": (100, 100, 200)}
        ]
        self.opcoes_upgrade = random.sample(catalogo, 3)

    def aplicar_upgrade(self, opcao):
        if opcao["tipo"] == "dano": self.Jogador.dano_base += opcao["valor"]
        elif opcao["tipo"] == "cooldown": self.Jogador.cooldown_tiro *= opcao["valor"] 
        elif opcao["tipo"] == "speed": self.Jogador.Velocidade += opcao["valor"]
        elif opcao["tipo"] == "cura": self.Jogador.vida_atual = min(self.Jogador.vida_atual + opcao["valor"], self.Jogador.vida_maxima)
        elif opcao["tipo"] == "vida_max":
            self.Jogador.vida_maxima += opcao["valor"]
            self.Jogador.vida_atual += opcao["valor"]
        self.estado = "JOGANDO"

    def desenhar_ui(self):
        x = 20; y = ALTURA_TELA - 40
        bg_rect = pygame.Rect(x, y, BARRA_VIDA_LARGURA, BARRA_VIDA_ALTURA)
        pygame.draw.rect(self.Tela, COR_UI_FUNDO, bg_rect)
        razao_vida = max(0, self.Jogador.vida_atual / self.Jogador.vida_maxima)
        vida_rect = bg_rect.copy(); vida_rect.width = bg_rect.width * razao_vida
        pygame.draw.rect(self.Tela, COR_VIDA, vida_rect)
        pygame.draw.rect(self.Tela, COR_UI_BORDA, bg_rect, 2)
        
        texto_vida = f"{int(self.Jogador.vida_atual)}/{self.Jogador.vida_maxima}"
        surf_vida = FONTE_UI.render(texto_vida, True, COR_BRANCA)
        self.Tela.blit(surf_vida, (x + 10, y + 2))
        
        y_xp = y - 15
        bg_xp = pygame.Rect(x, y_xp, BARRA_VIDA_LARGURA, 10)
        pygame.draw.rect(self.Tela, (30, 30, 30), bg_xp)
        razao_xp = min(1, self.Jogador.xp_atual / self.Jogador.xp_necessario)
        xp_rect = bg_xp.copy(); xp_rect.width = bg_xp.width * razao_xp
        pygame.draw.rect(self.Tela, (50, 100, 255), xp_rect)
        pygame.draw.rect(self.Tela, COR_UI_BORDA, bg_xp, 1)

    def desenhar_menu_levelup(self):
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        overlay.set_alpha(150); overlay.fill((0,0,0))
        self.Tela.blit(overlay, (0,0))
        
        titulo = FONTE_TITULO.render("LEVEL UP! Escolha:", True, (255, 215, 0))
        self.Tela.blit(titulo, (LARGURA_TELA//2 - titulo.get_width()//2, 100))
        
        mouse_pos = pygame.mouse.get_pos()
        clique = pygame.mouse.get_pressed()[0]
        
        largura_carta = 200; altura_carta = 300; espaco = 50
        total_w = 3*largura_carta + 2*espaco
        inicio_x = (LARGURA_TELA - total_w) // 2
        y_carta = 200
        
        for i, opcao in enumerate(self.opcoes_upgrade):
            x_carta = inicio_x + i * (largura_carta + espaco)
            rect_carta = pygame.Rect(x_carta, y_carta, largura_carta, altura_carta)
            
            cor_atual = opcao["cor"]
            if rect_carta.collidepoint(mouse_pos):
                cor_atual = (min(cor_atual[0]+30, 255), min(cor_atual[1]+30, 255), min(cor_atual[2]+30, 255))
                if clique:
                    self.aplicar_upgrade(opcao)
                    return 
            
            pygame.draw.rect(self.Tela, cor_atual, rect_carta, border_radius=15)
            pygame.draw.rect(self.Tela, COR_BRANCA, rect_carta, 3, border_radius=15)
            
            nome = FONTE_TITULO.render(opcao["nome"], True, COR_BRANCA)
            desc = FONTE_CARTA.render(opcao["desc"], True, COR_BRANCA)
            self.Tela.blit(nome, (rect_carta.centerx - nome.get_width()//2, rect_carta.y + 40))
            self.Tela.blit(desc, (rect_carta.centerx - desc.get_width()//2, rect_carta.centery))

    def desenhar_menu_pause(self):
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        overlay.set_alpha(200); overlay.fill((0,0,0))
        self.Tela.blit(overlay, (0,0))

        titulo = FONTE_TITULO.render("JOGO PAUSADO (ESC p/ Voltar)", True, COR_BRANCA)
        self.Tela.blit(titulo, (LARGURA_TELA//2 - titulo.get_width()//2, 150))

        mouse_pos = pygame.mouse.get_pos()
        clique = pygame.mouse.get_pressed()[0]

        largura_btn = 300; altura_btn = 60
        centro_x = LARGURA_TELA // 2 - largura_btn // 2
        
        # BOTÃO SOM
        rect_som = pygame.Rect(centro_x, 300, largura_btn, altura_btn)
        cor_som = (50, 200, 50) if self.config_som else (200, 50, 50)
        texto_som_str = f"Som: {'LIGADO' if self.config_som else 'DESLIGADO'}"
        
        # BOTÃO DANO
        rect_dano = pygame.Rect(centro_x, 400, largura_btn, altura_btn)
        cor_dano = (50, 200, 50) if self.config_dano else (200, 50, 50)
        texto_dano_str = f"Dano Pop-up: {'LIGADO' if self.config_dano else 'DESLIGADO'}"

        pygame.draw.rect(self.Tela, cor_som, rect_som, border_radius=10)
        pygame.draw.rect(self.Tela, COR_BRANCA, rect_som, 2, border_radius=10)
        txt_som = FONTE_BOTAO.render(texto_som_str, True, COR_BRANCA)
        self.Tela.blit(txt_som, (rect_som.centerx - txt_som.get_width()//2, rect_som.centery - txt_som.get_height()//2))

        pygame.draw.rect(self.Tela, cor_dano, rect_dano, border_radius=10)
        pygame.draw.rect(self.Tela, COR_BRANCA, rect_dano, 2, border_radius=10)
        txt_dano = FONTE_BOTAO.render(texto_dano_str, True, COR_BRANCA)
        self.Tela.blit(txt_dano, (rect_dano.centerx - txt_dano.get_width()//2, rect_dano.centery - txt_dano.get_height()//2))

        if clique:
            if rect_som.collidepoint(mouse_pos):
                self.config_som = not self.config_som 
                self.atualizar_volume_musica()
                pygame.time.delay(200) 
            if rect_dano.collidepoint(mouse_pos):
                self.config_dano = not self.config_dano
                pygame.time.delay(200)

    # TELA DE GAME OVER
    def desenhar_game_over(self):
        #  Tela Vermelha Sangue com transparência
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        overlay.set_alpha(220)
        overlay.fill((50, 0, 0)) # Vermelho escuro
        self.Tela.blit(overlay, (0,0))

        # Textos
        txt_gameover = FONTE_GAMEOVER.render("GAME OVER", True, (255, 0, 0))
        txt_reiniciar = FONTE_TITULO.render("Pressione 'R' para Reiniciar", True, COR_BRANCA)
        txt_score = FONTE_BOTAO.render(f"Nível Alcançado: {self.Jogador.nivel}", True, COR_DOURADA)

        # Posicionamento
        self.Tela.blit(txt_gameover, (LARGURA_TELA//2 - txt_gameover.get_width()//2, 200))
        self.Tela.blit(txt_score, (LARGURA_TELA//2 - txt_score.get_width()//2, 350))
        self.Tela.blit(txt_reiniciar, (LARGURA_TELA//2 - txt_reiniciar.get_width()//2, 500))

    def checar_colisoes(self):
        colisoes = pygame.sprite.groupcollide(self.GrupoInimigos, self.GrupoTiros, False, True)
        for inimigo, balas in colisoes.items():
            dano = len(balas) * self.Jogador.dano_base 
            if self.config_dano:
                TextoDano(dano, inimigo.rect.center, [self.CameraGroup], COR_BRANCA)
            
            if inimigo.receber_dano(dano):
                self.tocar_som("explosao")
                tipo = random.choice(['xp', 'xp', 'xp', 'ouro', 'vida'])
                Coletavel(tipo, inimigo.rect.center, [self.CameraGroup, self.GrupoItens])

        itens = pygame.sprite.spritecollide(self.Jogador, self.GrupoItens, True)
        for item in itens:
            self.tocar_som("moeda")
            if item.tipo == 'vida':
                self.Jogador.vida_atual = min(self.Jogador.vida_atual + 20, self.Jogador.vida_maxima)
                if self.config_dano:
                    TextoDano("+20", self.Jogador.rect.topright, [self.CameraGroup], COR_VERDE_CLARO)
            elif item.tipo == 'xp':
                ganhou_xp_valor = 20 
                if self.Jogador.ganhar_xp(ganhou_xp_valor):
                    self.tocar_som("levelup")
                    self.estado = "LEVEL_UP"
                    self.gerar_opcoes_upgrade()

        if pygame.sprite.spritecollide(self.Jogador, self.GrupoInimigos, False, pygame.sprite.collide_rect_ratio(0.8)):
            # MORTE DO JOGADOR
            if self.Jogador.receber_dano():
                if self.config_dano:
                    TextoDano(f"-{DANO_INIMIGO}", self.Jogador.rect.center, [self.CameraGroup], COR_VERMELHA)
            
            # sobrou nada p o betinha
            if self.Jogador.vida_atual <= 0:
                self.estado = "GAME_OVER"
                pygame.mixer.music.stop() # Para a música
                self.tocar_som("explosao") # Som dramático final

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                # ESC para Pause
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.estado == "JOGANDO": self.estado = "PAUSE"
                        elif self.estado == "PAUSE": self.estado = "JOGANDO"
                    
                    # R para Reiniciar so da no game over
                    if event.key == pygame.K_r and self.estado == "GAME_OVER":
                        self.reiniciar_jogo()

                if self.estado == "JOGANDO" and event.type == self.evento_spawn:
                    self.spawnar_inimigo()

            self.Tela.fill(COR_PRETA)
            
            if self.estado == "JOGANDO":
                self.CameraGroup.update()
                self.logica_tiro_automatico()
                for inimigo in self.GrupoInimigos:
                    inimigo.cacar_jogador(self.Jogador)
                self.checar_colisoes()
                self.CameraGroup.custom_draw(self.Jogador)
                self.desenhar_ui()
                
            elif self.estado == "LEVEL_UP":
                self.CameraGroup.custom_draw(self.Jogador)
                self.desenhar_ui()
                self.desenhar_menu_levelup()
            
            elif self.estado == "PAUSE":
                self.CameraGroup.custom_draw(self.Jogador)
                self.desenhar_ui()
                self.desenhar_menu_pause()

            # DESENHO DO GAME OVER
            elif self.estado == "GAME_OVER":
                self.CameraGroup.custom_draw(self.Jogador) # Desenha o jogo morto ao fundo
                self.desenhar_ui()
                self.desenhar_game_over()

            pygame.display.update()
            self.Relogio.tick(FPS)

if __name__ == '__main__':
    game = Jogo()
    game.run()
