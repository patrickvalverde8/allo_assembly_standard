"""装配 AST 数据模型"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
import numpy as np
from src.models.components import Component, NodeComponent, RodComponent, PanelComponent


@dataclass
class NodeInstance:
    """节点实例"""
    id: str
    component: NodeComponent
    position: np.ndarray  # [x, y, z] 世界坐标
    rotation_deg: np.ndarray  # [rx, ry, rz] Z-Y-X 欧拉角（度）


@dataclass
class RodEndRef:
    """光轴端点引用"""
    node: str  # 节点实例 ID
    port: str  # 端口 ID
    side: Literal["positive", "negative"]  # 从轴的哪一侧插入


@dataclass
class RodInstance:
    """光轴实例"""
    id: str
    component: RodComponent
    from_end: RodEndRef
    to_end: RodEndRef
    length_override_mm: Optional[float] = None


@dataclass
class RodAttachment:
    """光轴附件（节点挂在光轴中间）"""
    node: str  # 节点实例 ID
    port: str  # 端口 ID
    rod: str  # 光轴实例 ID
    offset_mm: float  # 从 from 端开始的距离


@dataclass
class PanelInstance:
    """面板实例"""
    id: str
    component: PanelComponent
    position: np.ndarray  # [x, y, z]
    normal: np.ndarray  # [nx, ny, nz] 法线方向
    x_dir: np.ndarray  # [xx, xy, xz] 面板局部 X 方向
    size_mm: List[float]  # [width, height] 或 [diameter]
    thickness_mm: Optional[float] = None


@dataclass
class Assembly:
    """装配体"""
    name: str
    unit_mm: float
    nodes: List[NodeInstance] = field(default_factory=list)
    rods: List[RodInstance] = field(default_factory=list)
    panels: List[PanelInstance] = field(default_factory=list)
    rod_attachments: List[RodAttachment] = field(default_factory=list)
    
    def get_node(self, node_id: str) -> Optional[NodeInstance]:
        """获取节点实例"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_rod(self, rod_id: str) -> Optional[RodInstance]:
        """获取光轴实例"""
        for rod in self.rods:
            if rod.id == rod_id:
                return rod
        return None
