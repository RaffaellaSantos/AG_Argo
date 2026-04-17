import random

from app.config import PIER_NODE
from app.optimization.routes.routes_schemas import CarrierEvent, CarrierSchedule, DeliveryTask, RouteSolution
from app.optimization.routes.time_travel_model import TravelTimeModel

def assign_tasks_greedy_by_permutation(
    perm: list[int],
    tasks: list[DeliveryTask],
    travel: TravelTimeModel,
    num_carriers: int,
) -> tuple[list[list[int]], float]:
    n = len(tasks)
    if n == 0:
        return [[] for _ in range(num_carriers)], 0.0

    t_free = [0.0] * num_carriers
    routes: list[list[int]] = [[] for _ in range(num_carriers)]

    i = 0
    while i < len(perm):
        idx_1 = perm[i]
        trip_idxs = [idx_1]

        if i + 1 < len(perm):
            trip_idxs.append(perm[i+1])
            i += 2
        else:
            i += 1

        best_c = 0
        best_finish = float("inf")

        for c in range(num_carriers):
            t = t_free[c]
            ready = max(tasks[idx].ready_time for idx in trip_idxs)
            t_start = max(t, ready)

            pos = PIER_NODE
            t_trip = t_start
            
            for idx in trip_idxs:
                dest = tasks[idx].destination
                t_trip += travel.time(pos, dest)
                pos = dest
            
            t_trip += travel.time(pos, PIER_NODE)

            if t_trip < best_finish:
                best_finish = t_trip
                best_c = c
        
        routes[best_c].extend(trip_idxs)
        t_free[best_c] = best_finish

    makespan = max(t_free) if t_free else 0.0
    return routes, makespan

def permutation_ox(p1: list[int], p2: list[int]) -> tuple[list[int], list[int]]:
    n = len(p1)
    if n < 2:
        return p1[:], p2[:]
    a, b = sorted(random.sample(range(n), 2))

    def ox(a, b, p1, p2):
        hole = set(p1[a : b + 1])
        child = [None] * n
        child[a : b + 1] = p1[a : b + 1]
        fill = [x for x in p2 if x not in hole]
        j = 0
        for i in list(range(0, a)) + list(range(b + 1, n)):
            child[i] = fill[j]
            j += 1
        return child

    return ox(a, b, p1, p2), ox(a, b, p2, p1)

def simulate_routes(
    tasks: list[DeliveryTask],
    travel: TravelTimeModel,
    routes: list[list[int]],
) -> RouteSolution:
    num_carriers = len(routes)
    schedules: list[CarrierSchedule] = []
    total_travel = 0.0

    for c in range(num_carriers):
        events: list[CarrierEvent] = []
        t = 0.0
        route = routes[c]
        i = 0

        while i < len(route):
            trip_tasks = [tasks[route[i]]]

            if i + 1 < len(route):
                trip_tasks.append(tasks[route[i+1]])
                i += 2
            else:
                i += 1
            
            pos = PIER_NODE

            ready_time = max(tk.ready_time for tk in trip_tasks)
            if t < ready_time:
                events.append(CarrierEvent(t, ready_time, "espera", f"aguardando {len(trip_tasks)} container(s)"))
                t = ready_time

            for tk in trip_tasks:
                dest = tk.destination
                t_arrive = t + travel.time(pos, dest)
                total_travel += travel.time(pos, dest)
                events.append(CarrierEvent(t, t_arrive, "deslocamento", f"{pos}->{dest}"))
                events.append(CarrierEvent(t_arrive, t_arrive, "entrega", f"container {tk.container_id} -> destino {dest}"))
                t = t_arrive
                pos = dest

            t_return = t + travel.time(pos, PIER_NODE)
            total_travel += travel.time(pos, PIER_NODE)
            events.append(CarrierEvent(t, t_return, "deslocamento", f"{pos}->{PIER_NODE}"))
            t = t_return

        schedules.append(
            CarrierSchedule(
                carrier_id=c,
                task_indices=list(route),
                events=events,
                finish_time=t,
            )
        )

    makespan = max(s.finish_time for s in schedules) if schedules else 0.0
    return RouteSolution(
        schedules=schedules,
        makespan=makespan,
        total_travel_time=total_travel,
        permutation=None,
    )