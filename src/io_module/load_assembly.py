"""加载装配 AST JSON"""
import json
import numpy as np
from typing import Dict
from src.models.components import Component
from src.models.assembly import (
    Assembly, NodeInstance, RodInstance, RodEndRef, 
    PanelInstance, RodAttachment
)


def load_assembly(path: str, components_map: Dict[str, Component]) -> Assembly:
    """
    加载装配 JSON 文件
    
    Args:
        path: JSON 文件路径
        components_map: 构件库映射
        
    Returns:
        Assembly 对象
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assembly = Assembly(
        name=data['name'],
        unit_mm=data.get('unit_mm', 1.0)
    )
    
    # 加载节点实例
    for node_data in data.get('nodes', []):
        comp = components_map.get(node_data['component_id'])
        if comp is None or comp.category != 'node':
            raise ValueError(f"Node component not found: {node_data['component_id']}")
        
        node = NodeInstance(
            id=node_data['id'],
            component=comp,
            position=np.array(node_data['position']),
            rotation_deg=np.array(node_data.get('rotation_deg', [0, 0, 0]))
        )
        assembly.nodes.append(node)
    
    # 加载光轴实例
    for rod_data in data.get('rods', []):
        comp = components_map.get(rod_data['component_id'])
        if comp is None or comp.category != 'rod':
            raise ValueError(f"Rod component not found: {rod_data['component_id']}")
        
        from_data = rod_data['from']
        to_data = rod_data['to']
        
        rod = RodInstance(
            id=rod_data['id'],
            component=comp,
            from_end=RodEndRef(
                node=from_data['node'],
                port=from_data['port'],
                side=from_data['side']
            ),
            to_end=RodEndRef(
                node=to_data['node'],
                port=to_data['port'],
                side=to_data['side']
            ),
            length_override_mm=rod_data.get('length_override_mm')
        )
        assembly.rods.append(rod)
    
    # 加载面板实例
    for panel_data in data.get('panels', []):
        comp = components_map.get(panel_data['component_id'])
        if comp is None or comp.category != 'panel':
            raise ValueError(f"Panel component not found: {panel_data['component_id']}")
        
        panel = PanelInstance(
            id=panel_data['id'],
            component=comp,
            position=np.array(panel_data['position']),
            normal=np.array(panel_data['normal']),
            x_dir=np.array(panel_data['x_dir']),
            size_mm=panel_data['size_mm'],
            thickness_mm=panel_data.get('thickness_mm')
        )
        assembly.panels.append(panel)
    
    # 加载光轴附件
    for attach_data in data.get('rod_attachments', []):
        attachment = RodAttachment(
            node=attach_data['node'],
            port=attach_data['port'],
            rod=attach_data['rod'],
            offset_mm=attach_data['offset_mm']
        )
        assembly.rod_attachments.append(attachment)
    
    return assembly
