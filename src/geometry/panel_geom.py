"""面板几何生成"""
import cadquery as cq
import numpy as np
from typing import List
from src.models.assembly import PanelInstance


def make_panel(panel: PanelInstance) -> cq.Workplane:
    """
    生成面板几何
    
    Args:
        panel: 面板实例
        
    Returns:
        CadQuery Workplane 对象
    """
    thickness = panel.thickness_mm if panel.thickness_mm else panel.component.thickness_mm
    
    if panel.component.shape == "rect":
        width, height = panel.size_mm[0], panel.size_mm[1]
        # 在 XY 平面创建矩形，从底面开始（position 定义在底面中心）
        panel_wp = (cq.Workplane("XY")
                    .rect(width, height)
                    .extrude(thickness))
        # 向下平移半个厚度，使 position 在底面
        panel_wp = panel_wp.translate((0, 0, -thickness / 2))
    elif panel.component.shape == "circle":
        diameter = panel.size_mm[0]
        panel_wp = (cq.Workplane("XY")
                    .circle(diameter / 2)
                    .extrude(thickness))
        # 向下平移半个厚度，使 position 在底面
        panel_wp = panel_wp.translate((0, 0, -thickness / 2))
    else:
        raise ValueError(f"Unknown panel shape: {panel.component.shape}")
    
    # 计算变换：将 +Z 对齐到 normal
    z_axis = np.array([0, 0, 1])
    normal = panel.normal / np.linalg.norm(panel.normal)
    
    # 计算旋转
    if np.allclose(normal, z_axis):
        rotation_angle = 0
    elif np.allclose(normal, -z_axis):
        rotation_axis = np.array([1, 0, 0])
        rotation_angle = 180
    else:
        rotation_axis = np.cross(z_axis, normal)
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
        rotation_angle = np.arccos(np.dot(z_axis, normal)) * 180 / np.pi
    
    # 应用旋转
    if rotation_angle > 0.001:
        panel_wp = panel_wp.rotate(
            (0, 0, 0),
            tuple(rotation_axis),
            rotation_angle
        )
    
    # 平移到位置
    panel_wp = panel_wp.translate(tuple(panel.position))
    
    return panel_wp
