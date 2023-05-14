import numpy as np
import open3d as o3d
from time import sleep
import copy
import sys
sys.path.append(sys.path[0]+"/..")
from data_collection_server.db_interface import query_positions_database



def visu_single_shot():
    # obj面片显示
    scene_mesh= o3d.io.read_triangle_mesh('asset/xty.ply')
    print(scene_mesh)
    scene_mesh.compute_vertex_normals()
    o3d.visualization.draw_geometries([scene_mesh], window_name="Open3D1")


    mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1.0)
    mesh_sphere.compute_vertex_normals()
    mesh_sphere.paint_uniform_color([0.1, 0.1, 0.7])

    o3d.visualization.draw_geometries(
        [mesh_sphere, scene_mesh],  window_name="Open3D1")

def visu_update():
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    scene_mesh= o3d.io.read_triangle_mesh('asset/xty.ply')
    scene_mesh.compute_vertex_normals()
    vis.add_geometry(scene_mesh)
    
    mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.1)
    mesh_sphere.compute_vertex_normals()
    mesh_sphere.paint_uniform_color([0.1, 0.1, 0.7])
    
    
    position1 = (-1.273, -2.684, -1.787)
    position2 = (1.0241, -2.7015, -2.45959)
    position3 = (1.642, -2.69, -0.345)
    
    mesh_1 = copy.deepcopy(mesh_sphere).translate(position1)
    mesh_2 = copy.deepcopy(mesh_sphere).translate(position2)
    mesh_3 = copy.deepcopy(mesh_sphere).translate(position3)
    meshes = [mesh_1, mesh_2, mesh_3]
    vis.poll_events()
    vis.update_renderer()
    
    
    for i in range(3):
        sleep(5)
        # vis.update_geometry(scene_mesh)
        vis.add_geometry(meshes[i])
        vis.poll_events()
        vis.update_renderer()
        
    print("Finish loading")

    while (True):
        vis.poll_events()
        vis.update_renderer()
        

    
    vis.destroy_window()

def visu_traj(data):
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    scene_mesh= o3d.io.read_triangle_mesh('asset/xty.ply')
    scene_mesh.compute_vertex_normals()
    vis.add_geometry(scene_mesh)
    
    mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.1)
    mesh_sphere.compute_vertex_normals()
    mesh_sphere.paint_uniform_color([0, 1, 0])
    mesh_sphere2 = o3d.geometry.TriangleMesh.create_sphere(radius=0.1)
    mesh_sphere2.compute_vertex_normals()
    mesh_sphere2.paint_uniform_color([1, 0, 0])
    
    
    position1 = (-1.273, -2.684, -1.787)
    position2 = (1.0241, -2.7015, -2.45959)
    position3 = (1.642, -2.69, -0.345)
    base_position = np.array([1.0241, -2.7015, -2.45959])
    x_axis = np.array(position1) - np.array(position2)
    y_axis = np.array(position3) - np.array(position2)
    z_axis = np.array([0,0.5,0])
    x_axis[1] = y_axis[1] = 0.
    x_axis = x_axis / np.linalg.norm(x_axis)
    y_axis = y_axis / np.linalg.norm(y_axis)
    
    
    
    # import pdb; pdb.set_trace()
    
    
    mesh_1 = copy.deepcopy(mesh_sphere).translate(position1)
    mesh_2 = copy.deepcopy(mesh_sphere).translate(position2)
    mesh_3 = copy.deepcopy(mesh_sphere).translate(position3)
    meshes = [mesh_1, mesh_2, mesh_3]
    vis.poll_events()
    vis.update_renderer()
    
    
    for i in range(3):
        sleep(0.1)
        # vis.update_geometry(scene_mesh)
        vis.add_geometry(meshes[i])
        vis.poll_events()
        vis.update_renderer()
    
    # for i in range(len(data)):
    #     print(i)
    #     # sleep(0.5)
    #     # import pdb; pdb.set_trace()
    #     from time import time
    #     now = time()
    #     while (True):
    #         tmp = time()
    #         if tmp - now > 0.1:
    #             break
    #         vis.poll_events()
    #         # vis.update_renderer()
    #     target_pos = base_position + x_axis*float(data[i]['pos_x']) + z_axis*float(data[i]['pos_z']) + y_axis*float(data[i]['pos_y'])
    #     # target_pos[2] -= 0.2
    #     mesh_now = o3d.geometry.TriangleMesh.create_sphere(radius=0.1)
    #     mesh_now.compute_vertex_normals()
    #     mesh_now.paint_uniform_color(np.array([1, 0, 0])*(i/143) + np.array([0, 0, 1])*(1- i/143))
    #     mesh_now = mesh_now.translate(target_pos)
    #     vis.add_geometry(mesh_now)
    #     vis.poll_events()
    #     vis.update_renderer()
        
        
    print("Finish loading")

    while (True):
        vis.poll_events()
        vis.update_renderer()
        

    
    vis.destroy_window()

target_mac = "b8:14:4d:8a:2d:04"
from datetime import datetime
st = datetime(2023, 5, 7, 11, 53, 00)
et = datetime(2023, 5, 7, 12, 5, 30)
data = query_positions_database(target_mac=target_mac, start_datetime=st, end_datetime=et)

visu_traj(data)



