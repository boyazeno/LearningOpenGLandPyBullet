# LearningOpenGLandPyBullet
使用pyOpenGL，pyQt5以及PyBullet完成一简单机器人读取加载仿真程序

## 使用
* `/openGL`：

  文件夹中存放openGL相关的类，包括抽象出来的index buffer， vertex buffer， shader，renderer，texture。
* `/resource/model`：

  文件夹中存放机器人model相关文件，包括urdf，mesh file， 可以加在的物体mesh
* `/resource` ：

  文件夹中还存放有编写好的shader文件两个，其中`shader.shader`是包含texture的，而`shader_simple.shader`是包含光照的

* `app.py`：

  此文件为一详细注释的PyQt5小程序样例。可用于学习使用PyQt5
  
* `DragAndDrop.py`,`ex.py`,`ex_gl.py`：
 
   均为PyQt5样例程序。其中第一个实现了拖拽功能。第二个为Qt5+openGL最小实现。第三个为一可动的Qt5+openGL程序，包括了视角移动。
   
 * `opengl_example_element_array_buffer.py`:
   
    为加载机器人到pybullet环境中的主程序。实现了将qt5以及openGL联动，并实现了openGL显示pybullet仿真内容，以及使用qt5按钮控制仿真的部分功能。
    
    **Bug：现阶段如果想要正常读入机器人model，需要在主程序开始前就将model加载。或者使用SHARED_MEMORY方式打开pybullet（具体实施需要到bullet安装文件夹中找到`bullet3/build/examples/SharedMemory/App_PhysicsServer_SharedMemory`，运行此app，就可以使用pybullet中的SHARED_MEMORY功能）。但是动态加载collision物体仍然会出现显示错误的问题，如果在GUI程序开始前加载则没有问题（至少说明opengl部分是对的）**
    
  * `pybullet_engine.py`：
    
      pybullet相关类，包括加载机器人，更新位置信息等。
