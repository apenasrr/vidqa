#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=7.0",
    "natsort>=8.2.0",
    "Unidecode>=1.3.4",
    "pandas",
]

test_requirements = []

setup(
    author="apenasrr",
    author_email="apenasrr@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Quality assurance for audiovisual collections",
    entry_points={
        "console_scripts": [
            "vidqa=vidqa.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="vidqa",
    name="vidqa",
    packages=find_packages(include=["vidqa", "vidqa.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/apenasrr/vidqa",
    version="0.1.19",
    zip_safe=False,
)
