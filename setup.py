from setuptools import setup, find_packages

setup(
    name="pytest-pyrest",
    version="0.1.0",
    description="A PyTest plugin for REST API testing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jasmine-Arabella Post",
    author_email="",  # Add your email
    url="https://github.com/yourusername/pytest-pyrest",
    packages=find_packages(where="code"),
    package_dir={"": "code"},
    install_requires=[
        "pytest>=7.0.0",
        "requests>=2.25.0",
        "pytest-env>=1.0.0",
    ],
    python_requires=">=3.11",
    entry_points={
        "pytest11": [
            "pyrest = pyrest.plugin",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Testing",
        "Framework :: Pytest",
    ],
    keywords="pytest plugin testing api rest http",
) 