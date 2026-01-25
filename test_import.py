"""
测试脚本：检查项目是否能正常导入
用于验证项目的基本可运行性
"""
import sys
import os

# 设置UTF-8输出（仅在Windows上需要）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("项目导入测试")
print("=" * 60)

# 测试1: 检查环境变量
print("\n1. 检查环境变量...")
env_var = os.getenv('GLOBAL_TOOLSFUNC_new')
if env_var:
    print(f"   [OK] GLOBAL_TOOLSFUNC_new 已设置: {env_var}")
    if os.path.exists(env_var):
        print(f"   [OK] 路径存在")
    else:
        print(f"   [WARN] 警告: 路径不存在!")
else:
    print("   [FAIL] GLOBAL_TOOLSFUNC_new 未设置")
    print("   提示: 需要设置此环境变量才能运行项目")

# 测试2: 检查依赖包
print("\n2. 检查依赖包...")
required_packages = {
    'pandas': '数据处理',
    'numpy': '数值计算',
    'scipy': '科学计算',
    'pymysql': 'MySQL连接',
    'yaml': 'YAML配置',
    'openpyxl': 'Excel读取',
    'xlrd': 'Excel读取(旧版)',
}

missing_packages = []
for package, description in required_packages.items():
    try:
        if package == 'yaml':
            __import__('yaml')
        else:
            __import__(package)
        print(f"   [OK] {package} - {description}")
    except ImportError:
        print(f"   [FAIL] {package} - {description} (未安装)")
        missing_packages.append(package)

# 测试3: 尝试导入项目模块
print("\n3. 检查项目模块导入...")

# 测试 setup_logger (不依赖环境变量)
try:
    from setup_logger.logger_setup import setup_logger
    print("   [OK] setup_logger 模块")
except Exception as e:
    print(f"   [FAIL] setup_logger 模块: {e}")

# 测试 global_dic (可能依赖配置文件)
try:
    import global_setting.global_dic as glv
    print("   [OK] global_setting.global_dic 模块")
except FileNotFoundError as e:
    print(f"   [FAIL] global_setting.global_dic: 配置文件缺失")
    print(f"      详情: {e}")
except Exception as e:
    print(f"   [FAIL] global_setting.global_dic: {e}")

# 测试主模块 (依赖环境变量)
if env_var:
    try:
        # 这会触发所有依赖项的导入
        import factor_update_main
        print("   [OK] factor_update_main 模块")
    except Exception as e:
        print(f"   [FAIL] factor_update_main: {e}")
else:
    print("   [SKIP] 跳过 factor_update_main (需要环境变量)")

# 测试4: 检查配置文件
print("\n4. 检查配置文件...")
config_files = {
    'config_project/sql_connection.yaml': 'SQL连接配置',
    'config_project/sql_connection.yaml.example': 'SQL连接配置示例',
}

for file_path, description in config_files.items():
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    if os.path.exists(full_path):
        print(f"   [OK] {file_path} - {description}")
    else:
        print(f"   [MISSING] {file_path} - {description} (不存在)")

# 总结
print("\n" + "=" * 60)
print("总结:")
print("=" * 60)

if missing_packages:
    print(f"[FAIL] 缺少依赖包: {', '.join(missing_packages)}")
    print(f"  安装命令: pip install {' '.join(missing_packages)}")
else:
    print("[OK] 所有依赖包已安装")

if not env_var:
    print("\n[FAIL] 需要设置环境变量 GLOBAL_TOOLSFUNC_new")
    print("  Windows: set GLOBAL_TOOLSFUNC_new=D:\\path\\to\\global_tools")
    print("  Linux/Mac: export GLOBAL_TOOLSFUNC_new=/path/to/global_tools")
else:
    print("\n[OK] 环境变量已设置")

print("\n" + "=" * 60)
