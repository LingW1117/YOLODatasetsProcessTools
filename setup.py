from setuptools import setup, find_packages

setup(
    name="yolo-tools",
    version="1.0.0",
    description="YOLO dataset processing utilities: split, clean, augment, convert, and more.",
    long_description=open("Readme.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5",
        "numpy>=1.21",
        "Pillow>=9.0",
        "requests>=2.25",
        "PyMuPDF>=1.19",
        "click>=8.0",
        "openai>=1.0",
    ],
    entry_points={
        "console_scripts": [
            "yolo-tools = yolo_tools.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
