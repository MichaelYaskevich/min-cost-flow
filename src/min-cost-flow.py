import sys


def get_delta_for_e(e, is_direct, flow):
    return 1 - flow[e] if is_direct else flow[(e[1], e[0])]


def sgn(direct):
    return 1 if direct else -1


def get_cost(e, direct):
    return r[e if direct else (e[1], e[0])]


def get_cycle_cost(q):
    return sum(sgn(direct) * get_cost(e, direct) for e, direct in q.values())


def is_cyclic_dfs(path, vertex, adjacency_lists, target, flow):
    for neighbour, direct in adjacency_lists[vertex]:
        if get_delta_for_e((vertex, neighbour), direct, flow) == 0:
            continue

        if neighbour == target:
            path[vertex] = ((vertex, target), direct)
            return True, path
        if neighbour not in path:
            new_path = path.copy()
            new_path[vertex] = ((vertex, neighbour), direct)
            ok, result = is_cyclic_dfs(new_path, neighbour, adjacency_lists, target, flow)
            if ok:
                if get_cycle_cost(result) < 0:
                    return True, result

    return False, None


def get_f_cycle(v, adjacency_lists, flow):
    for neighbour, direct in adjacency_lists[v]:
        if get_delta_for_e((v, neighbour), direct, flow) == 0:
            continue
        for neighbour2, direct2 in adjacency_lists[neighbour]:
            if neighbour2 == v or get_delta_for_e((neighbour, neighbour2), direct2, flow) == 0:
                continue
            path = {v: ((v, neighbour), direct), neighbour: ((neighbour, neighbour2), direct2)}
            ok, result = is_cyclic_dfs(path, neighbour2, adjacency_lists, v, flow)
            if ok:
                return True, result
    return False, None


def initialize_flow(adjacency_lists):
    flow = {}
    for v in adjacency_lists.keys():
        for w, direct in adjacency_lists[v]:
            if direct:
                flow[(v, w)] = 0

    current = 0
    while current != len(adjacency_lists) - 1:
        v, direct = sorted(adjacency_lists[current], key=lambda x: (not x[1], x[0]))[0]
        flow[(current, v)] = 1
        current = v

    return flow


def update_flow(chain, flow):
    delta = get_delta_for_chain(chain, flow)
    for e, direct in chain.values():
        edge = e if direct else (e[1], e[0])
        flow[edge] = flow[edge] + delta * sgn(direct)
    return flow


def get_delta_for_chain(chain, flow):
    return min(get_delta_for_e(e, is_direct, flow) for e, is_direct in chain.values())


def straight_algo(adjacency_lists):
    flow = initialize_flow(adjacency_lists)
    for v in adjacency_lists.keys():
        ok, result = get_f_cycle(v, adjacency_lists, flow)
        if ok:
            flow = update_flow(result, flow)
    return flow


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]

if __name__ == '__main__':
    with open(INPUT, 'r') as f:
        all_dist = int(f.readline())
        tank, km_for_litre, primaryCost, N = [float(x) for x in f.readline().split()]
        tank, km_for_litre, N = int(tank), int(km_for_litre), int(N)
        d = [0]
        costs = []
        for i in range(N):
            dist, cost = [float(x) for x in f.readline().split()]
            dist = int(dist)
            d.append(dist)
            costs.append(cost)
    d.append(all_dist)
    adjacency_lists = {}
    r = {}
    for i in range(N + 1):
        if i not in adjacency_lists:
            adjacency_lists[i] = []
        for j in range(i + 1, N + 2):
            if j not in adjacency_lists:
                adjacency_lists[j] = []
            max_dist = tank * km_for_litre
            if d[j] - d[i] <= max_dist and (j + 1 == len(d) or (j + 1 < len(d) and
                                                                (d[j + 1] - d[i] > max_dist
                                                                 or d[j] - d[i] > 0.5 * max_dist))):
                adjacency_lists[i].append((j, True))
                adjacency_lists[j].append((i, False))
                if j + 1 == len(d):
                    r[(i, j)] = 0
                else:
                    r[(i, j)] = round(((d[j] - d[i]) / km_for_litre) * costs[j - 1], 1) + 20

    flow = straight_algo(adjacency_lists)
    with open(OUTPUT, 'w') as f:
        f.write(str(sum((r[e]) * v for e, v in flow.items()) + primaryCost) + '0')
