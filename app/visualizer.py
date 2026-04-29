import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import networkx as nx
import numpy as np


def grafico_evolucao(historico_melhor, historico_media, filename="evolucao_ag.png"):
    plt.figure(figsize=(10, 5))
    plt.plot(historico_melhor, label="Melhor Fitness", color="blue", linewidth=2)
    plt.plot(
        historico_media, label="Media da População", color="orange", linestyle="--"
    )

    plt.title("Progresso do Algoritmo Genético - Estabilidade do Navio")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(filename)
    plt.show()


def grafico_estabilidade(
    historico_estabilidade, filename="estabilidade_naval_final.png"
):
    # Extrai os dados individuais da lista de dicionários
    list_gm = [d["GM"] for d in historico_estabilidade]
    list_graus = [d["List"] for d in historico_estabilidade]
    list_trim = [d["Trim"] for d in historico_estabilidade]
    passos = range(1, len(historico_estabilidade) + 1)
 
    # Cria uma figura com 3 subplots (3 linhas, 1 coluna)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
 
    # 1. Gráfico de GM (Altura Metacêntrica) - Estabilidade Vertical
    ax1.plot(
        passos, list_gm, color="blue", marker="s", label="GM (Altura Metacêntrica)"
    )
    ax1.axhline(y=0.5, color="red", linestyle="--", label="Limite Mínimo Seguro (0.5m)")
    ax1.set_ylabel("GM (m)")
    ax1.set_title("Estabilidade Naval durante o Descarregamento")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)
 
    # 2. Gráfico de Banda (List) - Inclinação Lateral (Eixo Y)
    ax2.plot(passos, list_graus, color="green", marker="o", label="Banda (List)")
    ax2.axhspan(-5, 5, color="green", alpha=0.1, label="Zona Segura (±5°)")
    ax2.set_ylabel("Inclinação (°)")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)
 
    # 3. Gráfico de Trim - Inclinação Longitudinal (Eixo X)
    ax3.plot(
        passos,
        list_trim,
        color="purple",
        marker="^",
        label="Trim (Diferença Proa/Popa)",
    )
    ax3.set_xlabel("Ordem de Retirada (Container nº)")
    ax3.set_ylabel("Diferença (m)")
    ax3.legend(loc="upper right")
    ax3.grid(True, alpha=0.3)
 
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()



