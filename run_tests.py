"""
测试运行脚本

使用方法：
    python run_tests.py              # 运行所有测试
    python run_tests.py --unit     # 仅运行单元测试
    python run_tests.py --coverage # 运行测试并生成覆盖率报告
"""

import os
import sys
import subprocess

# 确保项目根目录在路径中
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def run_tests(args=None):
    """运行测试"""
    cmd = [sys.executable, "-m", "pytest", "tests/"]

    if args:
        cmd.extend(args)
    else:
        cmd.extend(["-v", "--tb=short"])

    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--unit":
            print("运行单元测试...")
            # 跳过需要实际模型的测试
            run_tests(["-v", "--ignore=tests/test_rag.py"])
        elif arg == "--coverage":
            print("运行测试并生成覆盖率报告...")
            run_tests(["--cov=src", "--cov-report=html", "--cov-report=term"])
        elif arg == "--help":
            print(__doc__)
        else:
            run_tests([arg])
    else:
        print("运行所有测试...")
        run_tests()


if __name__ == "__main__":
    main()
