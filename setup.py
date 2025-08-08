"""Setup script for corun CLI tool."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README.md if it exists
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="corun",
    version="0.0.1",
    author="Corun Community",
    author_email="duccuong2808.dev@gmail.com",
    description="Extensible CLI for freely adding custom bash/zsh commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/corun-community/corun",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "corun=src.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Unix Shell",
        "Topic :: System :: Shells",
        "Topic :: System :: System Shells",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    keywords="cli, shell, bash, automation, community, metaprogramming",
    project_urls={
        "Bug Reports": "https://github.com/corun-community/corun/issues",
        "Source": "https://github.com/corun-community/corun",
        "Documentation": "https://github.com/corun-community/corun/blob/main/docs/",
    },
)
