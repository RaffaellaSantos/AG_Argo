import os

os.environ["DOTNET_ROOT"] = "/usr/share/dotnet"
os.environ["LD_LIBRARY_PATH"] = "/usr/lib/x86_64-linux-gnu"
os.environ["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "1"

from app.optimization.routes.campus_graph import create_campus_graph, get_travel_matrix
from app.optimization.routes.time_travel_model import TravelTimeModel
from app.optimization.unloading.unloading_ga import Argo
from app.config import (
    BARCO_INICIAL,
    MARGEM_ERRO,
    NUM_CARRERISTAS,
    NUM_GERACOES,
    NUM_INDIVIDUOS,
    NUM_CONTAINERS,
    VELOCIDADE_CARRERISTA_CM_S,
)
from app.visualizer import (
    grafico_cromossomos,
    grafico_evolucao,
    grafico_estabilidade,
    fronteira_de_pareto,
    grafico_gif_descarregamento,
    grafico_gif_rotas,
)


def main():

    print("Mapeando rotas do campus...")
    grafo = create_campus_graph()
    matriz_viagem, nodes = get_travel_matrix(grafo)
    travel_model = TravelTimeModel.from_symmetric_distances(
        matriz_viagem, node_names=nodes, speed=VELOCIDADE_CARRERISTA_CM_S
    )

    tentativas = 1
    is_empty_boat = False
    melhor_semente = None

    while not is_empty_boat:
        root_path = "outputs"
        steps_path = os.path.join(root_path, "passo_a_passo")
        graph_path = os.path.join(root_path, "graficos")
        os.makedirs(root_path, exist_ok=True)
        os.makedirs(steps_path, exist_ok=True)
        os.makedirs(graph_path, exist_ok=True)
        md_path = os.path.join(steps_path, "passo_a_passo.md")

        with open(md_path, "w", encoding="utf-8") as file:
            file.write(
                "<html><head><meta charset='utf-8'><style>"
                "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; padding: 40px; }"
                "h1, h2 { border-bottom: 2px solid #1a237e; padding-bottom: 10px; }"
                "table { margin-top: 20px; }"
                ".page-break { page-break-before: always; }"
                "</style></head><body>"
            )

            print(f"Iniciando Algoritmo Genético Argo - Tentativa {tentativas}\n")

            argo_ag: Argo = Argo(
                file=file,
                barco=BARCO_INICIAL,
                travel_model=travel_model,
                num_carriers=NUM_CARRERISTAS,
                margem_erro=MARGEM_ERRO,
                num_geracoes=NUM_GERACOES,
                tam_populacao=NUM_INDIVIDUOS,
                num_containers=NUM_CONTAINERS,
                semente_individuo=melhor_semente,
            )

            melhor_hist, media_hist, melhor_individuo, hist_cromossomos = argo_ag.inicializar_otimizacao()
            grafico_evolucao(melhor_hist, media_hist, filename=os.path.join(graph_path, 'evolucao_ag.png'))

            (
                restantes,
                makespan,
                penalidade,
                lista_estabilidade,
                historico_eventos,
                hist_rotas,
            ) = argo_ag.simular_descarregamento(melhor_individuo, log=True)
            
            grafico_estabilidade(lista_estabilidade, filename=os.path.join(graph_path, 'estabilidade_naval_final.png'))

            grafico_cromossomos(hist_cromossomos, filename=os.path.join(graph_path, 'heatmap_cromossomos.png'))

            print("Calculando Fronteira de Pareto")
            lista_makespans = []
            lista_penalidades = []

            for mk, pen in argo_ag.historico_solucoes:
                lista_makespans.append(mk)
                lista_penalidades.append(pen)

            fronteira_de_pareto(lista_makespans, lista_penalidades, filename=os.path.join(graph_path, 'pareto_argo.png'))

            print("Gerando GIFs Analíticos...")
            grafico_gif_descarregamento(
                historico_eventos,
                filename=os.path.join(graph_path, "descarregamento_matriz.gif"),
            )
            grafico_gif_rotas(
                grafo,
                hist_rotas,
                filename=os.path.join(graph_path, "rotas_carreristas.gif"),
            )

            if restantes == 0:
                is_empty_boat = True
                print(
                    "SUCESSO! Barco esvaziado, frota alocada e excedentes no estoque do píer."
                )
            else:
                tentativas += 1
                melhor_semente = melhor_individuo
                print(f"A solução falhou! Restaram {restantes} containers o barco.\n")

        with open(md_path, "a", encoding="utf-8") as file:
            file.write("</body></html>")


if __name__ == "__main__":
    main()
