from setuptools import setup, find_packages

setup(
    name="slurmrest",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click>=8.0",
        "requests>=2.25.0",
        "python-dateutil>=2.8.0",
        "pyyaml>=5.4.0",
        "pyjwt>=2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "srest=srest.cli.main:cli",
        ],
    },
    author="Jose Luna",
    author_email="jluna@tacc.utexas.edu",
    description="A comprehensive Slurm REST API client",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lunajos/srest",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)