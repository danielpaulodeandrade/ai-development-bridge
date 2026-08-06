from setuptools import setup, find_packages

setup(
    name="ai-workspace-bridge",
    version="1.0.0",
    description="Bridge API to orchestrate multiple AI browser instances for IDEs like Continue.",
    author="Daniel Andrade",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "playwright",
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "bridge=src.cli:main",
        ],
    },
)
