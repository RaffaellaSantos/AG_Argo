import copy
import random
from statistics import mean

from app.config import PIER_NODE
from app.optimization.routes.routes_schemas import DeliveryTask, RouteSolution
from app.optimization.routes.time_travel_model import TravelTimeModel
from app.optimization.routes.utils import assign_tasks_greedy_by_permutation, permutation_ox, simulate_routes


class RouteOptimizerGA:
    def __init__(
        self,
        tasks: list[DeliveryTask],
        travel: TravelTimeModel,
        num_carriers: int,
        population_size: int = 80,
        generations: int = 150,
        p_crossover: float = 0.85,
        p_mutation: float = 0.15,
        elitism: int = 2,
        rng: random.Random | None = None,
    ):
        self.tasks = tasks
        self.travel = travel
        self.num_carriers = max(1, num_carriers)
        self.population_size = population_size
        self.generations = generations
        self.p_crossover = p_crossover
        self.p_mutation = p_mutation
        self.elitism = min(elitism, population_size)
        self.rng = rng or random.Random()
        self.n = len(tasks)
        self._indices = list(range(self.n))

    def _fitness(self, perm: list[int]) -> float:
        _, makespan = assign_tasks_greedy_by_permutation(
            perm, self.tasks, self.travel, self.num_carriers
        )
        return 1.0 / (makespan + 1e-9)

    def _random_individual(self) -> list[int]:
        ind = self._indices[:]
        self.rng.shuffle(ind)
        return ind

    def _mutate(self, perm: list[int]) -> None:
        if self.n < 2:
            return
        if self.rng.random() < 0.5:
            i, j = self.rng.sample(range(self.n), 2)
            perm[i], perm[j] = perm[j], perm[i]
        else:
            i, j = sorted(self.rng.sample(range(self.n), 2))
            perm[i : j + 1] = reversed(perm[i : j + 1])

    def run(self) -> tuple[RouteSolution, list[float], list[float]]:
        if self.n == 0:
            empty = RouteSolution(
                schedules=[], makespan=0.0, total_travel_time=0.0, permutation=[]
            )
            return empty, [], []

        pop = [self._random_individual() for _ in range(self.population_size)]
        best_hist: list[float] = []
        mean_hist: list[float] = []

        def fit(p):
            return self._fitness(p)

        for _ in range(self.generations):
            fitnesses = [fit(p) for p in pop]
            best_hist.append(max(fitnesses))
            mean_hist.append(mean(fitnesses))

            sorted_idx = sorted(range(self.population_size), key=lambda i: -fitnesses[i])
            new_pop = [copy.deepcopy(pop[sorted_idx[i]]) for i in range(self.elitism)]

            while len(new_pop) < self.population_size:

                def pick():
                    a, b = self.rng.randrange(self.population_size), self.rng.randrange(
                        self.population_size
                    )
                    return pop[a] if fitnesses[a] >= fitnesses[b] else pop[b]

                p1, p2 = pick(), pick()
                if self.rng.random() < self.p_crossover:
                    c1, c2 = permutation_ox(p1, p2)
                else:
                    c1, c2 = copy.deepcopy(p1), copy.deepcopy(p2)

                for c in (c1, c2):
                    if self.rng.random() < self.p_mutation:
                        self._mutate(c)
                    new_pop.append(c)
                    if len(new_pop) >= self.population_size:
                        break
            pop = new_pop[: self.population_size]

        best_perm = max(pop, key=fit)
        routes, makespan = assign_tasks_greedy_by_permutation(
            best_perm, self.tasks, self.travel, self.num_carriers
        )
        sol = simulate_routes(self.tasks, self.travel, routes)
        sol = RouteSolution(
            schedules=sol.schedules,
            makespan=makespan,
            total_travel_time=sol.total_travel_time,
            permutation=best_perm,
        )
        return sol, best_hist, mean_hist


def optimize_routes_greedy(
    tasks: list[DeliveryTask], travel: TravelTimeModel, num_carriers: int
) -> RouteSolution:
    n = len(tasks)
    if n == 0:
        return RouteSolution(
            schedules=[], makespan=0.0, total_travel_time=0.0, permutation=[]
        )
    perm = list(range(n))
    routes, _ = assign_tasks_greedy_by_permutation(perm, tasks, travel, num_carriers)
    sol = simulate_routes(tasks, travel, routes)
    sol.permutation = perm
    return sol


def optimize_routes_ga(
    tasks: list[DeliveryTask],
    travel: TravelTimeModel,
    num_carriers: int,
    **ga_kwargs,
) -> tuple[RouteSolution, list[float], list[float]]:
    return RouteOptimizerGA(tasks, travel, num_carriers, **ga_kwargs).run()


def tasks_from_unloading_order(
    container_destination: list[tuple[int, int]],
    ready_times: list[float] | None = None,
) -> list[DeliveryTask]:
    """Monta entregas a partir de (container_id, destino). destino ≠ 0 (píer)."""
    rt = ready_times or [0.0] * len(container_destination)
    if len(rt) != len(container_destination):
        raise ValueError("ready_times deve ter o mesmo tamanho que container_destination")
    out = []
    for (cid, dest), t in zip(container_destination, rt, strict=True):
        if dest == PIER_NODE:
            raise ValueError("destino não pode ser o píer (0)")
        out.append(DeliveryTask(container_id=cid, destination=dest, ready_time=t))
    return out


def print_solution_summary(solution: RouteSolution, tasks: list[DeliveryTask]) -> None:
    print("=" * 52)
    print("OTIMIZAÇÃO DE ROTAS — RESUMO")
    print("=" * 52)
    print(f"Makespan: {solution.makespan:.4f}")
    print(f"Soma dos deslocamentos: {solution.total_travel_time:.4f}")
    if solution.permutation is not None:
        print(f"Permutação (prioridade): {solution.permutation}")
    print("-" * 52)
    for sch in solution.schedules:
        print(f"\nCarregador {sch.carrier_id} | término: {sch.finish_time:.4f}")
        for idx in sch.task_indices:
            t = tasks[idx]
            print(
                f"  · container {t.container_id} → destino {t.destination} "
                f"(ready no píer: {t.ready_time})"
            )
    print("=" * 52)