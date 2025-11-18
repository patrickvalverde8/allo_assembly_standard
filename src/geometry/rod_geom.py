"""光轴几何生成"""
import cadquery as cq
import numpy as np
from typing import Tuple


def make_rod(start_point: np.ndarray, end_point: np.ndarray, radius_mm: float) -> cq.Workplane:
    """
    生成光轴几何 - 使用 CadQuery 的 polyline 方法
    
    Args:
        start_point: 起点 [x, y, z]
        end_point: 终点 [x, y, z]
        radius_mm: 半径
        
    Returns:
        CadQuery Workplane 对象
    """
    # 计算长度
    vec = end_point - start_point
    length = np.linalg.norm(vec)
    
    if length < 0.001:
        raise ValueError("Rod length too short")
    
    # 使用 CadQuery 的方法：在起点和终点之间创建圆柱
    # 方法：创建一个工作平面，然后沿着两点之间的路径扫掠圆形
    
    # 简单方法：使用两点之间的直线
    start = tuple(start_point)
    end = tuple(end_point)
    
    # 创建圆柱：从起点到终点
    # 使用 CadQuery 的 cylinder 并正确定位
    mid_point = (start_point + end_point) / 2
    
    # 计算方向向量
    direction = vec / length
    
    # 创建沿 Z 轴的圆柱
    rod = cq.Workplane("XY").circle(radius_mm).extrude(length)
    
    # 计算旋转
    z_axis = np.array([0, 0, 1])
    
    if np.allclose(direction, z_axis, atol=0.001):
        # 已经对齐，只需平移
        rod = rod.translate((start[0], start[1], start[2]))
    elif np.allclose(direction, -z_axis, atol=0.001):
        # 反向，旋转 180 度
        rod = rod.rotate((0, 0, 0), (1, 0, 0), 180)
        rod = rod.translate((start[0], start[1], start[2] - length))
    else:
        # 需要旋转
        rotation_axis = np.cross(z_axis, direction)
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
        rotation_angle = np.arccos(np.clip(np.dot(z_axis, direction), -1.0, 1.0)) * 180 / np.pi
        
        # 先旋转，再平移
        rod = rod.rotate((0, 0, 0), tuple(rotation_axis), rotation_angle)
        rod = rod.translate(tuple(start_point))
    
    return rod
