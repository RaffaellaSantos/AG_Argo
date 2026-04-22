import matplotlib.pyplot as plt

def grafico_evolucao(historico_melhor, historico_media):
    plt.figure(figsize=(10, 5))
    plt.plot(historico_melhor, label='Melhor Fitness', color='blue', linewidth=2)
    plt.plot(historico_media, label='Media da População', color='orange', linestyle='--')

    plt.title('Progresso do Algoritmo Genético - Estabilidade do Navio')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig('evolucao_ag.png')
    plt.show()

def grafico_estabilidade(historico_estabilidade):
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
    plt.savefig('estabilidade_naval_final.png')
    plt.show()

def fronteira_de_pareto(makespans, instabilidades):
    plt.figure(figsize=(8,6))
    plt.scatter(makespans, instabilidades, c='blue', alpha=0.5, label='Soluções Testadas')

    plt.title('Fronteira de Pareto: Tempo vs Instabilidade')
    plt.xlabel('Tempo Total')
    plt.ylabel('Penalidade de Estabilidade Total')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.savefig('pareto_argo.png')
    plt.show()