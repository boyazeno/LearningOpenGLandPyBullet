import pybullet as p
import time
import math
import pybullet_data

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
#don't create a ground plane, to allow for gaps etc
p.resetSimulation()
#p.createCollisionShape(p.GEOM_PLANE)
#p.createMultiBody(0,0)
#p.resetDebugVisualizerCamera(5,75,-26,[0,0,1]);
p.resetDebugVisualizerCamera(15, -346, -16, [-15, 0, 1])

p.configureDebugVisualizer(p.COV_ENABLE_RENDERING, 0)

sphereRadius = 0.05
colSphereId = p.createCollisionShape(p.GEOM_SPHERE, radius=sphereRadius)

#a few different ways to create a mesh:

vertices = [[-0.246350, -0.246483, -0.000624], [-0.151407, -0.176325, 0.172867],
            [-0.246350, 0.249205, -0.000624], [-0.151407, 0.129477, 0.172867],
            [0.249338, -0.246483, -0.000624], [0.154395, -0.176325, 0.172867],
            [0.249338, 0.249205, -0.000624], [0.154395, 0.129477, 0.172867]]
indices = [
    0, 3, 2, 3, 6, 2, 7, 4, 6, 5, 0, 4, 6, 0, 2, 3, 5, 7, 0, 1, 3, 3, 7, 6, 7, 5, 4, 5, 1, 0, 6, 4,
    0, 3, 1, 5
]
#convex mesh from obj
stoneId = p.createCollisionShape(p.GEOM_MESH, vertices=vertices, indices=indices)

boxHalfLength = 0.5
boxHalfWidth = 2.5
boxHalfHeight = 0.1
segmentLength = 5

colBoxId = p.createCollisionShape(p.GEOM_BOX,
                                  halfExtents=[boxHalfLength, boxHalfWidth, boxHalfHeight])

mass = 1
visualShapeId = -1

segmentStart = 0

objID = None
for i in range(segmentLength):
  p.createMultiBody(baseMass=0,
                    baseCollisionShapeIndex=colBoxId,
                    basePosition=[segmentStart, 0, -0.1])
  width = 4
  for j in range(width):
    objID=p.createMultiBody(baseMass=0,
                      baseCollisionShapeIndex=stoneId,
                      basePosition=[segmentStart, 0.5 * (i % 2) + j - width / 2., 0])
  segmentStart = segmentStart - 1

import numpy as np
pose=p.getBasePositionAndOrientation(objID)
print(np.array(p.getMatrixFromQuaternion(pose[1])).reshape(3,3))

p.configureDebugVisualizer(p.COV_ENABLE_RENDERING, 1)
while (1):
  camData = p.getDebugVisualizerCamera()
  viewMat = camData[2]
  projMat = camData[3]
  p.getCameraImage(256,
                   256,
                   viewMatrix=viewMat,
                   projectionMatrix=projMat,
                   renderer=p.ER_BULLET_HARDWARE_OPENGL)
  keys = p.getKeyboardEvents()
  p.stepSimulation()
  #print(keys)
  time.sleep(0.01)