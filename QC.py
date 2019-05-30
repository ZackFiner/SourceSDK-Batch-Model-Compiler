import re

class QC:
    def __init__(self, filename:str = None):
        self.modelname = ""
        self.body = {"title": "", "studio_path": ""}
        self.static_prop = True
        self.surfaceprop = ""
        self.cdmaterials = list()
        self.sequence = [{"title": "", "studio_path": ""}]
        self.collision_model = {"studio_path": "", "params": ["{ $concave }"]}

    def get_qc_string(self)->str:
        concat_list = [
                 '$modelname\t"',self.modelname,'"\n',
                 '$body ',self.body["title"],'\t"'+self.body["studio_path"],'"\n',
                ('$static_prop\n' if self.static_prop else ''),
                 '$surfaceprop\t',self.surfaceprop,'\n',
                 '$cdmaterials\t']
        concat_list.extend([' "'+path+'"' for path in self.cdmaterials])
        concat_list.append('\n')
        for seq in self.sequence:
            concat_list.extend(["$sequence ",seq["title"],'\t"',seq["studio_path"],'"\n'])
        concat_list.extend(['$collisionmodel "', self.collision_model["studio_path"],'"\t'])
        concat_list.extend([p+' ' for p in self.collision_model["params"]])
        concat_list.append('\n')
        r_str = ''.join(concat_list)
        return r_str

    def write_to_file(self, filename):
        pass

n = QC()
print(n.get_qc_string())

