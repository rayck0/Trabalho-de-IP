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
        self.estado = "MENU" 
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
        
        # Tela menu
        img_original = pygame.image.load('Sprites/Menu.png')
        self.imagem_capa = pygame.transform.scale(img_original, (LARGURA_TELA, ALTURA_TELA))
        
        # --- CARREGAMENTO DAS CARTAS ---
        self.imagens_cards = {}
        try:
            dim = (200, 300)
            self.imagens_cards["dano"]     = pygame.transform.scale(pygame.image.load("Sprites/card_dano.png"), dim)
            self.imagens_cards["cooldown"] = pygame.transform.scale(pygame.image.load("Sprites/card_cooldown.png"), dim)
            self.imagens_cards["speed"]    = pygame.transform.scale(pygame.image.load("Sprites/card_speed.png"), dim)
            self.imagens_cards["cura"]     = pygame.transform.scale(pygame.image.load("Sprites/card_cura.png"), dim)
            self.imagens_cards["vida_max"] = pygame.transform.scale(pygame.image.load("Sprites/card_tank.png"), dim)
        except Exception as e:
            print(f"AVISO: Alguma carta não foi encontrada! {e}")
        # -------------------------------------

        # Setup Inicial
        self.setup_do_mundo()
        
        # Inicia a música do menu
        self.tocar_musica_menu()

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
        self.sons["musica-menu"] = carregar("Menu-musica.mp3", tipo="musica")
        self.sons["musica-principal"] = carregar('Neon Circuitry.mp3', tipo='musica')

    def tocar_som(self, nome):
        if self.config_som and self.sons.get(nome):
            self.sons[nome].play()

    def tocar_musica_menu(self):
        if self.config_som and self.sons.get("musica-menu"):
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
    
    def tocar_musica_principal(self):
        if self.config_som and self.sons.get("musica-principal"):
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

    def atualizar_volume_musica(self):
        # Verifica se o som está ligado ou desligado
        if self.config_som:
            pygame.mixer.music.set_volume(0.3)
            # Se a música estava pausada, despausa
            if not pygame.mixer.music.get_busy():
                # Tenta tocar a música apropriada para o estado atual
                if self.estado == "MENU":
                    self.tocar_musica_menu()
                else:
                    self.tocar_musica_principal()
        else:
            # Se desligou o som, zera o volume
            pygame.mixer.music.set_volume(0)

    def setup_do_mundo(self):
        self.Jogador = Jogador((1500, 1500), [self.CameraGroup])
        # INICIA AS MOEDAS (CORREÇÃO DO ERRO)
        self.Jogador.moedas = 0

    def reiniciar_jogo(self):
        # Zera tudo para começar de novo
        self.GrupoInimigos.empty()
        self.GrupoTiros.empty()
        self.GrupoItens.empty()
        self.CameraGroup.empty() # Limpa sprites visuais antigos
        
        # Recria o mundo
        self.setup_do_mundo()
        self.estado = "JOGANDO"
        self.tocar_musica_principal() # Volta a música

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
        
        # --- BARRA DE VIDA ---
        bg_rect = pygame.Rect(x, y, BARRA_VIDA_LARGURA, BARRA_VIDA_ALTURA)
        pygame.draw.rect(self.Tela, COR_UI_FUNDO, bg_rect)
        razao_vida = max(0, self.Jogador.vida_atual / self.Jogador.vida_maxima)
        vida_rect = bg_rect.copy(); vida_rect.width = bg_rect.width * razao_vida
        pygame.draw.rect(self.Tela, COR_VIDA, vida_rect)
        pygame.draw.rect(self.Tela, COR_UI_BORDA, bg_rect, 2)
        
        # Texto Vida
        texto_vida = f"{int(self.Jogador.vida_atual)}/{self.Jogador.vida_maxima}"
        surf_vida = FONTE_UI.render(texto_vida, True, COR_BRANCA)
        self.Tela.blit(surf_vida, (x + 10, y + 2))
        
        # --- BARRA DE XP ---
        y_xp = y - 20 # Subi um pouquinho
        bg_xp = pygame.Rect(x, y_xp, BARRA_VIDA_LARGURA, 15) # Altura 15
        pygame.draw.rect(self.Tela, (30, 30, 30), bg_xp)
        razao_xp = min(1, self.Jogador.xp_atual / self.Jogador.xp_necessario)
        xp_rect = bg_xp.copy(); xp_rect.width = bg_xp.width * razao_xp
        pygame.draw.rect(self.Tela, (50, 100, 255), xp_rect)
        pygame.draw.rect(self.Tela, COR_UI_BORDA, bg_xp, 1)

        # Texto numérico do XP (NOVO)
        texto_xp = f"{int(self.Jogador.xp_atual)}/{self.Jogador.xp_necessario}"
        try:
            fonte_xp = pygame.font.SysFont("arial", 14, bold=True)
        except:
            fonte_xp = pygame.font.Font(None, 18)
        surf_xp = fonte_xp.render(texto_xp, True, COR_BRANCA)
        self.Tela.blit(surf_xp, (bg_xp.centerx - surf_xp.get_width()//2, bg_xp.y))

        # --- CONTADOR DE MOEDAS (NOVO) ---
        COR_OURO = (255, 215, 0) 
        texto_moedas = f"Moedas: {self.Jogador.moedas}"
        surf_moedas = FONTE_UI.render(texto_moedas, True, COR_OURO)
        
        pos_x_moeda = x + BARRA_VIDA_LARGURA + 20
        pos_y_moeda = y + 5
        self.Tela.blit(surf_moedas, (pos_x_moeda, pos_y_moeda))

    def desenhar_menu_levelup(self):
        # 1. Fundo escuro
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        overlay.set_alpha(150); overlay.fill((0,0,0))
        self.Tela.blit(overlay, (0,0))
        
        # 2. Título
        titulo = FONTE_TITULO.render("LEVEL UP! Escolha:", True, (255, 215, 0))
        self.Tela.blit(titulo, (LARGURA_TELA//2 - titulo.get_width()//2, 80))
        
        mouse_pos = pygame.mouse.get_pos()
        clique = pygame.mouse.get_pressed()[0]
        
        # 3. Layout
        largura_carta = 200 
        altura_carta = 300
        espaco = 50
        
        total_w = 3 * largura_carta + 2 * espaco
        inicio_x = (LARGURA_TELA - total_w) // 2
        y_carta = 180
        
        # 4. Loop
        for i, opcao in enumerate(self.opcoes_upgrade):
            tipo = opcao["tipo"]
            imagem_carta = self.imagens_cards.get(tipo)
            
            x = inicio_x + i * (largura_carta + espaco)
            rect = pygame.Rect(x, y_carta, largura_carta, altura_carta)
            
            # Interação Mouse
            if rect.collidepoint(mouse_pos):
                largura_zoom = largura_carta + 20
                altura_zoom = altura_carta + 30
                
                diff_x = (largura_zoom - largura_carta) // 2
                diff_y = (altura_zoom - altura_carta) // 2
                
                if imagem_carta:
                    img_zoom = pygame.transform.scale(imagem_carta, (largura_zoom, altura_zoom))
                    self.Tela.blit(img_zoom, (x - diff_x, y_carta - diff_y))
                else:
                    pygame.draw.rect(self.Tela, opcao["cor"], (x - diff_x, y_carta - diff_y, largura_zoom, altura_zoom), border_radius=15)

                pygame.draw.rect(self.Tela, (255, 255, 255), (x - diff_x, y_carta - diff_y, largura_zoom, altura_zoom), 4, border_radius=15)
                
                if clique:
                    self.aplicar_upgrade(opcao)
                    return 
            
            else:
                if imagem_carta:
                    self.Tela.blit(imagem_carta, (x, y_carta))
                else:
                    pygame.draw.rect(self.Tela, opcao["cor"], rect, border_radius=15)
                    nome = FONTE_TITULO.render(opcao["nome"], True, COR_BRANCA)
                    self.Tela.blit(nome, (rect.centerx - nome.get_width()//2, rect.y + 40))

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
    
    def desenhar_menu_inicial(self):
        if self.imagem_capa:
            self.Tela.blit(self.imagem_capa, (0, 0))
        
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        overlay.set_alpha(80) 
        overlay.fill((0, 0, 0))
        self.Tela.blit(overlay, (0, 0))

        def desenhar_botao_pixelado(texto, y_pos, funcao_ao_clicar):
            mouse_pos = pygame.mouse.get_pos()
            clique = pygame.mouse.get_pressed()[0]
            
            rect = pygame.Rect(LARGURA_TELA//2 - 100, y_pos, 200, 60)
            p = 6 
            
            pontos = [
                (rect.left, rect.top + p), (rect.left + p, rect.top),
                (rect.right - p, rect.top), (rect.right, rect.top + p),
                (rect.right, rect.bottom - p), (rect.right - p, rect.bottom),
                (rect.left + p, rect.bottom), (rect.left, rect.bottom - p)
            ]

            cor_borda = (255, 0, 0)
            cor_texto = (255, 0, 0)
            preenchimento = None

            if rect.collidepoint(mouse_pos):
                preenchimento = cor_borda
                cor_texto = (255, 255, 255)
                pontos_sombra = [(x+4, y+4) for x, y in pontos]
                pygame.draw.polygon(self.Tela, (50, 0, 0), pontos_sombra)
                if clique:
                    funcao_ao_clicar()
            
            if preenchimento:
                pygame.draw.polygon(self.Tela, preenchimento, pontos)
            pygame.draw.polygon(self.Tela, cor_borda, pontos, 4)
            
            surf_texto = FONTE_BOTAO.render(texto, True, cor_texto)
            self.Tela.blit(surf_texto, (rect.centerx - surf_texto.get_width()//2, rect.centery - surf_texto.get_height()//2))

        def acao_iniciar():
            self.estado = "JOGANDO"
            self.reiniciar_jogo()

        def acao_sair():
            pygame.quit()
            sys.exit()

        desenhar_botao_pixelado("INICIAR", 480, acao_iniciar)
        desenhar_botao_pixelado("SAIR", 560, acao_sair)

        instrucao_sombra = FONTE_UI.render("Use WASD para mover", True, (0,0,0))
        self.Tela.blit(instrucao_sombra, (LARGURA_TELA//2 - instrucao_sombra.get_width()//2 + 2, ALTURA_TELA - 90))
        
        instrucao = FONTE_UI.render("Use WASD para mover", True, (255, 0, 0))
        self.Tela.blit(instrucao, (LARGURA_TELA//2 - instrucao.get_width()//2, ALTURA_TELA - 90))

    def desenhar_game_over(self):
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        overlay.set_alpha(220)
        overlay.fill((50, 0, 0)) 
        self.Tela.blit(overlay, (0,0))

        txt_gameover = FONTE_GAMEOVER.render("GAME OVER", True, (255, 0, 0))
        txt_reiniciar = FONTE_TITULO.render("Pressione 'R' para Reiniciar", True, COR_BRANCA)
        txt_score = FONTE_BOTAO.render(f"Nível Alcançado: {self.Jogador.nivel}", True, COR_DOURADA)

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
            
            elif item.tipo == 'ouro':
                self.Jogador.moedas += 1
                if self.config_dano:
                    TextoDano("+1 $", self.Jogador.rect.topright, [self.CameraGroup], (255, 215, 0))

        if pygame.sprite.spritecollide(self.Jogador, self.GrupoInimigos, False, pygame.sprite.collide_rect_ratio(0.8)):
            if self.Jogador.receber_dano():
                if self.config_dano:
                    TextoDano(f"-{DANO_INIMIGO}", self.Jogador.rect.center, [self.CameraGroup], COR_VERMELHA)
            
            if self.Jogador.vida_atual <= 0:
                self.estado = "GAME_OVER"
                pygame.mixer.music.stop()
                self.tocar_som("explosao")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.estado == "JOGANDO": self.estado = "PAUSE"
                        elif self.estado == "PAUSE": self.estado = "JOGANDO"
                    
                    if event.key == pygame.K_r and self.estado == "GAME_OVER":
                        self.reiniciar_jogo()

                if self.estado == "JOGANDO" and event.type == self.evento_spawn:
                    self.spawnar_inimigo()

            self.Tela.fill(COR_PRETA)
            
            if self.estado == "MENU":
                self.desenhar_menu_inicial()
                
            elif self.estado == "JOGANDO":
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

            elif self.estado == "GAME_OVER":
                self.CameraGroup.custom_draw(self.Jogador)
                self.desenhar_ui()
                self.desenhar_game_over()

            pygame.display.update()
            self.Relogio.tick(FPS)

if __name__ == '__main__':
    game = Jogo()
    game.run()
