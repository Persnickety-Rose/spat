from setuptools import setup, find_packages

setup(
    name="pyrest",
    version="0.1.0",
    packages=find_packages(where="code"),
    package_dir={"": "code"},
    install_requires=[
        "pytest",
        "requests",
        "repackage",
        "random-word"
    ],
    python_requires=">=3.11",
) 