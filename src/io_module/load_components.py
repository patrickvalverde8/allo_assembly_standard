"""加载构件库 JSON"""
import json
import numpy as np
from typing import Dict
from src.models.components import Component, NodeComponent, RodComponent, PanelComponent, PortDef


def load_components(path: str) -> Dict[str, Component]:
    """
    加载构件库 JSON 文件
    
    Args:
        path: JSON 文件路径
        
    Returns:
        构件 ID 到 Component 对象的映射
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = {}
    
    for comp_data in data.get('components', []):
        comp_id = comp_data['id']
        category = comp_data['category']
        
        if category == 'node':
            component = _load_node_component(comp_data)
        elif category == 'rod':
            component = _load_rod_component(comp_data)
        elif category == 'panel':
            component = _load_panel_component(comp_data)
        else:
            raise ValueError(f"Unknown component category: {category}")
        
        components[comp_id] = component
    
    return components


def _load_node_component(data: Dict) -> NodeComponent:
    """加载节点构件"""
    ports = []
    for port_data in data.get('ports', []):
        port = PortDef(
            id=port_data['id'],
            type=port_data['type'],
            position=np.array(port_data['position']),
            axis=np.array(port_data['axis']),
            compatible_rod=port_data.get('compatible_rod'),
            through=port_data.get('through', False),
            insert_from=port_data.get('insert_from', ["positive", "negative"]),
            max_rods=port_data.get('max_rods', 1),
            occupied_length_mm=port_data.get('occupied_length_mm', 0.0),
            mount_pattern=port_data.get('mount_pattern')
        )
        ports.append(port)
    
    return NodeComponent(
        id=data['id'],
        category='node',
        name=data['name'],
        params=data.get('params', {}),
        local_frame=data.get('local_frame', {}),
        ports=ports
    )


def _load_rod_component(data: Dict) -> RodComponent:
    """加载光轴构件"""
    return RodComponent(
        id=data['id'],
        category='rod',
        name=data['name'],
        params=data.get('params', {}),
        local_frame=data.get('local_frame', {}),
        radius_mm=data.get('radius_mm', 3.0),
        min_length_mm=data.get('min_length_mm', 10.0),
        max_length_mm=data.get('max_length_mm')
    )


def _load_panel_component(data: Dict) -> PanelComponent:
    """加载面板构件"""
    return PanelComponent(
        id=data['id'],
        category='panel',
        name=data['name'],
        params=data.get('params', {}),
        local_frame=data.get('local_frame', {}),
        shape=data.get('shape', 'rect'),
        thickness_mm=data.get('thickness_mm', 3.0)
    )