def fronteira_de_pareto(makespans, instabilidades, restantes, filename="pareto_argo.png"):
    """
    Plota a fronteira de Pareto real: Makespan vs Instabilidade Naval Pura.
 
    Recebe três listas paralelas vindas de historico_solucoes:
      - makespans: tempo total da operação
      - instabilidades: custo de estabilidade acumulado (só custo naval, sem penalidades de falha)
      - restantes: containers que sobraram no barco (0 = solução válida)
 
    Só soluções com restantes == 0 entram na fronteira de Pareto.
    """
    from scipy.interpolate import PchipInterpolator
 
    # --- Separação válidas / inválidas ---
    validas   = [(m, i) for m, i, r in zip(makespans, instabilidades, restantes) if r == 0]
    invalidas = [(m, i) for m, i, r in zip(makespans, instabilidades, restantes) if r > 0]
 
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#f8f9fa")
 
    if not validas:
        ax.set_title("Fronteira de Pareto — nenhuma solução válida ainda")
        ax.set_xlabel("Makespan (tempo total)"); ax.set_ylabel("Instabilidade Naval Acumulada")
        plt.tight_layout(); plt.savefig(filename, dpi=150); plt.close()
        return
 
    all_i_validas = [p[1] for p in validas]
    all_m_validas = [p[0] for p in validas]
 
    # Limita Y ao percentil 98 para não deixar outliers distorcerem a escala
    top_y = np.percentile(all_i_validas, 98) * 1.25
    top_y = max(top_y, 200)
    x_ini = min(all_m_validas) * 0.997
    x_fim = max(all_m_validas) * 1.003
 
    # --- Scatter das inválidas: cinza, pequenas, no fundo ---
    if invalidas:
        inv_m = [p[0] for p in invalidas]
        inv_i = [min(p[1], top_y * 0.95) for p in invalidas]  # comprime no topo se > ylim
        ax.scatter(inv_m, inv_i, c="#bbbbbb", alpha=0.2, s=6, zorder=1,
                   label=f"Barco não esvaziado (n={len(invalidas)})")
 
    # --- Scatter das válidas: colorido por densidade ---
    # Usa hexbin como mapa de calor para mostrar onde as soluções se concentram
    val_m = np.array(all_m_validas)
    val_i = np.array(all_i_validas)
    # Filtra para o ylim antes do hexbin
    mask = val_i <= top_y
    hb = ax.hexbin(val_m[mask], val_i[mask], gridsize=55, cmap="Blues",
                   mincnt=1, alpha=0.75, zorder=2, linewidths=0.2)
    cb = fig.colorbar(hb, ax=ax, pad=0.01, shrink=0.85)
    cb.set_label("Densidade de soluções", fontsize=9)
 
    # --- Fronteira de Pareto ---
    pareto = []
    min_i = float("inf")
    for m, i in sorted(validas):
        if i < min_i:
            pareto.append((m, i))
            min_i = i
 
    pm = [p[0] for p in pareto]
    pi = [p[1] for p in pareto]
 
    # Curva suave Pchip sobre os pontos da fronteira
    if len(pm) >= 4:
        xs = np.linspace(pm[0], x_fim, 800)
        pchip = PchipInterpolator(pm + [x_fim], pi + [pi[-1]])
        ys = np.clip(pchip(xs), pi[-1], pi[0])
        # Sombra da curva (efeito glow)
        for lw, alpha in [(10, 0.08), (6, 0.12), (3.5, 0.2)]:
            ax.plot(xs, ys, color="#FF1744", linewidth=lw, alpha=alpha, zorder=7)
        ax.plot(xs, ys, color="#FF1744", linewidth=2.0, zorder=8, label="Fronteira de Pareto")
    else:
        ax.step(pm + [x_fim], pi + [pi[-1]], where="post",
                color="#FF1744", linewidth=2.5, zorder=8, label="Fronteira de Pareto")
 
    # Pontos exatos da fronteira
    ax.scatter(pm, pi, color="white", s=40, zorder=9, edgecolors="#FF1744", linewidths=1.5)
 
    # --- Cotovelo ---
    mn_m, mx_m = pm[0], pm[-1]
    mn_i, mx_i = pi[-1], pi[0]
    melhor_dist = float("inf")
    melhor = pareto[0]
    for m, i in pareto:
        nm = (m - mn_m) / (mx_m - mn_m) if mx_m != mn_m else 0
        ni = (i - mn_i) / (mx_i - mn_i) if mx_i != mn_i else 0
        if (nm**2 + ni**2) ** 0.5 < melhor_dist:
            melhor_dist = (nm**2 + ni**2) ** 0.5
            melhor = (m, i)
 
    # Zona de destaque ao redor do cotovelo
    circ = plt.Circle((melhor[0], melhor[1]), radius=(x_fim - x_ini) * 0.025,
                       color="gold", alpha=0.25, zorder=10)
    ax.add_patch(circ)
 
    ax.plot(melhor[0], melhor[1], marker="*", color="gold", markersize=24,
            markeredgecolor="#333", markeredgewidth=0.8, zorder=11,
            label="Melhor Trade-off (Cotovelo)")
 
    # Linhas de referência do cotovelo
    ax.axvline(melhor[0], color="#FFA000", linestyle=":", linewidth=1.4, alpha=0.8, zorder=6)
    ax.axhline(melhor[1], color="#FFA000", linestyle=":", linewidth=1.4, alpha=0.8, zorder=6)
 
    # Posição inteligente da anotação: evita sair do gráfico
    txt_offset_x = 35 if melhor[0] < (x_ini + x_fim) / 2 else -140
    txt_offset_y = 40 if melhor[1] < top_y * 0.7 else -60
    ax.annotate(
        f"Melhor Escolha\nMakespan: {melhor[0]:.1f}\nInstabilidade: {melhor[1]:.0f}",
        xy=(melhor[0], melhor[1]),
        xytext=(txt_offset_x, txt_offset_y), textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="#333", lw=1.8),
        fontsize=10, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5", fc="#fff9c4", ec="#999", alpha=0.97),
        zorder=12
    )
 
    # --- Formatação final ---
    ax.set_xlim(x_ini, x_fim)
    ax.set_ylim(-top_y * 0.02, top_y)
    ax.set_title("Fronteira de Pareto: Makespan vs Instabilidade Naval",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Makespan — tempo total da operação (s)", fontsize=11)
    ax.set_ylabel("Instabilidade Naval Acumulada", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.35, color="#aaaaaa")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)
 
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()


