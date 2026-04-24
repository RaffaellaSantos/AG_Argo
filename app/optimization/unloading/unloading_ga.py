import numpy as np
import random
import copy
import math 

from app.config import AMARELO, DEMANDA_CAMPUS, LARGURA_CONTAINER_CM, ROSA, VAZIO, VELOCIDADE_GARRA_CM_S
from app.optimization.unloading.port_manager import PortManager


class Argo:
    def __init__(
        self,
        file: any,
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
        self.historico_solucoes = []
        self.historico_melhor_cromossomo = []
        self.pier = np.zeros((2, 2, 2))
        self.file = file

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
        
        PESO_VAZIO = 900.0   #peso do navio sem carga (ainda precisa ser confirmado)
        L = 60.0             #comprimento da embarcação (cm)
        B = 18.0             #largura da embarcação (cm)
        KG0 = 10.62          #altura do centro de gravidade a partir da quilha (ainda precisa ser confirmado)   
        rho = 1.0            #densidade água doce
        delta_t = PESO_VAZIO + peso_total_barco  #peso atual (variação)

        #Calado dinâmico (T)
        T = delta_t / (L * B * rho)

        KB = T / 2  #altura do centro de carena
        BM = (B ** 2)/(12 * T)  #raio metacêntrico transversal (o 12 vem da inércia de um retângulo)
        G0M = KB + BM - KG0     #altura metacêntrica inicial

        pos_x = np.array([9.132, 22.932, 36.732, 46.932]) #posição ao longo do comprimento (centros de cada conteiner)
        pos_y = np.array([2.26, 6.78, 11.30, 15.82])      #posições laterais (largura)
        pos_z = np.array([2.1, 6.3, 10.5])                #pilhas de conteiners

        centro_alvo_x = 30.0    #L/2
        centro_alvo_y = 9.0     #18 cm / 2

        if peso_total_barco > 0:
            pesos_x = np.sum(barco_aux, axis=(0, 1))     #peso total nas 4 "fatias" verticais do navio
            pesos_y = np.sum(barco_aux, axis=(0,2))      #peso total de cada "corredor"
            pesos_z = np.sum(barco_aux, axis = (1, 2))   #peso total de cada andar de conteiners

            cm_z = np.sum(pesos_z * pos_z)/peso_total_barco  #centro de gravidade vertical da carga
            gm = G0M - cm_z                                  #nova altura metacêntrica

            momentos_y = np.sum(pesos_y * (pos_y - centro_alvo_y)) #soma de momentos em relação á linha de centro 
            tan_theta = momentos_y / (delta_t * gm)                #fórmula da inclinação estática
            list_graus = math.degrees(math.atan(tan_theta))        #converte inclinação de rad->graus

            momentos_x = np.sum(pesos_x * (pos_x - centro_alvo_x))  #diferença de peso entre proa e popa
            trim = (L * momentos_x) / (delta_t * gm)                #diferença de calado entre a frente e a trás

            penalidade = 0.0

            if gm<=0:
                penalidade += 2000.0  #navio instável
            
            penalidade += abs(list_graus) * 100     #penaliza grandes inclinações
            penalidade += abs(trim) * 50            #penaliza desnivelamento

            return penalidade, {"GM": gm, "List": list_graus, "Trim": trim, "Gz": cm_z} #devolve o custo
        
        return 0.0, {"GM": G0M, "List": 0, "Trim": 0, "Gz": 0}


    def simular_descarregamento(self, cromossomo: np.ndarray, log: bool = False):
        """Simula o descarregamento de containers e o transporte dos mesmos"""

        barco_aux = copy.deepcopy(self.barco)
        pier_aux = copy.deepcopy(self.pier)
        historico_cm = []
        historico_rotas = []

        barco_ids = np.zeros_like(barco_aux, dtype=int)
        pier_ids = np.zeros_like(pier_aux, dtype=int)
        cid = 1
        for z in range(barco_aux.shape[0]):
            for y in range(barco_aux.shape[1]):
                for x in range(barco_aux.shape[2]):
                    if barco_aux[z,y,x] != VAZIO:
                        barco_ids[z,y,x] = cid
                        cid += 1

        historico_eventos = []
        historico_eventos.append({
            'tipo': 'init',
            'barco': copy.deepcopy(barco_aux), 'pier': copy.deepcopy(pier_aux),
            'barco_ids': copy.deepcopy(barco_ids), 'pier_ids': copy.deepcopy(pier_ids)
        })

        demandas_restantes = {
            AMARELO: copy.deepcopy(DEMANDA_CAMPUS[AMARELO]),
            ROSA: copy.deepcopy(DEMANDA_CAMPUS[ROSA]),
        }

        tempo_guidaste = 0.0
        penalidade = 0.0
        posicao_garra = (0, 0)
        peso_total_barco = int(np.sum(barco_aux))

        manager = PortManager(self.file, self.num_carriers, self.travel_model, pier_aux, pier_ids, log)

        def registrar_eventos_despacho():
            for desp in manager.eventos_despacho:
                historico_eventos.append({
                    'tipo': 'dispatch', 'id': desp['id'], 'color': desp['color'], 'from': desp['slot'],
                    'barco': copy.deepcopy(barco_aux), 'pier': copy.deepcopy(pier_aux),
                    'barco_ids': copy.deepcopy(barco_ids), 'pier_ids': copy.deepcopy(pier_ids)
                })
            manager.eventos_despacho.clear()

        if log:
            print("\n" + "=" * 50)
            print("SIMULAÇÃO DE EVENTOS: DESCARREGAMENTO & ROTAS")
            print("=" * 50)
            header = (
                "<h1 style='text-align: center; color: #1a237e;'>Relatório Passo a Passo: Operação Argo</h1>"
                "<hr/><h2 style='color: #0d47a1;'>1. Log de Movimentações</h2>"
            )
            self.file.write(header + "\n")

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
            container_id = barco_ids[pegar_z, barco_y, barco_x]
            barco_aux[pegar_z, barco_y, barco_x] = VAZIO
            barco_ids[pegar_z, barco_y, barco_x] = 0

            is_stock = False

            if len(demandas_restantes[tipo_buscado]) > 0:
                idx_escolhido = gene_destino % len(demandas_restantes[tipo_buscado])
                destino_final = demandas_restantes[tipo_buscado].pop(idx_escolhido)
            else:
                destino_final = "ESTOQUE_PIER"
                is_stock = True

            barco_aux[pegar_z, barco_y, barco_x] = VAZIO

            movimento, posicao_garra = self.garra(posicao_garra, barco_y, barco_x)
            tempo_guidaste += (movimento * LARGURA_CONTAINER_CM) / VELOCIDADE_GARRA_CM_S
            peso_total_barco -= tipo_buscado
            custo_estabilidade, status_estabilidade = self.calcular_estabilidade(barco_aux, peso_total_barco)

            penalidade += custo_estabilidade
            historico_cm.append(status_estabilidade)

            movimento, posicao_garra = self.garra(posicao_garra, pier_y, pier_x)
            tempo_chegada_pier = tempo_guidaste + movimento

            manager.limpar_pier(tempo_chegada_pier)
            registrar_eventos_despacho()

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
                faltam_entregas = len(demandas_restantes[AMARELO]) + len(
                    demandas_restantes[ROSA]
                )
                if faltam_entregas > 0:
                    penalidade += 100000.0
                else:
                    penalidade += 500.0

                barco_aux[pegar_z, barco_y, barco_x] = tipo_buscado
                barco_ids[pegar_z, barco_y, barco_x] = container_id
                peso_total_barco += tipo_buscado
                if not is_stock:
                    demandas_restantes[tipo_buscado].append(destino_final)
                continue

            tempo_guidaste = tempo_chegada_pier
            pier_aux[largar_z, pier_y, pier_x] = tipo_buscado
            pier_ids[largar_z, pier_y, pier_x] = container_id

            historico_eventos.append({
                'tipo': 'move_to_pier', 'id': container_id, 'color': tipo_buscado,
                'from': (pegar_z, barco_y, barco_x), 'to': (largar_z, pier_y, pier_x),
                'barco': copy.deepcopy(barco_aux), 'pier': copy.deepcopy(pier_aux),
                'barco_ids': copy.deepcopy(barco_ids), 'pier_ids': copy.deepcopy(pier_ids)
            })

            if not is_stock:
                manager.pier_unassigned.append(
                    {
                        "dest": destino_final,
                        "ready_time": tempo_guidaste,
                        "slot": (largar_z, pier_y, pier_x),
                    }
                )
                historico_rotas.append(destino_final)

            if log:
                cor_nome = "Rosa" if tipo_buscado == ROSA else "Amarelo"
                tag = (
                    f" -> Entregar em {destino_final}"
                    if not is_stock
                    else " -> Deixado em Estoque"
                )
                print(
                    f"[{tempo_guidaste:06.1f}] Guindaste (Passo {passo:02d}): Moveu container {cor_nome} (Y:{barco_y + 1} X:{barco_x + 1} Z;{pegar_z + 1}) para o Pier (Y:{pier_y + 1} X:{pier_x + 1} Z;{largar_z + 1}) {tag}"
                )
                cor_style = "#b81466" if tipo_buscado == ROSA else "#b8b814"
                tag_html = f"<b style='color: green;'>📍 Destino: {destino_final}</b>" if not is_stock else "<b style='color: red;'>📦 Estoque</b>"
                
                log_guindaste = (
                    f"<div style='background: #f5f5f5; padding: 8px; margin: 5px 0; border-radius: 4px; color:#111;'>"
                    f"<b>[{tempo_guidaste:06.1f}] 🏗️ Guindaste (Passo {passo:02d})</b><br/>"
                    f"Moveu container <span style='color: {cor_style};'>{cor_nome}</span> "
                    f"de Navio "
                    f"<b style='font-size:1.1em; color:#111; background:#e0e0e0; padding:2px 6px; border-radius:4px;'>"
                    f"(Y:{barco_y+1} X:{barco_x+1} Z:{pegar_z+1})</b> para "
                    f"Píer "
                    f"<b style='font-size:1.1em; color:#111; background:#e0e0e0; padding:2px 6px; border-radius:4px;'>"
                    f"(Y:{pier_y+1} X:{pier_x+1} Z:{largar_z+1})</b> "
                    f"| {tag_html}</div>"
                )
                self.file.write(log_guindaste + "\n")

            while len(manager.pier_unassigned) >= 2:
                manager.despachar_caminhao()

        while len(manager.pier_unassigned) > 0:
            manager.despachar_caminhao(forcar_um=True)

        tempo_ultima_entrega = max(manager.historico_entregas, default=0.0)

        makespan_total = max(tempo_guidaste, tempo_ultima_entrega)
        manager.limpar_pier(manager.tempo_maximo_frota() + 1.0)
        registrar_eventos_despacho()

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
            
            estoque_final = np.count_nonzero(pier_aux)
            relatorio_final = f"""
<div style='margin-top: 30px; padding: 20px; border: 2px solid #1a237e; border-radius: 8px;'>
    <h2 style='color: #1a237e; margin-top: 0;'>2. Resumo da Solução Otimizada</h2>
    <table style='width: 100%; border-collapse: collapse;'>
        <tr style='background: #e8eaf6;'>
            <th style='text-align: left; padding: 10px; border-bottom: 1px solid #ccc;'>Indicador</th>
            <th style='text-align: left; padding: 10px; border-bottom: 1px solid #ccc;'>Valor</th>
        </tr>
        <tr>
            <td style='padding: 10px; border-bottom: 1px solid #eee;'>Makespan Total</td>
            <td style='padding: 10px; border-bottom: 1px solid #eee;'><b>{makespan_total:.1f} unidades</b></td>
        </tr>
        <tr>
            <td style='padding: 10px; border-bottom: 1px solid #eee;'>Containers no Barco</td>
            <td style='padding: 10px; border-bottom: 1px solid #eee;'><b>{containers_restantes}</b></td>
        </tr>
        <tr>
            <td style='padding: 10px;'>Estoque no Píer</td>
            <td style='padding: 10px;'><b>{estoque_final}</b></td>
        </tr>
    </table>
</div>
            """
            self.file.write(relatorio_final)

        return containers_restantes, makespan_total, penalidade, historico_cm, historico_eventos, historico_rotas

    def funcao_fitness(self, cromossomo: np.ndarray):
        """
        Penaliza movimentos inválidos e instabilidade.
        No entanto, recompensa menor custo na distância percorrida.
        """

        restantes, makespan, penalidade, _, _, _ = self.simular_descarregamento(cromossomo, log=False)

        self.historico_solucoes.append((makespan, penalidade))

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

            print(f"Geração {gen + 1} | Melhor Fitness: {melhor_fitness:.4f}")

            self.historico_melhor_individuo.append(melhor_fitness)
            self.historico_media.append(float(np.mean(fitnesses)))
            self.historico_melhor_cromossomo.append(melhor_individuo.copy())

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

        return self.historico_melhor_individuo, self.historico_media, self.populacao[0], self.historico_melhor_cromossomo

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

