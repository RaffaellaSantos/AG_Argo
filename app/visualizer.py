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

def grafico_estabilidade(historico_cm):
    plt.figure(figsize = (12,5))

    plt.plot(historico_cm, color= 'red', marker='o', markersize=4, label='Trajetória do Centro de Massa')
    plt.axhline(y=8.5, color='black', linestyle='-', alpha=0.5, label='Centro Real(8.5 cm)')
    plt.axhspan(7.5, 9.5, color='green', alpha=0.2, label='Zona de Segurança(+-1cm)')

    plt.title('Estabilidade da Embarcação durante o Descarregamento')
    plt.xlabel('Ordem de Retirada (Ação nº)')
    plt.ylabel('Posição do Centro de Massa (cm)')
    plt.ylim(0,17) #largura da balsa
    plt.legend(loc='upper right')
    plt.grid(True, linestyle=':', alpha=0.6)

    plt.savefig('estabilidade_final.png')
    plt.show()

def fronteira_de_pareto(makespans, instabilidades):
    plt.figure(figsize=(8,6))

    plt.scatter(makespans, instabilidades, c='blue', alpha=0.5, label='Soluções Testadas')

    plt.title('Fronteira de Pareto: Tempo vs Instabilidade')
    plt.xlabel('Tempo Total')
    plt.ylabel('Penalidade de  Estabilidade (Desvio CM)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.savefig('pareto_argo.png')
    plt.show()
    