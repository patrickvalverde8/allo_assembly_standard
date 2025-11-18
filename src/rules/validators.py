"""装配合法性校验"""
from typing import List, Dict
from collections import defaultdict
from src.models.assembly import Assembly, RodInstance
from src.models.components import PortDef


class ValidationError:
    """校验错误"""
    def __init__(self, message: str, context: Dict = None):
        self.message = message
        self.context = context or {}
    
    def __str__(self):
        return f"ValidationError: {self.message} | Context: {self.context}"


def validate_assembly(assembly: Assembly) -> List[ValidationError]:
    """
    校验装配体合法性
    
    Args:
        assembly: 装配体对象
        
    Returns:
        错误列表（空列表表示通过）
    """
    errors = []
    
    # 检查节点引用
    errors.extend(_validate_node_references(assembly))
    
    # 检查端口兼容性
    errors.extend(_validate_port_compatibility(assembly))
    
    # 检查插入方向
    errors.extend(_validate_insert_direction(assembly))
    
    # 检查端口占用数量
    errors.extend(_validate_port_usage(assembly))
    
    # 检查光轴是否过孔心（新增）
    errors.extend(_validate_rod_alignment(assembly))
    
    return errors


def _validate_node_references(assembly: Assembly) -> List[ValidationError]:
    """检查节点引用是否存在"""
    errors = []
    node_ids = {node.id for node in assembly.nodes}
    
    for rod in assembly.rods:
        if rod.from_end.node not in node_ids:
            errors.append(ValidationError(
                f"Rod references non-existent node",
                {"rod_id": rod.id, "node": rod.from_end.node}
            ))
        if rod.to_end.node not in node_ids:
            errors.append(ValidationError(
                f"Rod references non-existent node",
                {"rod_id": rod.id, "node": rod.to_end.node}
            ))
    
    return errors


def _validate_port_compatibility(assembly: Assembly) -> List[ValidationError]:
    """检查端口类型和兼容性"""
    errors = []
    
    for rod in assembly.rods:
        # 检查 from 端
        from_node = assembly.get_node(rod.from_end.node)
        if from_node:
            from_port = from_node.component.get_port(rod.from_end.port)
            if from_port:
                if from_port.type != "rod_axis":
                    errors.append(ValidationError(
                        f"Port type mismatch: expected rod_axis",
                        {"rod_id": rod.id, "node": from_node.id, "port": from_port.id}
                    ))
                elif from_port.compatible_rod and from_port.compatible_rod != rod.component.id:
                    errors.append(ValidationError(
                        f"Rod not compatible with port",
                        {"rod_id": rod.id, "port": from_port.id, "expected": from_port.compatible_rod}
                    ))
        
        # 检查 to 端
        to_node = assembly.get_node(rod.to_end.node)
        if to_node:
            to_port = to_node.component.get_port(rod.to_end.port)
            if to_port:
                if to_port.type != "rod_axis":
                    errors.append(ValidationError(
                        f"Port type mismatch: expected rod_axis",
                        {"rod_id": rod.id, "node": to_node.id, "port": to_port.id}
                    ))
                elif to_port.compatible_rod and to_port.compatible_rod != rod.component.id:
                    errors.append(ValidationError(
                        f"Rod not compatible with port",
                        {"rod_id": rod.id, "port": to_port.id, "expected": to_port.compatible_rod}
                    ))
    
    return errors


def _validate_insert_direction(assembly: Assembly) -> List[ValidationError]:
    """检查插入方向是否允许"""
    errors = []
    
    for rod in assembly.rods:
        from_node = assembly.get_node(rod.from_end.node)
        if from_node:
            from_port = from_node.component.get_port(rod.from_end.port)
            if from_port and rod.from_end.side not in from_port.insert_from:
                errors.append(ValidationError(
                    f"Insert direction not allowed",
                    {"rod_id": rod.id, "node": from_node.id, "port": from_port.id, 
                     "side": rod.from_end.side, "allowed": from_port.insert_from}
                ))
        
        to_node = assembly.get_node(rod.to_end.node)
        if to_node:
            to_port = to_node.component.get_port(rod.to_end.port)
            if to_port and rod.to_end.side not in to_port.insert_from:
                errors.append(ValidationError(
                    f"Insert direction not allowed",
                    {"rod_id": rod.id, "node": to_node.id, "port": to_port.id,
                     "side": rod.to_end.side, "allowed": to_port.insert_from}
                ))
    
    return errors


def _validate_port_usage(assembly: Assembly) -> List[ValidationError]:
    """检查端口使用数量是否超限"""
    errors = []
    
    # 统计每个端口的使用次数
    port_usage = defaultdict(int)
    
    for rod in assembly.rods:
        port_usage[(rod.from_end.node, rod.from_end.port)] += 1
        port_usage[(rod.to_end.node, rod.to_end.port)] += 1
    
    # 检查是否超过 max_rods
    for (node_id, port_id), count in port_usage.items():
        node = assembly.get_node(node_id)
        if node:
            port = node.component.get_port(port_id)
            if port and count > port.max_rods:
                errors.append(ValidationError(
                    f"Port usage exceeds max_rods limit",
                    {"node": node_id, "port": port_id, "usage": count, "max": port.max_rods}
                ))
    
    return errors



def _validate_rod_alignment(assembly: Assembly) -> List[ValidationError]:
    """检查光轴是否正确穿过孔心"""
    import numpy as np
    from src.geometry.frames import port_world_frame
    
    errors = []
    
    for rod in assembly.rods:
        # 获取两端节点和端口
        from_node = assembly.get_node(rod.from_end.node)
        to_node = assembly.get_node(rod.to_end.node)
        
        if not from_node or not to_node:
            continue
        
        from_port = from_node.component.get_port(rod.from_end.port)
        to_port = to_node.component.get_port(rod.to_end.port)
        
        if not from_port or not to_port:
            continue
        
        # 计算世界坐标系中的端口位置和方向
        from_pos, from_axis = port_world_frame(from_node, from_port)
        to_pos, to_axis = port_world_frame(to_node, to_port)
        
        # 计算光轴向量
        rod_vec = to_pos - from_pos
        rod_length = np.linalg.norm(rod_vec)
        
        if rod_length < 0.001:
            errors.append(ValidationError(
                f"Rod length too short",
                {"rod_id": rod.id, "length": rod_length}
            ))
            continue
        
        rod_dir = rod_vec / rod_length
        
        # 检查 from 端：光轴方向应该与端口轴向一致（或相反）
        from_dot = abs(np.dot(rod_dir, from_axis))
        if from_dot < 0.99:  # 允许小误差
            errors.append(ValidationError(
                f"Rod not aligned with from port axis",
                {"rod_id": rod.id, "from_node": from_node.id, "from_port": from_port.id, 
                 "alignment": from_dot}
            ))
        
        # 检查 to 端：光轴方向应该与端口轴向一致（或相反）
        to_dot = abs(np.dot(rod_dir, to_axis))
        if to_dot < 0.99:  # 允许小误差
            errors.append(ValidationError(
                f"Rod not aligned with to port axis",
                {"rod_id": rod.id, "to_node": to_node.id, "to_port": to_port.id,
                 "alignment": to_dot}
            ))
    
    return errors
