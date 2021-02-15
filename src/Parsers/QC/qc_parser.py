import plyplus



def naive_parse(filepath):
    fp = open(filepath, 'r')
    f_data = fp.readlines()


def generate_adjusted_qc(orig_filepath, smd_map):
    fp = open(orig_filepath, 'r')
    f_data = fp.readlines()
    for item, key in smd_map.items():
        f_data.replace(item, key)

    return f_data
