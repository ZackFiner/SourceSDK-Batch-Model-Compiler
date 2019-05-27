import vmf_reader
import numpy as np

def truncate(n, k):
    return int(n/k)*k


def gen_cluster_grid(object_list, grid_size) -> dict:
    grid_dict = dict()
    for object in object_list:
        truncate_key = (truncate(object.pt[0], grid_size), truncate(object.pt[1], grid_size))
        if truncate_key in grid_dict.keys():
            grid_dict[truncate_key].append(object)
        else:
            grid_dict[truncate_key] = [object]

    return grid_dict


def get_neighbors(grid_dict:dict, grid_loc, grid_size)->list:
    r_list = list()
    def add_offset_or_none(pair, r_list):
        target = grid_dict[(grid_loc[0] + pair[0]*grid_size, grid_loc[1] + pair[1]*grid_size)]
        if target is not None:
            r_list.append((target, grid_dict[target]))

    add_offset_or_none((1, 0), r_list)  # north
    add_offset_or_none((1, 1), r_list)  # north east
    add_offset_or_none((0, 1), r_list)  # east
    add_offset_or_none((-1, 1), r_list)  # south east
    add_offset_or_none((-1, 0), r_list)  # south
    add_offset_or_none((-1, -1), r_list)  # south west
    add_offset_or_none((0, -1), r_list)  # west
    add_offset_or_none((1, -1), r_list)  # north west
    return r_list


def get_midpoint(object_list):
    if len(object_list) == 0:
        return None
    x_avg = 0.0
    y_avg = 0.0
    for obj in object_list:
        x_avg += obj.pt[0]
        y_avg += obj.pt[1]
    x_avg /= len(object_list)
    y_avg /= len(object_list)
    return np.array([x_avg, y_avg])


def get_max_outlier(object_list, mid_point):
    if len(object_list) == 0:
        return None
    max_dist = 0.0
    for obj in object_list:
        dist = np.linalg.norm(mid_point-obj.pt)
        if dist > max_dist:
            max_dist = dist
    return max_dist


def un_stack_groups(grid_dict:dict, max_per_grid, finished_list):
    def pop_and_append(from_list, finished_list, max_per_grid):
        running_group = list()
        while len(from_list) > max_per_grid:
            for i in range(max_per_grid):
                running_group.append(from_list.pop())
            finished_list.append(running_group)
            running_group = list()

    for grid_key in grid_dict:
        grid = grid_dict[grid_key]
        if len(grid) > max_per_grid:
            un_stack_groups(grid, finished_list, max_per_grid)
            if len(grid) == 0:
                grid_dict.pop(grid_key)  # we remove empty grids


def evaluate_leftovers(grid_dict, max_per_grid, finished_list, grid_size):
    evaluation_list = [(pair, grid_dict[pair]) for pair in grid_dict.keys()]
    merged_pairs = set()
    while len(evaluation_list) > 0:
        current = evaluation_list.pop()
        if current[0] in merged_pairs:
            continue
        neighbor_list = get_neighbors(grid_dict, current[0], grid_size)

        local_mid = get_midpoint(current[1])
        local_radius = get_max_outlier(current[1], local_mid)

        if local_radius < grid_size/2:  # if our radius already encapsulates the full grid square, we can't add anything
            for neighbor in neighbor_list:  # check if the neighbors can be added to our list
                if len(current[1]) + len(neighbor[1]):
                    n_mid = get_midpoint(neighbor[1])
                    n_rad = get_max_outlier(neighbor[1], n_mid)
                    mid_dist = np.linalg.norm(local_mid-n_mid)
                    if mid_dist+local_radius+n_rad <= grid_size:
                        # we can now group these points together:
                        # we need to update our local midpoint and radius
                        # i can easily update midpoint, but the radius is what i'm confused about
                        merged_pairs.add(neighbor[0])  # mark this pair as merged, so we don't re-evaluate it
                        






def cluster_objects(object_list):
    # we want to break these objects into groups where there are only 40 of them per group
    # keep in mind that 803/40 = 20, so we've reduced the number of props on the map

    def truncate(n, k):
        return int(n/k)*k
    grid_size = 4096
    max_per_grid = 32

    grid_dict = gen_cluster_grid(object_list, grid_size)

    re_combine_groups = dict()
    finished_groups = list()

    un_stack_groups(grid_dict, max_per_grid, finished_groups)

    return finished_groups, re_combine_groups


data = vmf_reader.get_batch_points_by_group("gm_ost1.vmf", 24)
d, r = cluster_objects(data)

def get_max_l(data_dict):
    max_v = 0
    for l in data_dict:
        data_list = data_dict[l]
        if len(data_list) > max_v:
            max_v = len(data_list)
    return max_v
#print(get_max_l(d))
print(len(d))
print(len(r))