def grafico_gif_descarregamento(
    historico_eventos, filename="descarregamento_animado.gif"
):
    """Gera um GIF animado mostrando o descarregamento top-down para cada andar simultaneamente."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(
        "Visão Top-Down do Descarregamento por Andar",
        fontsize=18,
        fontweight="bold",
        color="#1a237e",
    )

    cor_amarelo = "yellow"
    cor_rosa = "#ffcbdb"
    cor_vazio = "#f5f5f5"

    def get_color(tipo):
        if tipo == 1:
            return cor_amarelo
        if tipo == 2:
            return cor_rosa
        return cor_vazio

    def get_label(tipo):
        if tipo == 1:
            return "x"
        if tipo == 2:
            return "2x"
        return "N/A"

    def get_boat_coords(x, y):
        return 1.0 + x * 0.9, y * 1.0

    def get_pier_coords(x, y):
        return -2.0 + x * 0.9, 1.0 + y * 1.0

    frames = []

    def add_static_frame(evento, count=3):
        for _ in range(count):
            frames.append({"evento": evento, "moving": None})

    for ev in historico_eventos:
        if ev["tipo"] == "init":
            add_static_frame(ev, 5)

        elif ev["tipo"] == "move_to_pier":
            z_from, y_from, x_from = ev["from"]
            z_to, y_to, x_to = ev["to"]
            start_x, start_y = get_boat_coords(x_from, y_from)
            end_x, end_y = get_pier_coords(x_to, y_to)

            steps = 6
            for i in range(steps + 1):
                t = i / steps
                cur_x = start_x + (end_x - start_x) * t
                cur_y = start_y + (end_y - start_y) * t
                frames.append(
                    {
                        "evento": ev,
                        "moving": {
                            "id": ev["id"],
                            "color": ev["color"],
                            "x": cur_x,
                            "y": cur_y,
                            "z_from": z_from,
                            "z_to": z_to,
                        },
                    }
                )
            add_static_frame(ev, 2)

        elif ev["tipo"] == "dispatch":
            z_from, y_from, x_from = ev["from"]
            start_x, start_y = get_pier_coords(x_from, y_from)
            end_x, end_y = -6.0, start_y

            steps = 6
            for i in range(steps + 1):
                t = i / steps
                cur_x = start_x + (end_x - start_x) * t
                cur_y = start_y + (end_y - start_y) * t
                frames.append(
                    {
                        "evento": ev,
                        "moving": {
                            "id": ev["id"],
                            "color": ev["color"],
                            "x": cur_x,
                            "y": cur_y,
                            "z_from": z_from,
                            "z_to": z_from,
                        },
                    }
                )
            add_static_frame(ev, 2)

    def update(frame_data):
        evento = frame_data["evento"]
        moving = frame_data["moving"]

        for z in range(3):
            ax = axes[z]
            ax.clear()
            ax.set_xlim(-4, 5)
            ax.set_ylim(-1, 5)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_title(f"Andar Z={z + 1}", fontsize=14, fontweight="bold")

            pier_bg = patches.Rectangle(
                (-3.5, 0.5), 1.2, 3, linewidth=2, edgecolor="black", facecolor="#424242"
            )
            ax.add_patch(pier_bg)
            ax.text(
                -2.9,
                2.0,
                "P Í E R",
                color="white",
                weight="bold",
                rotation=90,
                ha="center",
                va="center",
                fontsize=12,
            )

            for py in range(2):
                for px in range(2):
                    coord_x, coord_y = get_pier_coords(px, py)
                    tipo = evento["pier"][z, py, px] if z < 2 else 0
                    cid = evento["pier_ids"][z, py, px] if z < 2 else 0

                    if moving and moving["id"] == cid and evento["tipo"] == "dispatch":
                        tipo = 0

                    color = get_color(tipo)
                    label = get_label(tipo)
                    text_color = "black" if tipo != 0 else "#bbb"

                    rect = patches.Rectangle(
                        (coord_x, coord_y),
                        0.8,
                        0.9,
                        linewidth=1,
                        edgecolor="gray",
                        facecolor=color,
                    )
                    ax.add_patch(rect)
                    ax.text(
                        coord_x + 0.4,
                        coord_y + 0.55,
                        label,
                        color=text_color,
                        weight="bold",
                        ha="center",
                        va="center",
                        fontsize=10,
                    )
                    if tipo != 0:
                        ax.text(
                            coord_x + 0.4,
                            coord_y + 0.25,
                            f"#{cid}",
                            color="black",
                            ha="center",
                            va="center",
                            fontsize=8,
                        )

            for by in range(4):
                for bx in range(4):
                    coord_x, coord_y = get_boat_coords(bx, by)
                    tipo = evento["barco"][z, by, bx]
                    cid = evento["barco_ids"][z, by, bx]

                    color = get_color(tipo)
                    label = get_label(tipo)
                    text_color = "black" if tipo != 0 else "#bbb"

                    rect = patches.Rectangle(
                        (coord_x, coord_y),
                        0.8,
                        0.9,
                        linewidth=1,
                        edgecolor="gray",
                        facecolor=color,
                    )
                    ax.add_patch(rect)
                    ax.text(
                        coord_x + 0.4,
                        coord_y + 0.55,
                        label,
                        color=text_color,
                        weight="bold",
                        ha="center",
                        va="center",
                        fontsize=10,
                    )
                    if tipo != 0:
                        ax.text(
                            coord_x + 0.4,
                            coord_y + 0.25,
                            f"#{cid}",
                            color="black",
                            ha="center",
                            va="center",
                            fontsize=8,
                        )

            if moving and (z == moving["z_from"] or z == moving["z_to"]):
                color = get_color(moving["color"])
                label = get_label(moving["color"])
                rect = patches.Rectangle(
                    (moving["x"], moving["y"]),
                    0.8,
                    0.9,
                    linewidth=2.5,
                    edgecolor="orange",
                    facecolor=color,
                    zorder=10,
                )
                ax.add_patch(rect)
                ax.text(
                    moving["x"] + 0.4,
                    moving["y"] + 0.55,
                    label,
                    color="black",
                    weight="bold",
                    ha="center",
                    va="center",
                    fontsize=10,
                    zorder=11,
                )
                ax.text(
                    moving["x"] + 0.4,
                    moving["y"] + 0.25,
                    f"#{moving['id']}",
                    color="black",
                    ha="center",
                    va="center",
                    fontsize=8,
                    zorder=11,
                )

    ani = animation.FuncAnimation(fig, update, frames=frames, interval=150)
    ani.save(filename, writer="pillow")
    plt.close()


def grafico_gif_rotas(grafo, historico_destinos, filename="rotas_carreristas.gif"):
    """Gera um GIF do carrerista percorrendo os nós do grafo."""
    fig, ax = plt.subplots(figsize=(16, 14))
    pos = _layout_campus()

    caminho_completo = ["jambeiro"]
    for destino in historico_destinos:
        if destino in grafo.nodes:
            rota = nx.shortest_path(
                grafo, source=caminho_completo[-1], target=destino, weight="weight"
            )
            caminho_completo.extend(rota[1:])

    if caminho_completo[-1] != "jambeiro":
        rota_volta = nx.shortest_path(
            grafo, source=caminho_completo[-1], target="jambeiro", weight="weight"
        )
        caminho_completo.extend(rota_volta[1:])

    def update(frame):
        ax.clear()
        ax.axis("off")

        ax.set_xlim(-12, 18)
        ax.set_ylim(-8, 16)

        nx.draw_networkx_edges(grafo, pos, alpha=0.2, edge_color="gray", ax=ax)

        nx.draw_networkx_nodes(grafo, pos, node_color="lightgray", node_size=150, ax=ax)

        nx.draw_networkx_labels(
            grafo,
            pos,
            font_size=7,
            bbox=dict(facecolor="white", alpha=0.6, edgecolor="none"),
            ax=ax,
        )

        if frame > 0:
            percorrido = list(
                zip(caminho_completo[:frame], caminho_completo[1 : frame + 1])
            )

            nx.draw_networkx_edges(
                grafo, pos, edgelist=percorrido, edge_color="orange", width=3, ax=ax
            )

        no_atual = caminho_completo[frame]

        nx.draw_networkx_nodes(
            grafo,
            pos,
            nodelist=[no_atual],
            node_color="red",
            node_size=500,
            edgecolors="black",
            linewidths=2,
            ax=ax,
        )

        ax.set_title(
            f"Movimentação do Carrerista\nPassando por: {no_atual}",
            fontsize=15,
            fontweight="bold",
        )

    ani = animation.FuncAnimation(
        fig, update, frames=len(caminho_completo), interval=300
    )
    ani.save(filename, writer="pillow")
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


def grafico_cromossomos(historico_cromossomos, filename="heatmap_cromossomos.png"):
    """Gera um mapa de calor mostrando a convergência dos genes ao longo das gerações"""

    matriz_evolucao = np.array([crom.flatten() for crom in historico_cromossomos])

    plt.figure(figsize=(12, 8))
    plt.imshow(
        matriz_evolucao, aspect="auto", cmap="nipy_spectral", interpolation="nearest"
    )
    plt.colorbar(label="Valor do Gene (Coordenadas / Destino)")

    plt.title(
        "Convergência Genética: Cromossomos no Decorrer das Gerações",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Índice do Gene (Ações Achatadas)", fontsize=12)
    plt.ylabel("Geração", fontsize=12)

    plt.grid(False)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
