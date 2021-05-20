import OpenGL.GL as gl

class VertexArrayElement(object):
    sizeMap = {gl.GL_FLOAT:        4,
               gl.GL_UNSIGNED_INT: 4,
               gl.GL_UNSIGNED_BYTE:4}

    def __init__(self,type, count, normalized=False):
        self.type=type
        self.count=count
        self.normalized=gl.GL_TRUE if normalized else gl.GL_FALSE

    @classmethod
    def getSizeOfType(cls,type):
        if type not in cls.sizeMap.keys():
            raise TypeError(f"Cannot find the type {repr(type)}")
        return cls.sizeMap[type]


class VertexArrayLayout(object):
    def __init__(self):
        self.__elements = []
        self.__stride = 0

    def push(self, type, count):
        self.__elements.append(VertexArrayElement(type, count, False))
        self.__stride += VertexArrayElement.getSizeOfType(type)*count

    @property
    def elements(self):
        return self.__elements

    @property
    def stride(self):
        return self.__stride