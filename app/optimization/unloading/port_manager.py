import numpy as np

from app.config import PIER_NODE, VAZIO


class PortManager:
    """Gerencia o despacho de carreristas e a liberação de vagas no píer."""

    def __init__(
        self, num_carriers: int, travel_model, pier_aux: np.ndarray, log: bool = False
    ):
        self.num_carriers = num_carriers
        self.travel_model = travel_model
        self.pier_aux = pier_aux
        self.log = log

        self.truck_free_time = [0.0] * self.num_carriers
        self.pier_unassigned = []
        self.pier_scheduled = []

    def despachar_caminhao(self, forcar_um: bool = False) -> bool:
        """Aloca um container a um carrerista e agendar a liberação da vaga."""

        qtd = 2
        if forcar_um and len(self.pier_unassigned) == 1:
            qtd = 1
        elif len(self.pier_unassigned) < 2:
            return False

        c = int(np.argmin(self.truck_free_time))
        c_free = self.truck_free_time[c]

        trip_c = [self.pier_unassigned.pop(0) for _ in range(qtd)]
        ready_time = max(item["ready_time"] for item in trip_c)

        t_start = max(c_free, ready_time)

        carretistas_na_rua = [t for t in self.truck_free_time if t > t_start]

        if len(carretistas_na_rua) >= 2:
            t_start = min(carretistas_na_rua)

        pos = PIER_NODE
        dur = 0.0

        for item in trip_c:
            dest = item["dest"]
            dur += self.travel_model.time(pos, dest)
            pos = dest
        dur += self.travel_model.time(pos, PIER_NODE)

        self.truck_free_time[c] = t_start + dur

        for item in trip_c:
            self.pier_scheduled.append({"dep_time": t_start, "slot": item["slot"]})

        if self.log:
            destinos = [item["dest"] for item in trip_c]
            print(
                f"[{t_start:06.1f}] Carrerista {c} saiu com {qtd} entregas para {destinos}"
            )

        return True

    def limpar_pier(self, tempo_atual: float):
        """Remover do pier os containers que já saíram para entrega"""

        restantes = []

        for item in self.pier_scheduled:
            if item["dep_time"] <= tempo_atual:
                z, y, x = item["slot"]
                self.pier_aux[z, y, x] = VAZIO
                if self.log:
                    print(
                        f"[{item['dep_time']:06.1f}] Carrerista retirou container (Y:{y + 1} X:{x + 1}, Z:{z + 1})"
                    )
            else:
                restantes.append(item)
        self.pier_scheduled = restantes

    def tem_fila(self) -> bool:
        """Verifica se há carrerista para sair"""
        return len(self.pier_scheduled) > 0

    def proxima_saida(self) -> float:
        """Retorna o tempo em que o próximo carrerista sairá do píer"""
        if not self.pier_scheduled:
            return float("inf")
        return min(item["dep_time"] for item in self.pier_scheduled)

    def tempo_maximo_frota(self) -> float:
        """Retorna o makespan da fronta de carrerista"""
        return max(self.truck_free_time) if self.truck_free_time else 0.0
