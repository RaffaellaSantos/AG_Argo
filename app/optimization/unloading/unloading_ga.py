import numpy as np
import random
import copy

from app.config import AZUL, DEMANDA_CAMPUS, VAZIO, VERMELHO
from app.optimization.unloading.port_manager import PortManager


class Argo:
    def __init__(
        self,
        barco: list,
        travel_model,
        num_carriers: int,
        margem_erro: int = 15,
        num_containers: int = 24,
        tam_populacao: int = 100,
        p_mutacao: float = 0.1,  # Evitar minimos locais
        p_crossover: float = 0.8,
        num_geracoes: int = 100,
        semente_individuo: np.ndarray = None,
    ):
        self.barco = barco
        self.travel_model = travel_model
        self.num_carriers = num_carriers
        self.num_containers = num_containers
        self.tam_populacao = tam_populacao
        self.p_mutacao = p_mutacao
        self.p_crossover = p_crossover
        self.num_geracoes = num_geracoes
        self.tam_cromossomos = self.num_containers + margem_erro
        self.populacao = [self.gerar_cromossomo() for _ in range(self.tam_populacao)]
        # Variáveis para armazenar o histórico
        self.historico_melhor_individuo = []
        self.historico_media = []
        self.pier = np.zeros((2, 2, 2))

        if semente_individuo is not None:
            self.populacao[0] = copy.deepcopy(semente_individuo)
            for i in range(1, int(tam_populacao * 0.1)):
                clone = copy.deepcopy(semente_individuo)
                self.mutar(clone)
                self.populacao[i] = clone

    def garra(self, garra_pos_atual: tuple[int, int], alvo_y: int, alvo_x: int):
        """Reproz o movimento da garra que pega os containers"""

        movimentos = abs(garra_pos_atual[0] - alvo_y) + abs(garra_pos_atual[1] - alvo_x)
        nova_posicao = (alvo_y, alvo_x)
        return movimentos, nova_posicao

    def verificar_container_abaixo(self, matriz: np.ndarray, y: int, x: int, acao: str):
        """Verifica se existe um container abaixo"""

        match acao:
            case "pegar":
                for z in range(matriz.shape[0] - 1, -1, -1):
                    if matriz[z, y, x] != 0:
                        return z
                return -1
            case "largar":
                for z in range(matriz.shape[0]):
                    if matriz[z, y, x] == 0:
                        return z
                return -1
            case _:
                return -1

    def calcular_estabilidade(self, barco_aux: np.ndarray, peso_total_barco: float):
        """Calcula o centro de massa e retorna a penalidade caso esteja instável."""
        centro_massa_x=8.5

        if peso_total_barco > 0:
            pos_x = np.array([2.125, 6.375, 10.625, 14.875])
            centro_barco = 8.5

            pesos_colunas = np.sum(barco_aux, axis=(0,1))
            pesos_x = np.sum(barco_aux, axis=(0, 1))

            centro_massa_x = np.sum(pesos_colunas * pos_x) / peso_total_barco

            desvio = abs(centro_massa_x - centro_barco)
            if desvio > 1.0: 
                return desvio * 100.0, centro_massa_x

        return 0.0, centro_massa_x

    def simular_descarregamento(self, cromossomo: np.ndarray, log: bool = False):
        """Simula o descarregamento de containers e o transporte dos mesmos"""


        barco_aux = copy.deepcopy(self.barco)
        pier_aux = copy.deepcopy(self.pier)
        historico_cm = []

        demandas_restantes = {
            AZUL: copy.deepcopy(DEMANDA_CAMPUS[AZUL]),
            VERMELHO: copy.deepcopy(DEMANDA_CAMPUS[VERMELHO]),
        }

        tempo_guidaste = 0.0
        penalidade = 0.0
        posicao_garra = (0, 0)
        peso_total_barco = int(np.sum(barco_aux))

        manager = PortManager(self.num_carriers, self.travel_model, pier_aux, log)

        if log:
            print("\n" + "=" * 50)
            print("SIMULAÇÃO DE EVENTOS: DESCARREGAMENTO & ROTAS")
            print("=" * 50)

        for i, acao in enumerate(cromossomo):
            if np.count_nonzero(barco_aux) == 0:
                break

            barco_y, barco_x, pier_y, pier_x, gene_destino = acao
            passo = i + 1

            colunas_com_container = []
            for y in range(barco_aux.shape[1]):
                for x in range(barco_aux.shape[2]):
                    if self.verificar_container_abaixo(barco_aux, y, x, "pegar") != -1:
                        colunas_com_container.append((y, x))

            if not colunas_com_container:
                break

            idx_escolhido = (barco_y + barco_x) % len(colunas_com_container)
            barco_y, barco_x = colunas_com_container[idx_escolhido]

            pegar_z = self.verificar_container_abaixo(
                barco_aux, barco_y, barco_x, "pegar"
            )

            if pegar_z == -1:
                penalidade += 500.0  # modificar conforme necessidade
                continue

            # Verifica o tipo de container e associa o destino
            tipo_buscado = barco_aux[pegar_z, barco_y, barco_x]

            is_stock = False

            if len(demandas_restantes[tipo_buscado]) > 0:
                idx_escolhido = gene_destino % len(demandas_restantes[tipo_buscado])
                destino_final = demandas_restantes[tipo_buscado].pop(idx_escolhido)
            else:
                destino_final = "ESTOQUE_PIER"
                is_stock = True

            barco_aux[pegar_z, barco_y, barco_x] = VAZIO

            movimento, posicao_garra = self.garra(posicao_garra, barco_y, barco_x)
            tempo_guidaste += movimento
            peso_total_barco -= tipo_buscado
            custo_estabilidade, cm_atual = self.calcular_estabilidade(barco_aux, peso_total_barco)

            penalidade+= custo_estabilidade
            historico_cm.append(cm_atual)

            movimento, posicao_garra = self.garra(posicao_garra, pier_y, pier_x)
            tempo_chegada_pier = tempo_guidaste + movimento

            manager.limpar_pier(tempo_chegada_pier)

            largar_z = self.verificar_container_abaixo(
                pier_aux, pier_y, pier_x, "largar"
            )

            while largar_z == -1:
                manager.despachar_caminhao()

                if not manager.tem_fila():
                    break

                next_dep = manager.proxima_saida()

                if next_dep <= tempo_chegada_pier:
                    next_dep = tempo_chegada_pier + 0.1

                tempo_chegada_pier = next_dep
                manager.limpar_pier(tempo_chegada_pier)
                largar_z = self.verificar_container_abaixo(
                    pier_aux, pier_y, pier_x, "largar"
                )

            if largar_z == -1:
                faltam_entregas = len(demandas_restantes[AZUL]) + len(
                    demandas_restantes[VERMELHO]
                )
                if faltam_entregas > 0:
                    penalidade += 100000.0
                else:
                    penalidade += 500.0

                barco_aux[pegar_z, barco_y, barco_x] = tipo_buscado
                peso_total_barco += tipo_buscado
                if not is_stock:
                    demandas_restantes[tipo_buscado].append(destino_final)
                continue

            tempo_guidaste = tempo_chegada_pier
            pier_aux[largar_z, pier_y, pier_x] = tipo_buscado

            if not is_stock:
                manager.pier_unassigned.append(
                    {
                        "dest": destino_final,
                        "ready_time": tempo_guidaste,
                        "slot": (largar_z, pier_y, pier_x),
                    }
                )

            if log:
                cor = "Vermelho" if tipo_buscado == VERMELHO else "Azul"
                tag = (
                    f" -> Entregar em {destino_final}"
                    if not is_stock
                    else " -> Deixado em Estoque"
                )
                print(
                    f"[{tempo_guidaste:06.1f}] Guindaste (Passo {passo:02d}): Moveu container {cor} (Y:{barco_y + 1} X:{barco_x + 1} Z;{pegar_z + 1}) para o Pier (Y:{pier_y + 1} X:{pier_x + 1} Z;{largar_z + 1}) {tag}"
                )

            while len(manager.pier_unassigned) >= 2:
                manager.despachar_caminhao()

        while len(manager.pier_unassigned) > 0:
            manager.despachar_caminhao(forcar_um=True)

        makespan_total = max(manager.tempo_maximo_frota(), tempo_guidaste)
        manager.limpar_pier(makespan_total + 1.0)

        containers_restantes = np.count_nonzero(barco_aux)
        penalidade += (
            containers_restantes**2
        ) * 50000.0  # Tentando evitar que cotainers fiquem no barco

        if log:
            print("\n" + "=" * 50)
            print("RELATÓRIO DO INDIVÍDUO OTIMIZADO")
            print(f"MAKESPAN TOTAL: {makespan_total:.1f} unidades de tempo")
            print(f"CONTAINERS RESTANTES NO BARCO: {containers_restantes}")

            estoque_final = np.count_nonzero(pier_aux)
            print(f"CONTAINERS DEIXADOS NO PÍER (Estoque): {estoque_final}")
            print("=" * 50 + "\n")

        return containers_restantes, makespan_total, penalidade, historico_cm

    def funcao_fitness(self, cromossomo: np.ndarray):
        """
        Penaliza movimentos inválidos e instabilidade.
        No entanto, recompensa menor custo na distância percorrida.
        """

        restantes, makespan, penalidade, _ = self.simular_descarregamento(cromossomo, log=False)

        if restantes > 0:
            fator_falha = 1000000.0 * (restantes ** 2)
            return 1.0 / (fator_falha + penalidade + makespan + 1.0)

        custo_total = makespan + penalidade
        return 1000000.0 / (custo_total + 1.0)

    def gerar_cromossomo(self):
        """
        Gera cromossomos com coordenadas aleatórios de posicionamento barco -> pier.
        """
        cromossomo = []

        for _ in range(self.tam_cromossomos):
            barco_y, barco_x = random.randint(0, 3), random.randint(0, 3)
            pier_y, pier_x = random.randint(0, 1), random.randint(0, 1)
            gene_destnino = random.randint(0, 99)
            cromossomo.append([barco_y, barco_x, pier_y, pier_x, gene_destnino])
        return np.array(cromossomo)

    def inicializar_otimizacao(self):
        """Inicializa otimização."""
        for gen in range(self.num_geracoes):
            fitnesses = [self.funcao_fitness(individuo) for individuo in self.populacao]

            melhor_idx = int(np.argmax(fitnesses))
            melhor_fitness = fitnesses[melhor_idx]
            melhor_individuo = self.populacao[melhor_idx].copy()

            print(f"Geração {gen} | Melhor Fitness: {melhor_fitness:.4f}")

            self.historico_melhor_individuo.append(melhor_fitness)
            self.historico_media.append(float(np.mean(fitnesses)))

            nova_população = []
            nova_população.append(melhor_individuo)  # Elitismo

            while len(nova_população) < self.tam_populacao:
                pai = self.torneio(fitnesses)
                mae = self.torneio(fitnesses)

                primogenito, ultimogênito = self.crossover(pai, mae)

                self.mutar(primogenito)
                self.mutar(ultimogênito)

                nova_população.append(primogenito)

                if len(nova_população) < self.tam_populacao:
                    nova_população.append(ultimogênito)
            self.populacao = nova_população

        return self.historico_melhor_individuo, self.historico_media, self.populacao[0]

    def torneio(self, fitnesses: list[float], num_competidores: int = 3):
        """Seleciona por torneio. Minimizar perda de diversidade"""
        participantes = random.sample(range(self.tam_populacao), num_competidores)
        ganhador = max(participantes, key=lambda idx: fitnesses[idx])
        return self.populacao[ganhador].copy()

    def crossover(self, pai: np.ndarray, mae: np.ndarray):
        """Crossover de 2 pontos na sequência de ações"""
        if np.random.rand() < self.p_crossover:
            ponto = np.random.randint(2, self.tam_cromossomos - 1)
            primogenito = np.concatenate([pai[:ponto], mae[ponto:]])
            ultimogênito = np.concatenate([mae[:ponto], pai[ponto:]])
            return primogenito, ultimogênito
        return pai.copy(), mae.copy()

    def mutar(self, individuo: np.ndarray):
        """Altera uma coordenada aleatoriamente."""
        for i in range(self.tam_cromossomos):
            if np.random.rand() < self.p_mutacao:
                individuo[i][0] = random.randint(0, 3)
                individuo[i][1] = random.randint(0, 3)

            if np.random.rand() < self.p_mutacao:
                individuo[i][2] = random.randint(0, 1)
                individuo[i][3] = random.randint(0, 1)

            if np.random.rand() < self.p_mutacao:
                individuo[i][4] = random.randint(0, 99)

    def passo_a_passo(self, melhor_cromossomo: np.ndarray):
        """Imprime o passo a passo do melhor resultado"""
        self.simular_descarregamento(melhor_cromossomo, log=True)
