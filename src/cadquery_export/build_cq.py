"""构建 CadQuery Assembly"""
import cadquery as cq
import numpy as np
from typing import Dict
from scipy.spatial.transform import Rotation

from src.models.assembly import Assembly
from src.models.components import Component
from src.geometry.frames import port_world_frame
from src.geometry.rod_geom import make_rod
from src.geometry.panel_geom import make_panel


def build_cadquery_assembly(assembly: Assembly, components_map: Dict[str, Component]) -> cq.Assembly:
    """
    构建 CadQuery Assembly
    
    Args:
        assembly: 装配体对象
        components_map: 构件库映射
        
    Returns:
        CadQuery Assembly 对象
    """
    assy = cq.Assembly()
    
    # 添加节点
    for node in assembly.nodes:
        node_geom = _build_node(node)
        if node_geom:
            # 创建位置变换
            loc = _create_location(node.position, node.rotation_deg)
            assy.add(node_geom, name=node.id, loc=loc)
    
    # 添加光轴
    for rod in assembly.rods:
        rod_geom = _build_rod(rod, assembly)
        if rod_geom:
            assy.add(rod_geom, name=rod.id)
    
    # 添加面板
    for panel in assembly.panels:
        panel_geom = make_panel(panel)
        if panel_geom:
            assy.add(panel_geom, name=panel.id)
    
    return assy


def _build_node(node) -> cq.Workplane:
    """构建节点几何 - 从 STEP 文件加载"""
    import os
    
    # 尝试 .step 和 .stp 两种扩展名
    step_file = f"nodes/{node.component.id}.step"
    stp_file = f"nodes/{node.component.id}.stp"
    
    if os.path.exists(step_file):
        try:
            imported = cq.importers.importStep(step_file)
            return imported
        except Exception as e:
            print(f"警告: 无法加载 {step_file}: {e}")
    elif os.path.exists(stp_file):
        try:
            imported = cq.importers.importStep(stp_file)
            return imported
        except Exception as e:
            print(f"警告: 无法加载 {stp_file}: {e}")
    
    # 如果没有 STEP 文件，返回简单占位
    print(f"警告: 未找到 {node.component.id} 的 STEP 文件")
    return cq.Workplane("XY").box(10, 10, 10)


def _build_rod(rod, assembly: Assembly) -> cq.Workplane:
    """构建光轴几何"""
    # 获取两端节点
    from_node = assembly.get_node(rod.from_end.node)
    to_node = assembly.get_node(rod.to_end.node)
    
    if not from_node or not to_node:
        return None
    
    # 获取端口
    from_port = from_node.component.get_port(rod.from_end.port)
    to_port = to_node.component.get_port(rod.to_end.port)
    
    if not from_port or not to_port:
        return None
    
    # 计算世界坐标系中的端口位置
    from_pos, from_axis = port_world_frame(from_node, from_port)
    to_pos, to_axis = port_world_frame(to_node, to_port)
    
    # 根据 side 调整起点
    if rod.from_end.side == "positive":
        start_point = from_pos + from_axis * from_port.occupied_length_mm
    else:
        start_point = from_pos - from_axis * from_port.occupied_length_mm
    
    if rod.to_end.side == "positive":
        end_point = to_pos + to_axis * to_port.occupied_length_mm
    else:
        end_point = to_pos - to_axis * to_port.occupied_length_mm
    
    # 生成光轴
    return make_rod(start_point, end_point, rod.component.radius_mm)


def _create_location(position: np.ndarray, rotation_deg: np.ndarray) -> cq.Location:
    """创建 CadQuery Location"""
    # 旋转（Z-Y-X 欧拉角）
    rot = Rotation.from_euler('ZYX', rotation_deg, degrees=True)
    rot_matrix = rot.as_matrix()
    
    # CadQuery 使用 (center, x_dir, z_dir) 或直接用 matrix
    loc = cq.Location(cq.Vector(*position))
    
    # 应用旋转（简化处理）
    if not np.allclose(rotation_deg, [0, 0, 0]):
        # 使用欧拉角逐步旋转，确保转换为 float
        loc = loc * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), float(rotation_deg[0]))
        loc = loc * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), float(rotation_deg[1]))
        loc = loc * cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), float(rotation_deg[2]))
    
    return loc
