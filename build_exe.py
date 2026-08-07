import os
import subprocess
import sys

def build():
    print("Building standalone Doc2MD.exe for Windows with collected PyMuPDF & MarkItDown layout resources...")
    
    add_data_web = f"web{os.path.pathsep}web"
    add_data_logo = f"Kidmedia-logo.png{os.path.pathsep}."
    add_data_icon = f"app_icon.ico{os.path.pathsep}."

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=Doc2MD",
        "--icon=app_icon.ico",
        f"--add-data={add_data_web}",
        f"--add-data={add_data_logo}",
        f"--add-data={add_data_icon}",
        "--collect-all=pymupdf",
        "--collect-all=pymupdf_layout",
        "--collect-all=pymupdf4llm",
        "--collect-all=markitdown",
        "main.py"
    ]
    
    print("Executing:", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode == 0:
        exe_path = os.path.abspath("dist/Doc2MD.exe")
        print(f"\nBUILD SUCCESS! Executable created at: {exe_path}")
    else:
        print("\nBUILD FAILED with exit code:", res.returncode)

if __name__ == '__main__':
    build()
