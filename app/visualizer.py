import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import networkx as nx
import numpy as np

def grafico_evolucao(historico_melhor, historico_media, filename='evolucao_ag.png'):
    plt.figure(figsize=(10, 5))
    plt.plot(historico_melhor, label='Melhor Fitness', color='blue', linewidth=2)
    plt.plot(historico_media, label='Media da População', color='orange', linestyle='--')

    plt.title('Progresso do Algoritmo Genético - Estabilidade do Navio')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(filename)
    plt.show()

def grafico_estabilidade(historico_estabilidade, filename='estabilidade_naval_final.png'):
    # Extrai os dados individuais da lista de dicionários
    list_gm = [d["GM"] for d in historico_estabilidade]
    list_graus = [d["List"] for d in historico_estabilidade]
    list_trim = [d["Trim"] for d in historico_estabilidade]
    passos = range(1, len(historico_estabilidade) + 1)

    # Cria uma figura com 3 subplots (3 linhas, 1 coluna)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

    # 1. Gráfico de GM (Altura Metacêntrica) - Estabilidade Vertical
    ax1.plot(passos, list_gm, color='blue', marker='s', label='GM (Altura Metacêntrica)')
    ax1.axhline(y=0.5, color='red', linestyle='--', label='Limite Mínimo Seguro (0.5m)')
    ax1.set_ylabel('GM (m)')
    ax1.set_title('Estabilidade Naval durante o Descarregamento')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    # 2. Gráfico de Banda (List) - Inclinação Lateral (Eixo Y)
    ax2.plot(passos, list_graus, color='green', marker='o', label='Banda (List)')
    ax2.axhspan(-5, 5, color='green', alpha=0.1, label='Zona Segura (±5°)')
    ax2.set_ylabel('Inclinação (°)')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    # 3. Gráfico de Trim - Inclinação Longitudinal (Eixo X)
    ax3.plot(passos, list_trim, color='purple', marker='^', label='Trim (Diferença Proa/Popa)')
    ax3.set_xlabel('Ordem de Retirada (Container nº)')
    ax3.set_ylabel('Diferença (m)')
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

def fronteira_de_pareto(makespans, instabilidades, filename='pareto_argo.png'):
    pontos = sorted(list(zip(makespans, instabilidades)))
    pareto_front = []
    min_instabilidade = float('inf')

    for m, i in pontos:
        if i < min_instabilidade:
            pareto_front.append((m, i))
            min_instabilidade = i

    pareto_makespans = [p[0] for p in pareto_front]
    pareto_instabilidades = [p[1] for p in pareto_front]

    plt.figure(figsize=(8,6))
    plt.scatter(makespans, instabilidades, c='blue', alpha=0.3, label='Soluções Testadas')
    plt.step(pareto_makespans, pareto_instabilidades, where='post', color='red', linewidth=2, label='Fronteira de Pareto')
    plt.plot(pareto_makespans, pareto_instabilidades, 'ro') 

    plt.title('Fronteira de Pareto: Tempo (Makespan) vs Instabilidade')
    plt.xlabel('Tempo Total')
    plt.ylabel('Penalidade de Estabilidade Total')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.savefig(filename)
    plt.close()

