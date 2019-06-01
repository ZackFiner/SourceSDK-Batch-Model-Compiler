import subprocess
import os
import shutil
import vmf_reader
import re
import time
from tile_script import genTiledSMD
from SMD import *
from QC import *
from batch_script import *
studiomdlpath = 'C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Source\\bin\studiomdl.exe'
gamepath = 'C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Source\cstrike'

def modifyQC(data:list, new_smd_name, new_model_name):
    new_data = data.copy()
    for i in range(len(new_data)):
        x = new_data[i]
        if '$modelname' in x:
            d = x.split()
            model_string = d[1]
            tokens = re.split('\\\\|/', model_string)
            tokens[-1] = new_model_name+'.mdl"\n'
            model_string = '/'.join(tokens)
            new_data[i] = '$modelname '+model_string
        if '$body' in x:
            d = x.split()
            d[1] = new_model_name
            d[2] = '"'+new_smd_name+'_mesh.smd"\n'
            new_data[i] = ' '.join(d)
        if '$sequence' in x:
            d = x.split()
            d[2] = '"'+new_smd_name+'_ref.smd"\n'
            new_data[i] = ' '.join(d)
        if '$texturegroup' in x:
            pass
        if '$collisionmodel' in x:
            d = x.split()
            d[1] = '"'+new_smd_name+'_phys.smd"'
            new_data[i] = ' '.join(d)
    return new_data

def getSMDpath(path_to)->dict:
    files = os.listdir(path_to+'/..')
    tokens = path_to.split('/')
    last = tokens[-1].split('\\')[-1]
    target = last.replace('_mesh.smd', '')
    d = dict()
    d['dir'] = path_to.strip(last)
    d['mesh'] = last
    for file in files:
        if target in file:
            if '_phys.smd' == file.replace(target, ''):
                d['phys'] = file
            if '_ref.smd' == file.replace(target, ''):
                d['ref'] = file
    return d

def autoTileFile(newName, qcfpath, basesmdpath, dim, spacing):
    f = open(qcfpath)
    qc_data = f.readlines()
    new_qc_data = modifyQC(qc_data, newName, newName)
    f.close()
    skinlist = getSkinsFromQC(qcfpath)
    newqcpath = re.split('\\\\|/', qcfpath)
    newqcpath[-1] = newName+'.qc'
    target_dir = '/'.join(newqcpath[0:-1])
    newqcpath = '/'.join(newqcpath)

    w_f = open(newqcpath, 'w')
    w_f.write(''.join(new_qc_data))
    w_f.close()

    smd_paths = getSMDpath(basesmdpath)
    for x in smd_paths:
        if x is not 'dir':
            base = SMD.SMD(smd_paths['dir']+smd_paths[x])
            data = genTiledSMD(base, dim, spacing, skinlist)
            data.write_to_file(target_dir + '/' + newName + '_' + x)
            if x is 'mesh' and not smd_paths['ref']:
                new_ref = open(target_dir+'/'+newName+'_ref', 'w')
                new_ref.write(data.getsmdstring())
                new_ref.close()
    autoCompile(newqcpath)
    '''
    cmd = '"'+studiomdlpath+'"'+' -game "'+gamepath+'" -nop4 -r "'+newqcpath+'"'
    print(cmd)
    r_str = subprocess.call(cmd)
    print(r_str)
    '''

def getMeshFromQC(qcpath):
    f = open(qcpath, 'r')
    d = f.readlines()
    f.close()
    for line in d:
        if '$body' in line:
            tokens = line.split()
            return tokens[2].strip('\n').strip('"')

def getMatDirFromQC(qcpath):
    f = open(qcpath, 'r')
    d = f.readlines()
    f.close()
    for line in d:
        if '$cdmaterials' in line:
            tokens = line.split()
            return tokens[1].strip('\n').strip('"')

def getModDirFromQC(qcpath):
    f = open(qcpath, 'r')
    d = f.readlines()
    f.close()
    for line in d:
        if '$modelname' in line:
            tokens = line.split()
            return tokens[1].strip('\n').strip('"')
def getSkinsFromQC(qcpath):
    f = open(qcpath, 'r')
    d = f.readlines()
    f.close()
    reading = False
    lns = list()
    for i in range(len(d)):

        x = d[i]
        if reading:
            lns.append(re.sub('\\n|\\t|{|}| |"', '', x))
        if '$texturegroup' in x:
            reading = True
        if x == '}\n':
            reading = False
    r_list = list(filter(lambda x: x!='',lns))
    return r_list


def compile_from_data(qc: QC, ref_smd: SMD, phys_smd: SMD):
    temp_qc_path = os.getcwd()+"/temp/temp_qc"
    temp_phys_smd = os.getcwd()+"/temp/temp_phys"
    temp_ref_smd = os.getcwd()+"/temp/temp_ref"
    cmd = '"' + studiomdlpath + '"' + ' -game "' + gamepath + '" -nop4 -r "' + temp_qc_path + '"'
    qc.write_to_file(temp_qc_path)
    ref_smd.write_to_file(temp_ref_smd)
    phys_smd.write_to_file(temp_phys_smd)
    print(subprocess.call(cmd))


