from dataclasses import dataclass, field

@dataclass
class DeliveryTask:
    """Uma entrega: container, destino no grafo, disponível no píer em ready_time."""

    container_id: int
    destination: int
    ready_time: float = 0.0


@dataclass
class CarrierEvent:
    t_start: float
    t_end: float
    kind: str
    detail: str


@dataclass
class CarrierSchedule:
    carrier_id: int
    task_indices: list[int]
    events: list[CarrierEvent] = field(default_factory=list)
    finish_time: float = 0.0


@dataclass
class RouteSolution:
    schedules: list[CarrierSchedule]
    makespan: float
    total_travel_time: float
    permutation: list[int] | None = None