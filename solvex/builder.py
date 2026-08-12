"""SolveX Independent Builder — Tiến trình đóng gói .exe độc lập cho SolveX.
Chạy hoàn toàn tách biệt với SolveX chính, giúp việc build không bị ngắt quãng khi SolveX đóng hoặc khởi động lại.
"""

import os
import shutil
import subprocess
import sys
import time


def find_project_dir() -> str:
    candidates = [
        os.getcwd(),
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        r"c:\Users\hoang\Downloads\SolveX-main\SolveX-main",
    ]
    for p in candidates:
        if os.path.exists(os.path.join(p, "solvex.spec")):
            return p
    return candidates[0]


def main():
    print("=" * 60)
    print("      SOLVEX INDEPENDENT EXE BUILDER v1.8.3")
    print("=" * 60)

    project_dir = find_project_dir()
    print(f"[+] Project Directory: {project_dir}")

    # 1. Kill old SolveX.exe to release file lock
    print("[+] Closing running SolveX.exe instances to release file locks...")
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "SolveX.exe"], capture_output=True, text=True)
    except Exception:
        pass

    time.sleep(1)

    # 2. Check spec file
    spec_file = os.path.join(project_dir, "solvex.spec")
    if not os.path.exists(spec_file):
        print(f"[!] ERROR: Spec file not found at {spec_file}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # 3. Locate PyInstaller
    python_exe = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    pyinstaller_exe = os.path.join(project_dir, ".venv", "Scripts", "pyinstaller.exe")

    if os.path.exists(pyinstaller_exe):
        cmd = [pyinstaller_exe, "--noconfirm", "--clean", spec_file]
    elif os.path.exists(python_exe):
        cmd = [python_exe, "-m", "PyInstaller", "--noconfirm", "--clean", spec_file]
    else:
        sys_pyinstaller = shutil.which("pyinstaller")
        if sys_pyinstaller:
            cmd = [sys_pyinstaller, "--noconfirm", "--clean", spec_file]
        else:
            cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", spec_file]

    print(f"[+] Running Command: {' '.join(cmd)}")
    print("-" * 60)

    start_time = time.time()
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()

        proc.wait()
        elapsed = time.time() - start_time

        print("-" * 60)
        if proc.returncode == 0:
            exe_path = os.path.join(project_dir, "dist", "SolveX.exe")
            print(f"[✓] BUILD SUCCESSFUL in {elapsed:.1f} seconds!")
            print(f"[✓] Executable output path: {exe_path}")
        else:
            print(f"[!] BUILD FAILED with exit code {proc.returncode}")
    except Exception as exc:
        print(f"[!] ERROR executing build process: {exc}")

    print("=" * 60)
    input("\nPress Enter to close builder window...")


if __name__ == "__main__":
    main()
