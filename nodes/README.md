# 节点模型存储目录

## 文件命名规范

每个节点对应一个 STEP 文件，文件名与节点 ID 一致：

```
nodes/
├── node_cross_6x6.step          # 十字连接件
├── node_T_6x6.step              # T型连接件
├── node_parallel_6x6_c10.step   # 平行连接件
├── node_SC6_ring.step           # 固定环
├── node_SK6_support.step        # SK6支撑座
└── node_SK8_support.step        # SK8支撑座
```

## 坐标系要求

每个 STEP 文件的坐标系必须符合 `docs/component_frames.md` 中的定义：

- 原点位置：按照各节点的 `origin_rule`
- 轴向：与全局坐标系平行（+X右，+Y前，+Z上）
- 单位：毫米 (mm)

## 使用方法

1. 将你的节点 CAD 模型导出为 STEP 格式
2. 确保坐标系正确
3. 重命名为对应的节点 ID
4. 放入此目录

程序会自动加载这些文件替换占位几何。
