import numpy as np
from enum import Enum

Axis = Enum('Axis',("x","y","z"))

def vecTranslation(x=0., y=0., z=0.):
    return np.array([x,y,z,1.])


def matTranslation(x=0., y=0., z=0., vec=None):
    data = np.eye(4)
    if isinstance(vec, np.ndarray):
        data[0:3,3] = vec[0:3]
    else:
        data[0:3,3] = [x,y,z]
    return data


def matRotationX(angle):
    data = np.eye(4)
    data[1, 1] = np.cos(angle)
    data[2, 2] = np.cos(angle)
    data[1, 2] = -1 * np.sin(angle)
    data[2, 1] = np.sin(angle)
    return data


def  matRotationY(angle):
    data = np.eye(4)
    data[0, 0] = np.cos(angle)
    data[0, 2] = np.sin(angle)
    data[2, 0] = -1 * np.sin(angle)
    data[2, 2] = np.cos(angle)
    return data


def matRotationZ(angle):
    data = np.eye(4)
    data[0, 0] = np.cos(angle)
    data[0, 1] = -1 * np.sin(angle)
    data[1, 0] = np.sin(angle)
    data[1, 1] = np.cos(angle)
    return data


def matRotation(val,comb:str,rpy=True):
    if len(val)!= len(comb):
        raise TypeError(f"[Type Error]: Should give data with same length! Get {(len(val),len(comb))}.")
    data = np.eye(4)
    rotationMap = {"x": matRotationX, "y": matRotationY, "z": matRotationZ}
    if rpy:
        for v, axis in zip(val,comb):
            data=rotationMap[axis](v).dot(data)
    else:
        for v, axis in zip(val,comb):
            data=data.dot(rotationMap[axis](v))
    return data


def matOrtho(left,right,bottom,top,zNear,zFar):
    mvp = np.eye(4)
    mvp[1,1] = 2. / (top - bottom)
    mvp[2,2] = - 2. / (zFar - zNear)
    mvp[0,0] = 2. / (right - left)
    mvp[3,0] = - (right + left) / (right - left)
    mvp[3,1] = - (top + bottom) / (top - bottom)
    mvp[3,2] = - (zFar + zNear) / (zFar - zNear)
    return mvp

def matPersp(left,right,bottom,top,zNear,zFar):

    mvp = np.eye(4)
    mvp[0,0] = 2.*zNear/(right-left)
    mvp[2,0] = (right+left)/(right-left)
    mvp[1,1] = 2.*zNear/(top-bottom)
    mvp[2,1] = (top+bottom)/(top-bottom)
    mvp[2,2] = -1.*(zFar+zNear)/(zFar-zNear)
    mvp[2,3] = -1.0
    mvp[3,3] = 0.0
    mvp[3,2] = -2.*zFar*zNear/(zFar-zNear)
    return mvp.T


def translate(mat,trans,local=True):
    if len(trans.shape)==1:
        if local:
            return mat.dot(matTranslation(vec=trans))
        else:
            return matTranslation(vec=trans).dot(mat)
    else:
        if local:
            return mat.dot(trans)
        else:
            return trans.dot(mat)


def rotate(mat, rot, rpy=True):
    if type(rot)==tuple or len(rot.shape)==1:
        if rpy:
            rotMat = matRotationX(rot[0]).dot(mat)
            rotMat = matRotationY(rot[1]).dot(rotMat)
            rotMat = matRotationZ(rot[2]).dot(rotMat)
        else:
            rotMat = mat.dot(matRotationX(rot[0]))
            rotMat = rotMat.dot(matRotationY(rot[1]))
            rotMat = rotMat.dot(matRotationZ(rot[2]))
        return rotMat
    elif len(rot.shape)==2:
        if rot.shape[0]==4:
            return mat.dot(rot)
        else:
            rotMat = np.eye(4)
            rotMat[0:3,0:3] = rot
            return mat.dot(rotMat)

    else:
        raise TypeError(f"[Type Error]: Need list input or matrix input! Get {rot}, need list or mat4*4.")


def matAffine(rot, rpy=True,x=0., y=0., z=0., vec=None):
    data = np.eye(4)
    data = translate(data, matTranslation(x, y, z, vec))
    data = rotate(data,rot,rpy)
    return data


