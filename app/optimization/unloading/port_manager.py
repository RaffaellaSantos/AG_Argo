import numpy as np

from app.config import PIER_NODE, VAZIO


class PortManager:
    """Gerencia o despacho de carreristas e a liberação de vagas no píer."""

    def __init__(
        self, file, num_carriers: int, travel_model, pier_aux: np.ndarray, pier_ids: np.ndarray, log: bool = False
    ):
        self.num_carriers = num_carriers
        self.travel_model = travel_model
        self.pier_aux = pier_aux
        self.pier_ids = pier_ids
        self.log = log
        self.file = file

        self.truck_free_time = [0.0] * self.num_carriers
        self.pier_unassigned = []
        self.pier_scheduled = []
        self.eventos_despacho = []
        self.historico_entregas = []

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
            self.historico_entregas.append(t_start + dur)
        dur += self.travel_model.time(pos, PIER_NODE)

        self.truck_free_time[c] = t_start + dur

        for item in trip_c:
            self.pier_scheduled.append({"dep_time": t_start, "slot": item["slot"]})

        if self.log:
            destinos = [item["dest"] for item in trip_c]
            print(
                f"[{t_start:06.1f}] Carrerista {c + 1} saiu com {qtd} entregas para {destinos}"
            )
            destinos_str = ", ".join(destinos)
            log_msg = (
                f"<div style='border-left: 4px solid #2196F3; padding-left: 10px; margin-bottom: 10px;'>"
                f"<b>[{t_start:06.1f}] 🚛 Carrerista {c + 1}</b><br/>"
                f"Saída com {qtd} entrega(s) para: <i>{destinos_str}</i>"
                f"</div>"
            )
            self.file.write(log_msg + "\n")

        return True

    def limpar_pier(self, tempo_atual: float):
        """Remover do pier os containers que já saíram para entrega"""

        restantes = []
        self.eventos_despacho.clear()

        for item in self.pier_scheduled:
            if item["dep_time"] <= tempo_atual:
                z, y, x = item["slot"]
                cid = self.pier_ids[z, y, x]
                tipo = self.pier_aux[z, y, x]

                self.pier_aux[z, y, x] = VAZIO
                self.pier_ids[z, y, x] = 0

                self.eventos_despacho.append({'slot': (z, y, x), 'id': cid, 'color': tipo})
                
                if self.log:
                    print(
                        f"[{item['dep_time']:06.1f}] Carrerista retirou container (Y:{y + 1} X:{x + 1}, Z:{z + 1})"
                    )
                    log_msg = (
                    f"<div style='color: #111; font-size: 0.95em;'>&nbsp;&nbsp;↳ [{item['dep_time']:06.1f}] "
                    f"Container removido do Píer: <b style='color: #111;'>(Y:{y + 1} X:{x + 1}, Z:{z + 1})</b></div>"
                    )
                    self.file.write(log_msg + "\n")
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
