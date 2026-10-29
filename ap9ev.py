import random
import matplotlib.pyplot as plt


def sphere(x):
    return sum(xi ** 2 for xi in x)


def clip(val, low, high):
    if val < low:
        return low
    if val > high:
        return high
    return val


def run_de(cost_func, bounds, variant='rand1',
           np_size=50, g_max=200, f=0.5, cr=0.8,
           tau1=0.1, tau2=0.1):

    dim = len(bounds)

    if np_size < 4:
        raise ValueError("Populácia musí mať aspoň 4 jedincov.")
    if dim < 1:
        raise ValueError("Počet dimenzií musí byť aspoň 1.")
    if variant not in ('rand1', 'best1', 'jde'):
        raise ValueError("Neznámy variant DE.")

    # Inicializácia populácie
    pop = []
    fitness = []

    for _ in range(np_size):
        ind = [
            bounds[d][0] + random.random() *
            (bounds[d][1] - bounds[d][0])
            for d in range(dim)
        ]
        pop.append(ind)
        fitness.append(cost_func(ind))

    # Počiatočné parametre pre jDE
    f_arr = [0.5] * np_size
    cr_arr = [0.9] * np_size

    best_idx = min(range(np_size), key=lambda i: fitness[i])
    best_cost = fitness[best_idx]
    best_ind = list(pop[best_idx])

    history = [best_cost]

    # Evolučný proces
    for _ in range(g_max):

        # Najlepší jedinec sa počas generácie nemení
        generation_best_idx = min(
            range(np_size), key=lambda i: fitness[i]
        )
        generation_best = list(pop[generation_best_idx])

        for i in range(np_size):

            # Adaptácia parametrov jDE
            if variant == 'jde':
                cur_f = (
                    0.1 + 0.8 * random.random()
                    if random.random() < tau1
                    else f_arr[i]
                )
                cur_cr = (
                    random.random()
                    if random.random() < tau2
                    else cr_arr[i]
                )
            else:
                cur_f = f
                cur_cr = cr

            # Mutácia
            if variant in ('rand1', 'jde'):
                candidates = [
                    idx for idx in range(np_size) if idx != i
                ]
                r1, r2, r3 = random.sample(candidates, 3)

                v = [
                    pop[r1][d] +
                    cur_f * (pop[r2][d] - pop[r3][d])
                    for d in range(dim)
                ]

            elif variant == 'best1':
                candidates = [
                    idx for idx in range(np_size)
                    if idx != i and idx != generation_best_idx
                ]

                # Výber dvoch rôznych jedincov
                if len(candidates) < 2:
                    candidates = [
                        idx for idx in range(np_size) if idx != i
                    ]

                r1, r2 = random.sample(candidates, 2)

                v = [
                    generation_best[d] +
                    cur_f * (pop[r1][d] - pop[r2][d])
                    for d in range(dim)
                ]

            v = [
                clip(v[d], bounds[d][0], bounds[d][1])
                for d in range(dim)
            ]

            u = list(pop[i])
            j_rand = random.randrange(dim)

            for d in range(dim):
                if random.random() <= cur_cr or d == j_rand:
                    u[d] = v[d]

            # Selekcia
            cost_u = cost_func(u)

            if cost_u <= fitness[i]:
                pop[i] = u
                fitness[i] = cost_u

                if variant == 'jde':
                    f_arr[i] = cur_f
                    cr_arr[i] = cur_cr

        # Aktualizácia najlepšieho jedinca po celej generácii
        best_idx = min(range(np_size), key=lambda i: fitness[i])
        best_cost = fitness[best_idx]
        best_ind = list(pop[best_idx])

        history.append(best_cost)

    return best_ind, best_cost, history


if __name__ == "__main__":

    random.seed(42)

    dim = 10
    bounds = [(-5.12, 5.12)] * dim
    np_size = 40
    g_max = 200

    # Rand/1
    _, best_r, hist_r = run_de(
        sphere, bounds, variant='rand1',
        np_size=np_size, g_max=g_max,
        f=0.5, cr=0.8
    )

    # Best/1
    _, best_b, hist_b = run_de(
        sphere, bounds, variant='best1',
        np_size=np_size, g_max=g_max,
        f=0.5, cr=0.8
    )

    # jDE
    _, best_j, hist_j = run_de(
        sphere, bounds, variant='jde',
        np_size=np_size, g_max=g_max,
        tau1=0.1, tau2=0.1
    )

    print(f"Rand/1: {best_r:.12g}")
    print(f"Best/1: {best_b:.12g}")
    print(f"jDE:    {best_j:.12g}")

    # Graf
    eps = 1e-16

    plt.figure(figsize=(10, 6))

    plt.semilogy(
        [max(v, eps) for v in hist_r],
        label="Rand/1 (F=0.5, CR=0.8)"
    )
    plt.semilogy(
        [max(v, eps) for v in hist_b],
        label="Best/1 (F=0.5, CR=0.8)"
    )
    plt.semilogy(
        [max(v, eps) for v in hist_j],
        label="jDE (tau1=0.1, tau2=0.1)"
    )

    plt.xlabel("Generácia")
    plt.ylabel("Najlepšia hodnota funkcie")
    plt.title("Porovnanie konvergencie diferenciálnej evolúcie")
    plt.legend()
    plt.grid(True, which="both")
    plt.tight_layout()
    plt.show()
