# 装配文件说明

## 装配列表

### 01_nodes_test.json
**节点测试装配**

所有节点横排显示，用于验证：
- 节点 STEP 文件是否正确加载
- 节点原点位置是否正确
- 节点轴向是否正确

构建：
```bash
python build.py assemblies/01_nodes_test.json
```

### 02_box_lamp.json
**机箱风格灯具**

一个 200×200×300mm 的立方体框架结构：

**结构**：
- 4 个底座支撑（SK8）- 四个角
- 4 根竖直光轴（300mm）
- 4 个固定环（SC6）- 中间位置
- 4 个顶部十字连接件 - 四个角
- 4 根顶部横向光轴 - 形成顶部框架
- 底板（240×240×5mm）
- 顶板（240×240×3mm）

构建：
```bash
python build.py assemblies/02_box_lamp.json
```

### 03_complex_lamp.json
**复杂错位灯具**

一个 150×150×280mm 的错位结构，展示光轴错位美学：

**特点**：
- 光轴错位布局（不对称）
- 多节点设计（21个节点）
- 4 块小玻璃面板（90×90×3mm）
- SC6 夹持玻璃（间距 11mm）
- 尺寸 < 500mm

**结构**：
- 底层：4 个 SK8 支撑座
- 中层：4 个节点（十字+T型）+ 1 个中心十字
- 顶层：4 个 T 型节点（错位布局）
- 8 个 SC6 固定环（4 对，夹持玻璃）
- 4 块玻璃面板（四个方向）

构建：
```bash
python build.py assemblies/03_complex_lamp.json
```

## 创建新装配

1. 在此目录创建 JSON 文件
2. 定义节点、光轴、面板
3. 运行 `python build.py assemblies/your_file.json`

## JSON 格式

```json
{
  "name": "装配名称",
  "unit_mm": 1.0,
  "nodes": [
    {
      "id": "节点ID",
      "component_id": "节点类型",
      "position": [x, y, z],
      "rotation_deg": [rz, ry, rx]
    }
  ],
  "rods": [
    {
      "id": "光轴ID",
      "component_id": "rod_3mm",
      "from": {"node": "起点节点", "port": "端口", "side": "positive/negative"},
      "to": {"node": "终点节点", "port": "端口", "side": "positive/negative"}
    }
  ],
  "panels": [
    {
      "id": "面板ID",
      "component_id": "panel_rect",
      "position": [x, y, z],
      "normal": [nx, ny, nz],
      "x_dir": [xx, xy, xz],
      "size_mm": [width, height],
      "thickness_mm": thickness
    }
  ],
  "rod_attachments": [
    {
      "node": "节点ID",
      "port": "端口",
      "rod": "光轴ID",
      "offset_mm": 距离
    }
  ]
}
```

## 可用节点

- `node_cross_6x6` - 十字连接件（6个端口）
- `node_T_6x6` - T型连接件（3个端口）
- `node_parallel_6x6_c10` - 平行连接件（2个端口）
- `node_SC6_ring` - 固定环（1个端口）
- `node_SK6_support` - SK6支撑座（1个端口）
- `node_SK8_support` - SK8支撑座（1个端口）

详见 `nodes/components.json`
