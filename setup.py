from setuptools import setup, find_packages

# Read requirements from requirements.txt if it exists
try:
    with open('requirements.txt') as f:
        required = f.read().splitlines()
except FileNotFoundError:
    required = [
        "Click>=8.0",
        "requests>=2.25.0",
        "python-dateutil>=2.8.0",
        "pyyaml>=5.4.0",
        "pyjwt>=2.0.0",
        "urllib3>=2.0.0"
    ]

# Read long description from README.md
try:
    with open("README.md", encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A comprehensive Slurm REST API client"

setup(
    name="slurmrest",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=required,
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=22.0.0',
            'isort>=5.0.0',
            'mypy>=0.900',
            'build>=0.7.0',
            'twine>=3.4.0'
        ]
    },
    entry_points={
        "console_scripts": [
            "srest=srest.cli.main:cli",
        ],
    },
    author="Jose Luna",
    author_email="jose@lunajos.com",
    description="A comprehensive Slurm REST API client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lunajos/srest",
    project_urls={
        "Bug Tracker": "https://github.com/lunajos/srest/issues",
        "Documentation": "https://github.com/lunajos/srest/wiki",
        "Source Code": "https://github.com/lunajos/srest",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Clustering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)