"""
实际测试提取功能
"""
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("测试提取功能")
print("=" * 60)

# 导入extract_tool_gui
print("\n[1] 导入模块...")
try:
    from extract_tool_gui import ExtractThread
    print("OK 导入成功")
except Exception as e:
    print(f"FAIL 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 使用测试文档
test_file = "d:\\OH-workspace\\diaohuo-assistant\\测试价格表.docx"

if os.path.exists(test_file):
    print(f"OK 使用测试文档: {test_file}")
else:
    print(f"FAIL 测试文档不存在: {test_file}")
    sys.exit(1)

# 创建线程
print("\n[2] 创建提取线程...")
try:
    thread = ExtractThread(test_file)
    print("OK 线程创建成功")
except Exception as e:
    print(f"FAIL 线程创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 运行提取
print("\n[3] 运行提取...")
try:
    thread.run()
    print("OK 提取完成")
except Exception as e:
    print(f"FAIL 提取失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 检查结果
print("\n[4] 检查结果...")
if hasattr(thread, 'products'):
    products = thread.products
    print(f"OK 提取到 {len(products)} 条产品")
    if products:
        print("\n前3条产品:")
        for i, p in enumerate(products[:3], 1):
            print(f"  {i}. 系列:{p.get('series', '')}, CPU:{p.get('cpu', '')}, 内存:{p.get('ram', '')}, 硬盘:{p.get('storage', '')}")
else:
    print("WARN 无法获取products属性")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

input("\n按Enter键退出...")
