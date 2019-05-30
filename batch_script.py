import vmf_reader
import numpy as np
from PIL import Image, ImageDraw
import random
import math
from transform import *
from SMD import *

def truncate(n, k):
    return int(math.floor(n/k)*k + (k/2))


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
        target = (grid_loc[0] + pair[0]*grid_size, grid_loc[1] + pair[1]*grid_size)
        if target in grid_dict:
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
        dist = np.linalg.norm(mid_point-obj.pt[:2])
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
            pop_and_append(grid, finished_list, max_per_grid)
            if len(grid) == 0:
                grid_dict.pop(grid_key)  # we remove empty grids


def evaluate_leftovers(grid_dict, max_per_grid, finished_list, grid_size, max_cull):
    evaluation_list = [(pair, grid_dict[pair]) for pair in grid_dict.keys()]
    merged_pairs = set()
    while len(evaluation_list) > 0:
        current = evaluation_list.pop()
        if current[0] in merged_pairs:
            continue
        neighbor_list = get_neighbors(grid_dict, current[0], grid_size)

        local_mid = get_midpoint(current[1])
        local_radius = get_max_outlier(current[1], local_mid)

        for neighbor in neighbor_list:  # check if the neighbors can be added to our list
            if local_radius < max_cull / 2:  # if our radius already encapsulates the full grid square, we can't add anything
                if len(current[1]) + len(neighbor[1]) <= max_per_grid:
                    n_mid = get_midpoint(neighbor[1])
                    n_rad = get_max_outlier(neighbor[1], n_mid)
                    mid_dist = np.linalg.norm(local_mid-n_mid)
                    if mid_dist+local_radius+n_rad <= max_cull:
                        # we can now group these points together:
                        # we need to update our local midpoint and radius
                        old_count = len(current[1])
                        old_n_count = len(neighbor[1])

                        merged_pairs.add(neighbor[0])  # mark this pair as merged, so we don't re-evaluate it
                        current[1].extend(neighbor[1])  # add the contents of the neighbor to our cluster
                        grid_dict.pop(neighbor[0])  # remove the neighbor from our grid, as we've emptied it anyway

                        old_local_mid = local_mid
                        local_mid = ((local_mid*old_count) + (n_mid*old_n_count)) / (old_count+old_n_count)
                        local_radius = max((np.linalg.norm(local_mid-old_local_mid) + local_radius),
                                            np.linalg.norm(n_mid-local_mid) + n_rad)
                        #  print("merged at: "+str(current[0][0])+", "+str(current[0][1]))
        merged_pairs.add(current[0])  # mark this entry as evaluated
        grid_dict.pop(current[0])  # remove this entry from the grid, as it has been evaluated
        finished_list.append(current[1])  # add it to the finished list


def cluster_objects(object_list, grid_size, max_per_grid, max_cull):
    # we want to break these objects into groups where there are only 40 of them per group
    # keep in mind that 803/40 = 20, so we've reduced the number of props on the map
    random.shuffle(object_list)

    grid_dict = gen_cluster_grid(object_list, grid_size)

    finished_groups = list()

    un_stack_groups(grid_dict, max_per_grid, finished_groups)
    evaluate_leftovers(grid_dict, max_per_grid, finished_groups, grid_size, max_cull)
    return finished_groups


def generate_smd_for_cluster(cluster_list:list, model_map:dict)->list:
    # model_map needs to map the .mdl files to a corresponding studio model data file name, located
    # in this directory, we will be using it to generate the model data.
    smd_map = dict((k, SMD(filename=model_map[k])) for k in model_map)  # pull immutable SMDs from our file system
    clustered_smds = list()
    for cluster in cluster_list:
        cluster_smd = SMD()
        for object in cluster:
            #  each object has a .pt, .ang, and .mdl_str
            ang_mat = genRotMat(object.ang)
            new_entries = [c.apply_transformation(ang_mat, object.pt) for c in smd_map[object.mdl_str]]
            cluster_smd.triangles.extend(new_entries)
        clustered_smds.append(cluster_smd)
    return clustered_smds


def draw_cluster_image(cluster_set, grid_size):
    cnvs = np.zeros([1024, 1024, 3], dtype=np.uint8)  # create a blank canvas, initially black
    siv = Image.fromarray(cnvs, 'RGB')
    brush = ImageDraw.Draw(siv)
    def new_color():
        """Returns a random color list. RGB."""
        return [round(255 * random.random()), round(255 * random.random()), round(255 * random.random())]
    for cluster in cluster_set:
        cluster_color = new_color()
        for point in cluster:
            our_origin = point.pt[:2]  # np array of dim 3
            our_origin = (our_origin/32_768)*1024 + np.array([512,512])
            brush.ellipse([(our_origin[0], our_origin[1]),(our_origin[0]+10, our_origin[1]+10)], fill=(cluster_color[0],cluster_color[1],cluster_color[2]))

    num_lines = int(32_768/grid_size) - 1
    px_size = 1024/(num_lines+1)
    for i in range(num_lines):
        horizontal_data = [0,(i+1)*px_size, 1024, (i+1)*px_size]
        vertical_data = [(i+1)*px_size, 0, (i+1)*px_size, 1024]
        brush.line(horizontal_data)  # draw horizontal
        brush.line(vertical_data)  # draw vertical



    siv.save('cluster_debug.png')
    # 32768^2
    # 1024x1024




def get_max_l(data_dict):
    max_v = 0
    for l in data_dict:
        data_list = data_dict[l]
        if len(data_list) > max_v:
            max_v = len(data_list)
    return max_v


data = vmf_reader.get_batch_points_by_group("gm_ost1.vmf", 24)
'''5792 is roughly sqrt(4096^2 + 4096^2), this is the max culling radius
enforced by the grids.'''
d = cluster_objects(data, 4096, 32, 5792)
#print(get_max_l(d))
print(len(d))
sum = 0
for item in d:
    print(len(item))
    sum += len(item)

print(sum)
draw_cluster_image(d, 4096)