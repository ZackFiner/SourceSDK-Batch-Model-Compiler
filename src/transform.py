import numpy as np
import math


class quaternion:
    def __init__(self, vec: np.array = None):
        if vec is None:
            self.qx = 0
            self.qy = 0
            self.qz = 0
            self.qw = 0
        else:
            len = np.linalg.norm(vec)
            mult = np.sin(0.5*len)
            vec2 = vec/len
            self.qx = np.cos(0.5*len)
            self.qy = vec2[0]*mult
            self.qz = vec2[1]*mult
            self.qw = vec2[2]*mult

    def conjugate(self):
        return_quat = quaternion()
        return_quat.qx = self.qx
        return_quat.qy = -self.qy
        return_quat.qz = -self.qz
        return_quat.qw = -self.qw
        return return_quat

    def __mul__(self, o):
        if isinstance(o, type(self)):
            return_q = quaternion()
            return_q.qx = o.qx*self.qx - o.qy*self.qy - o.qz*self.qz - o.qw*self.qw
            return_q.qy = o.qx*self.qy + o.qy*self.qx - o.qz*self.qw + o.qw*self.qz
            return_q.qz = o.qx*self.qz + o.qy*self.qw + o.qz*self.qx - o.qw*self.qy
            return_q.qw = o.qx*self.qw - o.qy*self.qz + o.qz*self.qy + o.qw*self.qx
            return return_q
        elif isinstance(o, np.ndarray):
            euler_param = quaternion()
            euler_param.qx = 0
            euler_param.qy = o[0]
            euler_param.qz = o[1]
            euler_param.qw = o[2]
            return self*euler_param  # don't we need a conjugate here?

    def getEulerParam(self):
        return np.array([self.qy, self.qz, self.qw])

def genRotMat(angles):
    rx = np.deg2rad(angles[2])
    ry = np.deg2rad(angles[0])
    rz = np.deg2rad(angles[1])
    mx = np.array([[1, 0, 0],
                   [0, np.cos(rx), np.sin(rx)],
                   [0, -np.sin(rx), np.cos(rx)]])

    my = np.array([[np.cos(ry), 0, np.sin(ry)],
                   [0, 1, 0],
                   [-np.sin(ry), 0, np.cos(ry)]])

    mz = np.array([[np.cos(rz), np.sin(rz), 0],
                   [-np.sin(rz), np.cos(rz), 0],
                   [0, 0, 1]])

    return np.dot(mz, np.dot(mx, my))

def rotVec(vec, axes, ang):
    rotQ = quaternion(axes*math.radians(ang))
    newQ = rotQ*vec*rotQ.conjugate()
    return newQ.getEulerParam()

'''
d = genRotMat(np.array([0,0,0]))
mult = np.dot(np.array([0,1,0]), d)
print(mult)
'''
