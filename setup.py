"""
Setup script for Storage Manager
For creating Python package distribution
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="storage-manager",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="System-wide file scanner to find and remove large files safely",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/storage-manager",
    project_urls={
        "Bug Tracker": "https://github.com/YOUR_USERNAME/storage-manager/issues",
        "Documentation": "https://github.com/YOUR_USERNAME/storage-manager#readme",
        "Source Code": "https://github.com/YOUR_USERNAME/storage-manager",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.7",
    install_requires=[
        "send2trash>=1.8.0",
        "Pillow>=10.2.0",
    ],
    entry_points={
        "console_scripts": [
            "storage-manager=main:main",
        ],
    },
    keywords="storage file-manager disk-cleanup large-files system-scanner",
    include_package_data=True,
)
