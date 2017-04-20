import maya.cmds as cmds  
import random  
  
random.seed(1111)  
  
cubeList = cmds.ls('mycube*')  
if len(cubeList)>0:  
    cmds.delete(cubeList)  
  
groupName = cmds.group(em=True,n='groupCube')  
for i in range(0,60):  
    result = cmds.polyCube(w=1,h=1,d=1,n='mycube#')  
    cmds.parent(result,groupName)  
    x = random.uniform(-10,10)  
    y = random.uniform(-10,10)  
    z = random.uniform(-10,10)  
    cmds.move(x,y,z,result)  
      
    xRot = random.uniform(0,180)  
    yRot = random.uniform(0,180)  
    zRot = random.uniform(0,180)  
    cmds.rotate(xRot,yRot,zRot,result)  
      
    scaleFactor = random.uniform(0.8,1.2)  
    cmds.scale(scaleFactor,scaleFactor,scaleFactor,result)  