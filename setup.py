#!/usr/bin/env python
import os
from setuptools import setup, find_packages

long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Bifrost Animation Asset Management System for production pipelines."

setup(
    name="bifrost-pipeline",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    
    # Dependencies
    install_requires=[
        "sqlalchemy>=1.4.0",
        "pyyaml>=6.0.0",
        "click>=8.0.0",
        "rich>=10.0.0",
        "requests>=2.26.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.2",
        "python-dotenv>=0.19.0",
        # Removed uuid as it is part of Python's standard library
        # OpenUSD dependency
        "usd-core>=23.11.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.1",
            "pytest-mock>=3.6.1",
            "black>=21.8b0",
            "isort>=5.9.3",
            "flake8>=3.9.2",
            "mypy>=0.910",
        ],
        "ui": ["pyside6>=6.2.0"],
        "cloud": [
            "boto3>=1.18.0",
            "google-cloud-storage>=1.42.0",
        ],
        "docs": [
            "sphinx>=4.2.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        # OpenAssetIO integration
        "openassetio": ["openassetio>=1.0.0-rc.2"],
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "bifrost=bifrost.ui.cli:main",
        ],
    },
    
    # Metadata
    author="Bifrost Team",
    author_email="example@example.com",
    description="Animation Asset Management System for production pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="animation, asset management, production pipeline, openusd, openassetio",
    url="https://github.com/your-organization/bifrost",
    project_urls={
        "Bug Tracker": "https://github.com/your-organization/bifrost/issues",
        "Documentation": "https://bifrost.readthedocs.io/",
        "Source Code": "https://github.com/your-organization/bifrost",
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    
    python_requires=">=3.9",
)
