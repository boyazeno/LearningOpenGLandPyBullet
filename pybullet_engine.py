import pybullet as p
import numpy as np
import os
import time
from collada import Collada
from stl import mesh
import pywavefront as w
from openGL import Utility



class MyWorld(object):
    def __init__(self,scale=5000):
        self.scale = scale
        self.rootPath = os.path.dirname(os.path.abspath(__file__))
        p.connect(p.GUI)#SHARED_MEMORY
        p.setPhysicsEngineParameter(collisionFilterMode=1)
        p.createCollisionShape(p.GEOM_PLANE)
        p.createMultiBody(0, 0)
        p.setGravity(0, 0, -10)

        #p.setRealTimeSimulation(1)
        self.id = None
        self.__shapeDataList = {}
        self.__objectDataList = {}
        self.init()


    def init(self,file : str="/home/boya/workspace/RL_pytorch/app/resource/model/urdf/model.urdf"):
        if self.id!=None:
            p.removeBody(self.id)
        self.__loadRobot(file)
        self.__shapeDataList.clear()
        self.__loadMesh()
        print("[Finished loading!]")
        self.poses = {}
        self.objectPoseList = {}


    def move(self,vel):
        if self.id==None:
            return
        numJoints = p.getNumJoints(self.id)
        #for joint in range(numJoints):
        #    print(p.getJointInfo(self.id, joint))
        maxForce = 100  # Newton
        p.setJointMotorControlArray(self.id, jointIndices=[1, 2, 3, 4, 5, 6], controlMode=p.VELOCITY_CONTROL,
                                    targetVelocities=[*vel], forces=[maxForce] * 6)

    def __loadRobot(self,path):
        self.id = p.loadURDF(path,flags=(p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT+p.URDF_USE_SELF_COLLISION))

    # load mesh data from file name for each link
    def __loadMesh(self):
        self.shapeFileList = {}
        for shapedata in p.getVisualShapeData(self.id):
            self.shapeFileList[shapedata[1]] = shapedata[4].decode("utf-8")
        self.__shapeDataList.clear()
        for idx, name in self.shapeFileList.items():
            if name.split(".")[-1] == "stl":
                m = mesh.Mesh.from_file(name)
                print(f"Get {name} points: {len(m.points)}")
                self.__shapeDataList[idx] = []
                points = m.vectors.reshape(m.vectors.size // 3, 3)
                pointsUnique = np.unique(points, axis=0).tolist()
                points = points.tolist()
                indexArray = []
                for pt in points:
                    indexArray.append(pointsUnique.index(pt))
                self.__shapeDataList[idx].append([m.vectors.shape[0],np.array(pointsUnique,dtype=np.float32),np.array(indexArray,np.int32),m.normals])
                #TODO have to fix the vertex and normal stack together.

            elif name.split(".")[-1] == "dae":
                m = Collada(name)
                print(f"Get {name} geometry: {len(m.geometries)}")
                self.__shapeDataList[idx] = []
                for geom in m.geometries:
                    for prim in geom.primitives:
                        prim_type = type(prim).__name__
                        if prim_type == 'BoundTriangleSet':
                            triangles = prim
                        elif prim_type == 'TriangleSet':
                            triangles = prim
                        elif prim_type == 'BoundPolylist':
                            triangles = prim.triangleset()
                        else:
                            print('Unsupported mesh used:', prim_type)
                            triangles = None

                        if triangles is not None:
                            triangles.generateNormals()
                            # We will need flat lists for VBO (batch) initialization
                            if "dae_rg2_" in name:
                                vertices = np.hstack([triangles.vertex,triangles.normal]).flatten()
                            else:
                                vertices = np.hstack([triangles.vertex*self.scale, triangles.normal]).flatten()
                            batch_len = len(vertices) // 3
                            indices = triangles.vertex_index.flatten()
                            self.__shapeDataList[idx].append([batch_len, vertices, indices])

    def getPose(self):
        if self.id==None: # if no robot loaded, do nothing
            return {}
        data = p.getLinkStates(self.id,list(self.__shapeDataList.keys()),computeForwardKinematics=0)
        keys = list(self.__shapeDataList.keys())
        poses = {keys[i]:Utility.matAffine(np.array(p.getMatrixFromQuaternion(data[i][5])).reshape(3,3),vec=np.array(data[i][4])*self.scale) for i in range(len(data))}

        # Get pose of collision object
        for key in self.__objectDataList.keys():
            pose = p.getBasePositionAndOrientation(self.__objectDataList[key][-2])
            orientation = p.getMatrixFromQuaternion(pose[1])
            self.objectPoseList[key] = Utility.matAffine(np.array(orientation).reshape(3,3),vec=np.array(pose[0])*self.scale)

        return poses

    def loadObject(self,fileName:str, position:tuple=(0.,0.,0.), orientation:tuple=(0.,0.,0.), mess:float=1.0, static=False, scale=1.0):
        idx = list(self.__objectDataList.keys())[-1]+1 if len(self.__objectDataList)!=0 else 0
        # load mesh for GUI
        if fileName.split(".")[-1] == "stl":
            m = mesh.Mesh.from_file(fileName)
            print(f"Get {fileName} points: {len(m.points)}")
            self.__objectDataList[idx] = []
            points = m.vectors.reshape(m.vectors.size // 3, 3)
            normalDict = {}
            for i, point in enumerate(points.tolist()):
                tp = tuple(point)
                if tp in  normalDict:
                    normalDict[tp].append(i//3)
                else:
                    normalDict[tp] = [i//3]

            pointsUnique = (np.unique(points, axis=0) * scale).tolist()
            points = points.tolist()
            indexArray = []
            vertexArray = []
            for pt in points:
                indexArray.append(pointsUnique.index(pt))
            pointsUnique = [point + list(np.average(m.normals[normalDict[tuple(points[0])],:],axis=0)) for point in pointsUnique]
            self.__objectDataList[idx]=[m.vectors.shape[0], np.array(pointsUnique, dtype=np.float32).flatten(), np.array(indexArray, np.int32)]
            # TODO have to fix the vertex and normal stack together.

        elif fileName.split(".")[-1] == "dae":
            m = Collada(fileName)
            print(f"Get {fileName} geometry: {len(m.geometries)}")
            self.__objectDataList[idx] = []
            for geom in m.geometries:
                for prim in geom.primitives:
                    prim_type = type(prim).__name__
                    if prim_type == 'BoundTriangleSet':
                        triangles = prim
                    elif prim_type == 'TriangleSet':
                        triangles = prim
                    elif prim_type == 'BoundPolylist':
                        triangles = prim.triangleset()
                    else:
                        print('Unsupported mesh used:', prim_type)
                        triangles = None

                    if triangles is not None:
                        triangles.generateNormals()
                        # We will need flat lists for VBO (batch) initialization
                        vertices = np.hstack([triangles.vertex * scale, triangles.normal]).flatten()
                        batch_len = len(vertices) // 3
                        indices = triangles.vertex_index.flatten()
                        self.__objectDataList[idx] = [batch_len, vertices, indices]

        elif fileName.split(".")[-1] == "obj":
            m = w.Wavefront(fileName, collect_faces=True)
            self.__objectDataList[idx] = []
            for primitive in m.mesh_list:
                for material in primitive.materials:
                    # get total size of each point, last 6 is normals and vertices
                    pointSize = 0
                    for fmt in material.vertex_format.split("_"):
                        pointSize += int(fmt[1])
                    if pointSize<6:
                        raise ValueError(f"Require point size larger than 6, get {pointSize} instead!")
                    v = np.array(material.vertices).reshape(-1,pointSize)
                    vertexSet = set([tuple(vertex) for vertex in v.tolist()])
                    normalDict = { tuple(vertex[-3:]):tuple(vertex[-6:-3]) for vertex in vertexSet}
                    vertexList = [list(vertex) + list(normalDict[vertex]) for vertex in m.vertices]
                    vertexList = np.array(vertexList,dtype=np.float32)
                    vertexList[:,:3] *= scale
                    vertexList = vertexList.flatten()
                    batch_len = len(vertexList) // 6
                    indices = np.array(primitive.faces,dtype=np.int32).flatten()
                    self.__objectDataList[idx] = [batch_len, vertexList, indices]

        else:
            raise TypeError(f"Mesh type not supported, currently only .stl, .dae and .obj (as collision object).")

        # load object for simulation
        if fileName.split(".")[-1] == "obj":
            meshID = p.createCollisionShape(p.GEOM_MESH, fileName=fileName, meshScale=[0.1]*3)
            if meshID == -1:
                raise IOError(f"Mesh file could not be loaded!")
            shapeID = p.createVisualShape(p.GEOM_MESH, fileName=fileName, meshScale=[0.1]*3)

            objectID = p.createMultiBody(baseMass=mess if not static else 0., baseCollisionShapeIndex=meshID,
                                         baseVisualShapeIndex=shapeID, basePosition=position,
                                         baseOrientation=p.getQuaternionFromEuler(orientation))
            self.__objectDataList[idx].extend([meshID, objectID, fileName.split(".")[0]])
        else:
            meshID = p.createCollisionShape(p.GEOM_MESH, vertices=self.__objectDataList[idx][1][:,0:3].tolist(),
                                            indices=self.__objectDataList[idx][2].tolist())
            shapeID = p.createVisualShape(p.GEOM_MESH, vertices=self.__objectDataList[idx][1][:,0:3].tolist(),
                                          indices=self.__objectDataList[idx][2].tolist())

            if meshID == -1:
                raise IOError(f"Mesh file could not be loaded!")

            # build multi body from mesh
            objectID = p.createMultiBody(baseMass=mess if not static else 0., baseCollisionShapeIndex=meshID,
                                         baseVisualShapeIndex=shapeID, basePosition=position,
                                         baseOrientation=p.getQuaternionFromEuler(orientation))
            p.changeDynamics(objectID, -1, spinningFriction=0.001, rollingFriction=0.001, linearDamping=0.0)

            self.__objectDataList[idx].extend([meshID, objectID, fileName.split(".")[0]])
        pose = p.getBasePositionAndOrientation(objectID)
        orientation = p.getMatrixFromQuaternion(pose[1])
        self.objectPoseList[idx] = Utility.matAffine(np.array(orientation).reshape(3, 3), vec=np.array(pose[0]))
        return idx


    def __buildObject(self):
        sphereRadius = 0.05
        colSphereId = p.createCollisionShape(p.GEOM_SPHERE, radius=sphereRadius)
        colBoxId = p.createCollisionShape(p.GEOM_BOX, halfExtents=[sphereRadius, sphereRadius, sphereRadius])
        return [colSphereId,colBoxId]


    def __setObjectPose(self, idx:int, position:tuple=(0.,0.,0.), orientation:tuple=(0.,0.,0.)):
        p.resetBasePositionAndOrientation(self.__objectDataList[idx][4], position, p.getQuaternionFromEuler(orientation))
        objectID = self.__objectDataList[idx][-2]
        pose = p.getBasePositionAndOrientation(objectID)
        orientation = p.getMatrixFromQuaternion(pose[1])
        self.objectPoseList[idx] =  Utility.matAffine(np.array(orientation).reshape(3, 3), vec=np.array(pose[0])*self.scale)

    def setObjectPose(self,idx, poses, angles):
        if type(idx)!=int:
            for i, pose, angle in zip(idx, poses,angles):
                npose = tuple([i * self.scale for i in pose])
                self.__setObjectPose(i, npose, angle)
        else:
            npose = tuple([i * self.scale for i in poses])
            self.__setObjectPose(idx, npose, angles)


    def step(self, t=0.01):
        p.stepSimulation()
        self.poses = self.getPose()
        #time.sleep(t)

    @property
    def shapeDataList(self):
        return self.__shapeDataList

    @property
    def objectDataList(self):
        return self.__objectDataList

    def collisionFilter(self):
        #p.setCollisionFilterPair(0,)
        pass

    def removeObject(self,idx):
        if idx in self.__objectDataList:
            del self.__objectDataList[idx]
            del self.objectPoseList[idx]
        else:
            raise ValueError(f"No idx {idx} in object dict!")


if __name__=="__main__":
    a=MyWorld()
    a.move([0.,0.5,0.,0.,0.,0.5])
    #a.loadObject("/home/boya/ros_ws/src/ur5_test/collision_objects/box.stl",(0.0,1., 0.2),static=False)
    a.loadObject("/home/boya/workspace/RL_pytorch/app/resource/model/meshes/object/box.obj", (0.0,1.,1.),scale=0.1)
    a.loadObject("/home/boya/workspace/RL_pytorch/app/resource/model/meshes/object/box.obj", (0.0, 1.5, 1.),scale=0.1)
    #for i in range(10000):

    a.step()
    time.sleep(1)
    for i in range(10000):
        a.step()
        time.sleep(0.01)