def autoCompile(qcpath):
    #  we want to copy the material files to the appropriate folder in our game
    cmd = '"' + studiomdlpath + '"' + ' -game "' + gamepath + '" -nop4 -r "' + qcpath + '"'
    print(subprocess.call(cmd))
    parent_dir = '\\'.join(re.split('\\\\|/', qcpath)[0:-1])
    matlist = getSkinsFromQC(qcpath)
    if len(matlist) == 0:
        print("NOTICE: Skin groups not found, defaulting to smd data")
        matlist = SMD.SMD(parent_dir+'\\'+getMeshFromQC(qcpath)).matset
    mat_files = list()
    for x in os.listdir(parent_dir):
        if '.vtf' in x or '.vmt' in x:
            for mat in matlist:
                if mat in x:
                    mat_files.append(x)
                    break
    for file in mat_files:
        shutil.copy(src=parent_dir+'\\'+file, dst=gamepath+'\\materials\\'+getMatDirFromQC(qcpath))
        shutil.copy(src=parent_dir + '\\' + file, dst=parent_dir + '\\merger_ready\\materials\\' + getMatDirFromQC(qcpath))
    moddir = re.split('\\\\|/', getModDirFromQC(qcpath).strip('"').replace('.mdl', ''))
    name = moddir[-1]
    moddir = '/'.join(moddir[0:-1])
    mod_files = list()
    for file in os.listdir(gamepath+'/models/'+moddir):
        if name in file:
            mod_files.append(file)
    for file in mod_files:
        shutil.copy(src=gamepath+'/models/'+moddir+'\\'+file, dst=parent_dir + '\\merger_ready\\models\\'+moddir)


def autoCompileFromMultiple():
    pass


# getSkinsFromQC('C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\facade3.qc')
# autoCompile('C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\facade3.qc')
'''autoTileFile('window06_4x2',
             'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\facade3.qc',
             'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\facade3_mesh.smd',
             (4,2),
             128)'''


def compile_batch(qcname, smdname, modelname):
    autoTileFile(modelname+'_4x2',
                 'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\'+qcname,
                 'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\'+smdname,
                 (4, 2),
                 128)
    autoTileFile(modelname+'_2x2',
                 'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\'+qcname,
                 'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\'+smdname,
                 (2, 2),
                 128)
    autoTileFile(modelname+'_1x2',
                 'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\'+qcname,
                 'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\'+smdname,
                 (1, 2),
                 128)
    autoTileFile(modelname+'_2x1',
                 'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\'+qcname,
                 'C:\\Users\Zackry Finer\Desktop\WIP Folder\Models\map_details\window_facade\\'+smdname,
                 (2, 1),
                 128)

#compile_batch('facade3.qc', 'facade3_mesh.smd', 'window06')

data = vmf_reader.get_batch_points_by_group("gm_ost1.vmf", group_name="Flora Clumped")
d = cluster_objects(data, 4096, 32, 5792)
ref_smd_list, offset_list = generate_smd_for_cluster(d, {'models/ost/fir_tree_4.mdl': 'decomp/fir_tree_4_reference.smd',
                                                         'models/ost/fir_tree_2.mdl': 'decomp/fir_tree_3_reference.smd',
                                                         'models/ost/fir_tree_3.mdl': 'decomp/fir_tree_2_reference.smd',
                                                         'models/ost/fir_tree_1.mdl': 'decomp/fir_tree_1_reference.smd'})
phys_smd_list, _ = generate_smd_for_cluster(d, {'models/ost/fir_tree_4.mdl': 'decomp/fir_tree_4_physics.smd',
                                                         'models/ost/fir_tree_2.mdl': 'decomp/fir_tree_3_physics.smd',
                                                         'models/ost/fir_tree_3.mdl': 'decomp/fir_tree_2_physics.smd',
                                                         'models/ost/fir_tree_1.mdl': 'decomp/fir_tree_1_physics.smd'})
qc_list = [QC() for entry in ref_smd_list]
index = 0
for qc in qc_list:
    qc.modelname = "ost/cluster_"+str(index)+".mdl"
    qc.body["studio_path"] = "temp_ref.smd"
    qc.body["title"] = "cluster"+str(index)
    qc.surfaceprop = "wood"
    qc.cdmaterials.append("models\\ost\\foliage\\")
    qc.sequence[0]["title"] = "idle"
    qc.sequence[0]["studio_path"] = "temp_ref.smd"
    qc.collision_model["studio_path"] = "temp_phys.smd"
    index += 1


compile_from_data(qc_list[8], ref_smd_list[8], phys_smd_list[8])

for i in range(len(offset_list)):
    print("CLUSTER"+str(i)+" ORIGIN:"+str(offset_list[i]))