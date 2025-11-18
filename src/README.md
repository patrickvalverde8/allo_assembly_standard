# 源代码说明

本目录包含系统的核心代码。

## 目录结构

```
src/
├── cadquery_export/    # CadQuery 模型生成和导出
│   └── build_cq.py     # 主要的模型构建逻辑
│
├── geometry/           # 几何计算
│   ├── frames.py       # 坐标系变换
│   ├── panel_geom.py   # 面板几何生成
│   └── rod_geom.py     # 光轴几何生成
│
├── io_module/          # JSON 文件加载
│   ├── load_assembly.py    # 装配文件加载
│   └── load_components.py  # 构件库加载
│
├── models/             # 数据模型
│   ├── assembly.py     # 装配数据结构
│   └── components.py   # 构件数据结构
│
└── rules/              # 校验规则
    └── validators.py   # 装配合法性校验
```

## 模块说明

### models
定义核心数据结构：
- `Component`: 构件基类
- `NodeComponent`: 节点构件
- `RodComponent`: 光轴构件
- `PanelComponent`: 面板构件
- `Assembly`: 装配数据结构

### io_module
负责 JSON 文件的加载和解析：
- 加载构件库（`components.json`）
- 加载装配文件（`assemblies/*.json`）
- 数据验证和转换

### rules
实现装配合法性校验：
- 端口使用检查
- 光轴对齐检查
- 几何约束验证

### geometry
几何计算和生成：
- 坐标系变换
- 端口世界坐标计算
- 光轴和面板几何生成

### cadquery_export
使用 CadQuery 生成 3D 模型：
- 节点放置
- 光轴生成
- 面板生成
- STEP 文件导出

## 开发指南

### 添加新的校验规则

在 `rules/validators.py` 中添加新的校验函数：

```python
def validate_new_rule(assembly: Assembly) -> List[ValidationError]:
    """新的校验规则"""
    errors = []
    # 实现校验逻辑
    return errors
```

然后在 `validate_assembly()` 中调用。

### 添加新的几何类型

1. 在 `models/components.py` 中定义新的构件类型
2. 在 `io_module/load_components.py` 中添加加载逻辑
3. 在 `geometry/` 中实现几何生成
4. 在 `cadquery_export/build_cq.py` 中添加构建逻辑

### 代码规范

- 使用类型提示（Type Hints）
- 添加文档字符串（Docstrings）
- 遵循 PEP 8 代码风格
- 单元测试（TODO）

## 依赖

- `cadquery`: 3D 建模引擎
- `numpy`: 数值计算
- `scipy`: 旋转变换
