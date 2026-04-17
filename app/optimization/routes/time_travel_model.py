from typing import Sequence


class TravelTimeModel:
    """Índice 0 = píer; travel[i,j] = tempo de i até j (mesmas unidades que ready_time)."""

    def __init__(self, travel_matrix: Sequence[Sequence[float]], node_names: list[str] = None):
        rows = [[float(x) for x in row] for row in travel_matrix]
        n = len(rows)
        if n == 0 or any(len(r) != n for r in rows):
            raise ValueError("travel_matrix deve ser quadrada e não vazia")
        self.matrix = rows
        self.n = n

        self.node_to_idx = {name: i for i, name in enumerate(node_names)} if node_names else None

    def time(self, origin: int | str, dest: int | str) -> float:
        idx_origin = self.node_to_idx[origin] if isinstance(origin, str) and self.node_to_idx else origin
        idx_dest = self.node_to_idx[dest] if isinstance(dest, str) and self.node_to_idx else dest
        return self.matrix[idx_origin][idx_dest]

    @staticmethod
    def from_symmetric_distances(
        distances: Sequence[Sequence[float]], node_names: list[str] = None, speed: float = 1.0
    ) -> "TravelTimeModel":
        spd = float(speed)
        t = [
            [float(distances[i][j]) / spd for j in range(len(distances[i]))]
            for i in range(len(distances))
        ]
        return TravelTimeModel(t, node_names)
    
