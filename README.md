# 🐶 Byte Survivors - Projeto Final de IP

![Status do Projeto](https://img.shields.io/badge/Status-Concluído-brightgreen)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/Lib-Pygame-yellow)

> Um jogo estilo *Roguelike/Bullet Hell* inspirado em Vampire Survivors

## 📖 Sobre o Jogo
**Byte Survivors** coloca você no controle de **Byte**, um cachorro corajoso em um mundo cibernético infinito. O objetivo é sobreviver o máximo de tempo possível contra hordas de robôs, coletar recursos para evoluir suas habilidades e alcançar a pontuação máxima.
O jogo utiliza mecânicas de **geração procedural de inimigos**, **sistema de level-up com cartas** e **mapa infinito** via câmera.

## 🎮 Funcionalidades Principais
* **Sistema de Combate Automático:** O jogador foca na movimentação enquanto o personagem mira e atira automaticamente no inimigo mais próximo.
* **Inimigos Variados:** 5 tipos de inimigos com comportamentos, velocidades e vidas diferentes (incluindo Boss).
* **Sistema de Level Up:** Ao coletar XP, o jogo pausa e oferece 3 cartas de melhoria aleatórias (RNG).
* **Mapa Infinito:** Sistema de câmera que segue o jogador, criando a ilusão de um mundo sem bordas.
* **Audio System:** Músicas de fundo diferentes para Menu/Jogo e efeitos sonoros para todas as interações.
* **Estados de Jogo:** Menu Inicial, Gameplay, Pause (com configurações) e Game Over.

## 🛠️ Tecnologias e Conceitos Aplicados
Este projeto foi fundamental para aplicar os conceitos de **Programação Orientada a Objetos (POO)**.

| Conceito | Aplicação no Projeto |
|----------|----------------------|
| **Herança** | A classe `InimigoPadrao` define a lógica base, e `RoboVoador`, `RoboDragao`, etc., herdam e modificam seus atributos. |
| **Polimorfismo** | Todos os inimigos têm o método `update()`, mas comportam-se de maneira diferente (velocidade, sprites). |
| **Encapsulamento** | Separação do código em módulos (`main.py`, `sprites.py`, etc.) para facilitar a manutenção. |
| **Vetores** | Uso de `pygame.math.Vector2` para cálculos de distância, direção de tiro e movimentação fluida. |

## 📂 Organização do Código

O projeto foi dividido em módulos para manter o código limpo:

* **`main.py`**: O "Gerente" do jogo. Controla o Loop Principal, a Máquina de Estados (MENU, JOGANDO, PAUSE), o gerenciamento de eventos e o desenho da UI.
* **`sprites.py`**: Contém a classe `Jogador` (física, inputs, animação), `GrupoCamera` (lógica de renderização do mapa) e `Projetil`.
* **`inimigos.py`**: Gerencia a IA dos inimigos. Implementa a lógica de "flip" (inverter sprite dependendo da direção) e o sistema de dano (piscar branco).
* **`coletaveis.py`**: Controla os itens (XP, Vida, Moedas). Usa lógica para recortar spritesheets automaticamente.
* **`config.py`**: Arquivo de configuração global. Guarda constantes como resolução, cores, FPS e balanceamento do jogo.

## 🚀 Como Rodar o Jogo

### Pré-requisitos
* Python 3.x instalado.
* Biblioteca Pygame instalada.

### Passo a Passo
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git)
    ```
2.  **Instale a dependência:**
    ```bash
    pip install pygame
    ```
3.  **Certifique-se da estrutura de pastas:**
    O diretório deve conter as pastas `Sprites/` e `Sons/` com os respectivos arquivos.
4.  **Execute o jogo:**
    ```bash
    python main.py
    ```

## 🕹️ Controles

| Tecla | Ação |
|-------|------|
| **W, A, S, D** ou **Setas** | Movimentar o Personagem |
| **ESC** | Pausar o Jogo / Voltar ao Jogo |
| **Mouse (Clique)** | Selecionar Cartas de Upgrade / Botões do Menu |
| **R** | Reiniciar (apenas na tela de Game Over) |

## 🧠 Desafios e Aprendizados
Durante o desenvolvimento, enfrentamos desafios como:
1.  **Lógica da Câmera:** Fazer o cenário se mover na direção oposta ao jogador para criar o efeito de câmera fixa no centro.
2.  **Animação de Sprites:** Sincronizar a taxa de quadros da animação e resolver o problema dos inimigos que andavam "de costas" (resolvido com `pygame.transform.flip`).
3.  **Gerenciamento de Estados:** Criar um fluxo robusto para que o jogo não continuasse rodando "por trás" do menu de Pause ou Level Up.

*Projeto desenvolvido para a disciplina de Introdução à Programação (CIn - UFPE).*
