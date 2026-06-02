import subprocess


def check_npu_available() -> bool:
    try:
        result = subprocess.run(["npu-smi", "info"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print("[OK] NPU设备检测通过")
            return True
        print("[WARN] 未检测到NPU设备")
        return False
    except FileNotFoundError:
        print("[WARN] 未检测到NPU设备")
        return False
    except subprocess.CalledProcessError:
        print("[WARN] 未检测到NPU设备")
        return False
    except subprocess.TimeoutExpired:
        print("[WARN] 未检测到NPU设备")
        return False
    except Exception:
        print("[WARN] 未检测到NPU设备")
        return False
