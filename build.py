"""主程序 - 生成装配"""
import sys
import os
from datetime import datetime
from src.io_module.load_components import load_components
from src.io_module.load_assembly import load_assembly
from src.rules.validators import validate_assembly
from src.cadquery_export.build_cq import build_cadquery_assembly


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python build.py <装配文件>")
        print()
        print("可用的装配文件:")
        for f in os.listdir("assemblies"):
            if f.endswith(".json"):
                print(f"  - assemblies/{f}")
        return 1
    
    assembly_file = sys.argv[1]
    
    print("=" * 70)
    print("光轴模块化结构系统 - 构建装配")
    print("=" * 70)
    print()
    
    # 1. 加载构件库
    print("1. 加载构件库...")
    try:
        components = load_components("nodes/components.json")
        print(f"   ✓ 成功加载 {len(components)} 个构件")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return 1
    
    print()
    
    # 2. 加载装配
    print(f"2. 加载装配: {assembly_file}")
    try:
        assembly = load_assembly(assembly_file, components)
        print(f"   ✓ 装配名称: {assembly.name}")
        print(f"   ✓ 节点数: {len(assembly.nodes)}")
        print(f"   ✓ 光轴数: {len(assembly.rods)}")
        print(f"   ✓ 面板数: {len(assembly.panels)}")
        if assembly.rod_attachments:
            print(f"   ✓ 光轴附件数: {len(assembly.rod_attachments)}")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    
    # 3. 校验
    print("3. 校验装配...")
    try:
        errors = validate_assembly(assembly)
        if errors:
            print(f"   ✗ 发现 {len(errors)} 个错误:")
            for err in errors:
                print(f"     - {err}")
            return 1
        else:
            print("   ✓ 校验通过")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        return 1
    
    print()
    
    # 4. 生成模型
    print("4. 生成 CadQuery 模型...")
    try:
        cq_assembly = build_cadquery_assembly(assembly, components)
        print("   ✓ 模型生成成功")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    
    # 5. 导出
    print("5. 导出模型...")
    try:
        os.makedirs("output", exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(assembly_file))[0]
        output_file = f"output/{timestamp}_{base_name}.step"
        
        cq_assembly.save(output_file)
        print(f"   ✓ 已保存到 {output_file}")
    except Exception as e:
        print(f"   ⚠ 警告: {e}")
    
    print()
    print("=" * 70)
    print("构建完成！")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
