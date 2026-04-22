from app.optimization.routes.campus_graph import create_campus_graph, get_travel_matrix
from app.optimization.routes.time_travel_model import TravelTimeModel
from app.optimization.unloading.unloading_ga import Argo
from app.config import BARCO_INICIAL, MARGEM_ERRO, NUM_CARRERISTAS, NUM_GERACOES, NUM_INDIVIDUOS, NUM_CONTAINERS
from app.visualizer import grafico_evolucao, grafico_estabilidade, fronteira_de_pareto

def main():

    print("Mapeando rotas do campus...")
    grafo = create_campus_graph()
    matriz_viagem, nodes = get_travel_matrix(grafo)
    travel_model = TravelTimeModel.from_symmetric_distances(matriz_viagem, node_names=nodes, speed=1.0)

    tentativas = 1
    is_empty_boat = False
    melhor_semente = None

    while not is_empty_boat:
        print(f"Iniciando Algoritmo Genético Argo - Tentativa {tentativas}\n")
        argo_ag: Argo = Argo(
            barco=BARCO_INICIAL,
            travel_model=travel_model,
            num_carriers=NUM_CARRERISTAS,
            margem_erro=MARGEM_ERRO,
            num_geracoes=NUM_GERACOES,
            tam_populacao=NUM_INDIVIDUOS,
            num_containers=NUM_CONTAINERS,
            semente_individuo=melhor_semente
        )
        
        melhor_hist, media_hist, melhor_individuo = argo_ag.inicializar_otimizacao()
        grafico_evolucao(melhor_hist, media_hist)
        
        restantes, makespan, penalidade, lista_estabilidade = argo_ag.simular_descarregamento(melhor_individuo, log=True)
        grafico_estabilidade(lista_estabilidade)

        print("Calculando Fronteira de Pareto")
        lista_makespans = []
        lista_penalidades = []

        for ind in argo_ag.populacao[:100]:
            _, mk, pen, _ = argo_ag.simular_descarregamento(ind)
            lista_makespans.append(mk)
            lista_penalidades.append(pen)

        fronteira_de_pareto(lista_makespans, lista_penalidades)

        if restantes == 0:
            is_empty_boat = True
            print("SUCESSO! Barco esvaziado, frota alocada e excedentes no estoque do píer.")
        else:
            tentativas += 1
            melhor_semente = melhor_individuo
            print(f"A solução falhou! Restaram {restantes} containers o barco.\n")
    
    argo_ag.passo_a_passo(melhor_individuo)

if __name__ == '__main__':
    main()