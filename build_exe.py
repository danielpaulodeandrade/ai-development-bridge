import PyInstaller.__main__
import os
import shutil

# Ensure we are in the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

print("Compiling AI Workspace Bridge as a standalone executable...")

PyInstaller.__main__.run([
    'src/cli.py',
    '--name=bridge',
    '--onefile',
    '--icon=src/img/bot.ico',
    '--add-data=.env.example;.',
    '--add-data=config.yaml;.',
    '--add-data=README.txt;.',
    '--add-data=.continue;.continue',
    '--hidden-import=playwright',
    '--hidden-import=playwright.sync_api',
    '--hidden-import=playwright.async_api',
    '--hidden-import=playwright._impl',
    '--hidden-import=playwright.__main__',
    '--hidden-import=uvicorn',
    '--hidden-import=fastapi',
    '--hidden-import=sse_starlette',
    '--hidden-import=src.interface_layer.main',
])

print("Compilation finished. Executable is located in the 'dist' folder.")
