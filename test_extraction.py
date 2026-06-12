"""
测试Word文档提取功能
"""
import os
import sys

# 模拟处理一个测试文件
def test_extraction():
    print("=" * 60)
    print("测试Word文档提取功能")
    print("=" * 60)
    
    # 查找一个测试用的Word文档
    test_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".docx"):
                test_files.append(os.path.join(root, file))
    
    if not test_files:
        print("\n未找到测试用的Word文档")
        print("请手动指定一个Word文档路径进行测试")
        return
    
    print(f"\n找到 {len(test_files)} 个Word文档:")
    for i, f in enumerate(test_files[:5], 1):
        print(f"  {i}. {f}")
    
    if len(test_files) > 0:
        test_file = test_files[0]
        print(f"\n使用第一个文档测试: {test_file}")
        
        # 尝试导入并运行提取功能
        try:
            print("\n[1] 导入模块...")
            from extract_tool_gui import ExtractThread
            
            print("[2] 创建提取线程...")
            thread = ExtractThread(test_file)
            
            print("[3] 运行提取...")
            thread.run()
            
            print("\n[4] 检查结果...")
            print(f"提取到的产品数量: {len(thread.products) if hasattr(thread, 'products') else 0}")
            
        except Exception as e:
            print(f"\n错误: {type(e).__name__}: {e}")
            import traceback
            print("\n详细错误信息:")
            traceback.print_exc()

if __name__ == "__main__":
    test_extraction()
    input("\n按Enter键退出...")
