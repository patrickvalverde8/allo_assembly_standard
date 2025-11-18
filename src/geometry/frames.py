"""坐标系变换"""
import numpy as np
from typing import Tuple
from scipy.spatial.transform import Rotation
from src.models.assembly import NodeInstance
from src.models.components import PortDef


def port_world_frame(node_instance: NodeInstance, port_def: PortDef) -> Tuple[np.ndarray, np.ndarray]:
    """
    计算端口在世界坐标系中的位置和方向
    
    Args:
        node_instance: 节点实例
        port_def: 端口定义
        
    Returns:
        (position, axis) 世界坐标系中的位置和方向向量
    """
    # 创建旋转矩阵（Z-Y-X 欧拉角）
    rotation = Rotation.from_euler('ZYX', node_instance.rotation_deg, degrees=True)
    rot_matrix = rotation.as_matrix()
    
    # 变换端口位置
    local_pos = port_def.position
    world_pos = node_instance.position + rot_matrix @ local_pos
    
    # 变换端口轴向
    local_axis = port_def.axis / np.linalg.norm(port_def.axis)  # 归一化
    world_axis = rot_matrix @ local_axis
    
    return world_pos, world_axis
