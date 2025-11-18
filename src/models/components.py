"""构件定义数据模型"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
import numpy as np


@dataclass
class PortDef:
    """端口定义"""
    id: str
    type: Literal["rod_axis", "panel_mount"]
    position: np.ndarray  # [x, y, z] 局部坐标
    axis: np.ndarray  # [ax, ay, az] 单位向量
    
    # rod_axis 专用字段
    compatible_rod: Optional[str] = None
    through: bool = False
    insert_from: List[Literal["positive", "negative"]] = field(default_factory=lambda: ["positive", "negative"])
    max_rods: int = 1
    occupied_length_mm: float = 0.0
    
    # panel_mount 专用字段
    mount_pattern: Optional[str] = None


@dataclass
class Component:
    """构件基类"""
    id: str
    category: Literal["node", "rod", "panel"]
    name: str
    params: Dict = field(default_factory=dict)
    local_frame: Dict = field(default_factory=dict)


@dataclass
class NodeComponent(Component):
    """节点构件"""
    ports: List[PortDef] = field(default_factory=list)
    
    def __post_init__(self):
        self.category = "node"
    
    def get_port(self, port_id: str) -> Optional[PortDef]:
        """获取指定端口"""
        for port in self.ports:
            if port.id == port_id:
                return port
        return None


@dataclass
class RodComponent(Component):
    """光轴构件"""
    radius_mm: float = 3.0
    min_length_mm: float = 10.0
    max_length_mm: Optional[float] = None
    
    def __post_init__(self):
        self.category = "rod"


@dataclass
class PanelComponent(Component):
    """面板构件"""
    shape: Literal["rect", "circle"] = "rect"
    thickness_mm: float = 3.0
    
    def __post_init__(self):
        self.category = "panel"
