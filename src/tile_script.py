from .SMD import SMD, VertexData, TriangleData, TimeFrame, replacemat
import random
import numpy as np

def genTiledSMD(base:SMD, tileDim:tuple, spacing, skinlist=None):
    #  we want to create a new SMD
    r_smd = SMD()
    w,h = tileDim
    for i in range(w):
        for j in range(h):
            add_vec = np.array([0, i*spacing, j*spacing])
            newtries = [c + add_vec for c in base.triangles]
            if skinlist is not None:
                replacemat(newtries, newtries[0].matName, random.choice(skinlist))
            r_smd.triangles.extend(newtries)

    for tri in r_smd.triangles:  # now, we re-center our objects
        add_vec = np.array([0,-(w-1)*spacing/2, -h*spacing/2])
        tri.translate(add_vec)
    r_smd.sequence = base.sequence  # shallow copy
    r_smd.nodes = base.nodes
    return r_smd


def instanceSMD(base:SMD, instance_data:list, skinlist=None):
    r_smd = SMD()
    x_c = instance_data[0]
    y_c = instance_data[1]
    z_c = instance_data[2]
    x_d = instance_data[3]
    y_d = instance_data[4]
    z_d = instance_data[5]

    for i in range(x_c):
        for j in range(y_c):
            for k in range(z_c):
                add_vec = np.array([i*x_d, j*y_d, k*z_d])
                newtries = [c + add_vec for c in base.triangles]
                if skinlist is not None:
                    replacemat(newtries, newtries[0].matName, random.choice(skinlist))
                r_smd.triangles.extend(newtries)
    correction = np.array([-(x_c - 1) * x_d / 2, -(y_c - 1) * y_d / 2, -z_c * z_d / 2])
    for tri in r_smd.triangles:
        tri.translate(correction)

    r_smd.sequence = base.sequence  # shallow copy
    r_smd.nodes = base.nodes
    return r_smd


#tiled = genTiledSMD(SMD('facade2_mesh.smd'), (4,4), 128)

#print(len(tiled.triangles))