def grafico_gif_descarregamento(historico_eventos, filename='descarregamento_animado.gif'):
    """Gera um GIF animado mostrando o descarregamento top-down para cada andar simultaneamente."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Visão Top-Down do Descarregamento por Andar", fontsize=18, fontweight='bold', color='#1a237e')

    cor_amarelo = 'yellow'
    cor_rosa = '#ffcbdb'
    cor_vazio = '#f5f5f5'

    def get_color(tipo):
        if tipo == 1: return cor_amarelo
        if tipo == 2: return cor_rosa
        return cor_vazio

    def get_label(tipo):
        if tipo == 1: return "x"
        if tipo == 2: return "2x"
        return "N/A"

    def get_boat_coords(x, y):
        return 1.0 + x * 0.9, y * 1.0

    def get_pier_coords(x, y):
        return -2.0 + x * 0.9, 1.0 + y * 1.0

    frames = []
    def add_static_frame(evento, count=3):
        for _ in range(count):
            frames.append({'evento': evento, 'moving': None})

    for ev in historico_eventos:
        if ev['tipo'] == 'init':
            add_static_frame(ev, 5)
            
        elif ev['tipo'] == 'move_to_pier':
            z_from, y_from, x_from = ev['from']
            z_to, y_to, x_to = ev['to']
            start_x, start_y = get_boat_coords(x_from, y_from)
            end_x, end_y = get_pier_coords(x_to, y_to)
            
            steps = 6
            for i in range(steps + 1):
                t = i / steps
                cur_x = start_x + (end_x - start_x) * t
                cur_y = start_y + (end_y - start_y) * t
                frames.append({
                    'evento': ev,
                    'moving': {'id': ev['id'], 'color': ev['color'], 'x': cur_x, 'y': cur_y, 'z_from': z_from, 'z_to': z_to}
                })
            add_static_frame(ev, 2)
            
        elif ev['tipo'] == 'dispatch':
            z_from, y_from, x_from = ev['from']
            start_x, start_y = get_pier_coords(x_from, y_from)
            end_x, end_y = -6.0, start_y 
            
            steps = 6
            for i in range(steps + 1):
                t = i / steps
                cur_x = start_x + (end_x - start_x) * t
                cur_y = start_y + (end_y - start_y) * t
                frames.append({
                    'evento': ev,
                    'moving': {'id': ev['id'], 'color': ev['color'], 'x': cur_x, 'y': cur_y, 'z_from': z_from, 'z_to': z_from}
                })
            add_static_frame(ev, 2)

    def update(frame_data):
        evento = frame_data['evento']
        moving = frame_data['moving']
        
        for z in range(3):
            ax = axes[z]
            ax.clear()
            ax.set_xlim(-4, 5)
            ax.set_ylim(-1, 5)
            ax.set_aspect('equal') 
            ax.axis('off')
            ax.set_title(f"Andar Z={z+1}", fontsize=14, fontweight='bold')

            
            pier_bg = patches.Rectangle((-3.5, 0.5), 1.2, 3, linewidth=2, edgecolor='black', facecolor='#424242')
            ax.add_patch(pier_bg)
            ax.text(-2.9, 2.0, "P Í E R", color='white', weight='bold', rotation=90, ha='center', va='center', fontsize=12)

            
            for py in range(2):
                for px in range(2):
                    coord_x, coord_y = get_pier_coords(px, py)
                    tipo = evento['pier'][z, py, px] if z < 2 else 0
                    cid = evento['pier_ids'][z, py, px] if z < 2 else 0
                    
                    
                    if moving and moving['id'] == cid and evento['tipo'] == 'dispatch':
                        tipo = 0 

                    color = get_color(tipo)
                    label = get_label(tipo)
                    text_color = 'black' if tipo != 0 else '#bbb'
                    
                    rect = patches.Rectangle((coord_x, coord_y), 0.8, 0.9, linewidth=1, edgecolor='gray', facecolor=color)
                    ax.add_patch(rect)
                    ax.text(coord_x + 0.4, coord_y + 0.55, label, color=text_color, weight='bold', ha='center', va='center', fontsize=10)
                    if tipo != 0:
                        ax.text(coord_x + 0.4, coord_y + 0.25, f"#{cid}", color='black', ha='center', va='center', fontsize=8)

            
            for by in range(4):
                for bx in range(4):
                    coord_x, coord_y = get_boat_coords(bx, by)
                    tipo = evento['barco'][z, by, bx]
                    cid = evento['barco_ids'][z, by, bx]
                    
                    color = get_color(tipo)
                    label = get_label(tipo)
                    text_color = 'black' if tipo != 0 else '#bbb'
                    
                    rect = patches.Rectangle((coord_x, coord_y), 0.8, 0.9, linewidth=1, edgecolor='gray', facecolor=color)
                    ax.add_patch(rect)
                    ax.text(coord_x + 0.4, coord_y + 0.55, label, color=text_color, weight='bold', ha='center', va='center', fontsize=10)
                    if tipo != 0:
                        ax.text(coord_x + 0.4, coord_y + 0.25, f"#{cid}", color='black', ha='center', va='center', fontsize=8)

            
            if moving and (z == moving['z_from'] or z == moving['z_to']):
                color = get_color(moving['color'])
                label = get_label(moving['color'])
                rect = patches.Rectangle((moving['x'], moving['y']), 0.8, 0.9, linewidth=2.5, edgecolor='orange', facecolor=color, zorder=10)
                ax.add_patch(rect)
                ax.text(moving['x'] + 0.4, moving['y'] + 0.55, label, color='black', weight='bold', ha='center', va='center', fontsize=10, zorder=11)
                ax.text(moving['x'] + 0.4, moving['y'] + 0.25, f"#{moving['id']}", color='black', ha='center', va='center', fontsize=8, zorder=11)

    ani = animation.FuncAnimation(fig, update, frames=frames, interval=150)
    ani.save(filename, writer='pillow')
    plt.close()

def grafico_gif_rotas(grafo, historico_destinos, filename='rotas_carreristas.gif'):
    """Gera um GIF do carrerista percorrendo os nós do grafo."""
    fig, ax = plt.subplots(figsize=(16, 14)) 
    pos = _layout_campus()

    caminho_completo = ["jambeiro"]
    for destino in historico_destinos:
        if destino in grafo.nodes:
            rota = nx.shortest_path(grafo, source=caminho_completo[-1], target=destino, weight='weight')
            caminho_completo.extend(rota[1:]) 
    
    if caminho_completo[-1] != "jambeiro":
        rota_volta = nx.shortest_path(grafo, source=caminho_completo[-1], target="jambeiro", weight='weight')
        caminho_completo.extend(rota_volta[1:])

    def update(frame):
        ax.clear()
        ax.axis('off')

        ax.set_xlim(-12, 18)
        ax.set_ylim(-8, 16)

        nx.draw_networkx_edges(grafo, pos, alpha=0.2, edge_color='gray', ax=ax)

        nx.draw_networkx_nodes(
            grafo, pos,
            node_color='lightgray',
            node_size=150,
            ax=ax
        )

        nx.draw_networkx_labels(
            grafo, pos,
            font_size=7,
            bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'),
            ax=ax
        )

        if frame > 0:
            percorrido = list(zip(caminho_completo[:frame], caminho_completo[1:frame+1]))

            nx.draw_networkx_edges(
                grafo,
                pos,
                edgelist=percorrido,
                edge_color='orange',
                width=3,
                ax=ax
            )

        no_atual = caminho_completo[frame]

        nx.draw_networkx_nodes(
            grafo,
            pos,
            nodelist=[no_atual],
            node_color='red',
            node_size=500,
            edgecolors='black',
            linewidths=2,
            ax=ax
        )

        ax.set_title(
            f"Movimentação do Carrerista\nPassando por: {no_atual}",
            fontsize=15,
            fontweight='bold'
        )

    ani = animation.FuncAnimation(fig, update, frames=len(caminho_completo), interval=300)
    ani.save(filename, writer='pillow')
    plt.close()

def _layout_campus():
    """
    Layout manual do campus.
    Coordenadas pensadas para parecer mapa real:
    Norte = jambeiro
    Centro = entrada/biblioteca
    Leste = ocean/baja/urutau/quadra
    Sul = bloco C
    Oeste = bloco B
    """

    pos = {

        # =========================
        # NORTE / JAMBEIRO
        # =========================
        "jambeiro": (0, 14),
        "jambeiro Saída 1": (0, 12),
        "jambeiro Saída 2": (-6, 8),

        # =========================
        # BLOCO A SUPERIOR
        # =========================
        "Corredor Bloco A-B-1.2": (0, 10),
        "Corredor Bloco A-B-1.1": (-2, 8),
        "Corredor Bloco A-B-1.3": (3, 10),
        "Corredor Bloco A-B-1.4": (6, 8),

        "Sala A4": (-5, 9),
        "Sala A18": (7, 10),

        # =========================
        # CENTRO
        # =========================
        "Corredor Daetec 1": (-2, 5),
        "Entrada": (1, 4),
        "Escadaria entrada": (2, 5),
        "Escadaria biblioteca": (5, 5),
        "Hub": (3, 3),
        "Callidus": (6, 3),

        # =========================
        # LESTE / ÁREA EXTERNA
        # =========================
        "Ocean": (10, 5),
        "Baja": (10, 3),
        "Quadra": (10, 1),
        "FemtonLab": (13, 2),
        "Urutau": (16, 1),

        "Entrada lado da Quadra": (12, 0),
        "Entrada lado do Campo": (11, -1),

        "Corredor STEM-RU": (14, 4),
        "Corredor STEM-OCEAN": (14, 5),

        # =========================
        # BLOCO D
        # =========================
        "Corredor Bloco D-1.1": (8, 6),
        "Corredor Bloco D-1.2": (8, -1),
        "Corredor Bloco D-1.3": (8, 2),

        # =========================
        # BLOCO B OESTE
        # =========================
        "Corredor B-1.1": (-7, 4),
        "Corredor B-1.2": (-7, 1),
        "Cruza Bloco B->A": (-10, 5),

        # =========================
        # TRANSIÇÃO B -> C
        # =========================
        "Corredor Transicao B->C": (-6, -1),

        # =========================
        # BLOCO BC
        # =========================
        "Corredor Bloco B-C-1.1": (-1, 1),
        "Corredor Bloco B-C-1.2": (-3, -2),
        "Corredor Bloco B-C-1.3": (1, -2),
        "Corredor Bloco B-C-1.4": (5, -1),

        # =========================
        # BLOCO C
        # =========================
        "Corredor Bloco C-1.1": (4, -5),
        "Corredor Bloco C-1.2": (7, -4),
        "Corredor Bloco C-1.3": (3, -4),
        "Corredor Bloco C-1.4": (-1, -3),

        "Sala C18": (9, -6),
    }

    return pos

def grafico_cromossomos(historico_cromossomos, filename='heatmap_cromossomos.png'):
    """Gera um mapa de calor mostrando a convergência dos genes ao longo das gerações"""
    
    matriz_evolucao = np.array([crom.flatten() for crom in historico_cromossomos])

    plt.figure(figsize=(12, 8))
    plt.imshow(matriz_evolucao, aspect='auto', cmap='plasma', interpolation='nearest')
    plt.colorbar(label='Valor do Gene (Coordenadas / Destino)')
    
    plt.title('Convergência Genética: Cromossomos no Decorrer das Gerações', fontsize=14, fontweight='bold')
    plt.xlabel('Índice do Gene (Ações Achatadas)', fontsize=12)
    plt.ylabel('Geração', fontsize=12)
    
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()