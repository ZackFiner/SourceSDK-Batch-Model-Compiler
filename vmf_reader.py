import numpy as np
import re

def parse_ents(vmf_line_data):
    sub_regions = list()
    t_st_ind = -1
    param_count = 0
    for index in range(len(vmf_line_data)):
        if "entity" in vmf_line_data[index]:
            t_st_ind = index
            continue
        if not t_st_ind == -1 and "{" in vmf_line_data[index]:
            param_count += 1
        if not t_st_ind == -1 and "}" in vmf_line_data[index]:
            param_count += -1
        if not t_st_ind == -1 and param_count == 0:
            sub_regions.append((t_st_ind, index+1))
            t_st_ind = -1

    return sub_regions


def get_group_ids(data_groups, data_mf):
    r_set = set()
    for group in data_groups:
        for i in range(group[0], group[1]):
            if '"visgroupid"' in data_mf[i]:
                r_set.add(data_mf[i])
    return r_set


def get_entities_by_visgroup(data_groups, data_mf, visgroupid):
    r_set = list()
    for group in data_groups:
        for i in range(group[0], group[1]):
            if '"visgroupid"' in data_mf[i] and int(data_mf[i].split(" ")[1].replace('"',""))==visgroupid:
                r_set.append(group)
    return r_set


def read_vmf(filename: str):
    file = open(filename, 'r')
    f_data = file.readlines()
    return parse_ents(f_data), f_data

def get_visgroupid_by_name(file_data, name):
    data_start = -1
    braket_level = 0
    for i in range(len(file_data)):  # read up to the visgroups area
        if file_data[i] == "visgroups\n":
            data_start = i
            break
    group_data = list()
    index = data_start
    temp_start = -1
    while True:
        index += 1
        if "{" in file_data[index]:
            braket_level += 1
            if braket_level == 2:
                temp_start = index
        if "}" in file_data[index]:
            braket_level -= 1
            if braket_level == 1:
                group_data.append((temp_start+1, index-1))
        if braket_level == 0:
            break
    for start, end in group_data:
        group_name = re.match(r'(?:\s*\"name\" \")(?P<name>.+)(?:\".*)', file_data[start]).groupdict()["name"]
        id = file_data[start+1].split(" ")[1].replace('"', "").replace("\n", "")
        if group_name == name:
            return int(id)
    return -1

def get_batch_points_by_group(filename, groupid:int=None, group_name:str=None):
    index_groups, file_data = read_vmf(filename)
    if groupid is None:
        groupid = get_visgroupid_by_name(file_data, group_name)
    new_groups = get_entities_by_visgroup(index_groups, file_data, groupid)
    r_data = list()
    for group in new_groups:
        r_data.append(batch_data_point(group, file_data))
    return r_data


class batch_data_point:
    def __init__(self, parse_data_group, parse_data):
        self.mdl_str = ""
        for i in range(parse_data_group[0], parse_data_group[1]):
            if '"model"' in parse_data[i]:
                self.mdl_str = parse_data[i].split(" ")[1]
            if '"origin"' in parse_data[i]:
                tokens = parse_data[i].split(" ")[1:]
                self.pt = np.array([float(tokens[0].replace('"',"")), float(tokens[1].replace('"',"")),float(tokens[2].replace('"',""))])
            if '"angles"' in parse_data[i]:
                tokens = parse_data[i].split(" ")[1:]
                self.ang = np.array([float(tokens[0].replace('"',"")), float(tokens[1].replace('"',"")),float(tokens[2].replace('"',""))])


data = get_batch_points_by_group("gm_ost1.vmf", group_name="Flora Clumped")
print(len(data))