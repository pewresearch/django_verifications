import os
from distutils.core import setup
from setuptools import find_packages

with open(os.path.join(os.path.dirname(__file__), "README.md"), "rb") as readme:
    readme = str(readme.read())

install_requires = []
with open("requirements.txt") as reqs:
    for line in reqs.read().split("\n"):
        if not line.startswith("#"):
            install_requires.append(line)

setup(
    name="django_verifications",
    version='0.2.7.dev1',
    description="Lightweight coding interface to manually review and freeze various model attributes using simple metadata toggles",
    long_description=readme,
    url="https://github.com/pewresearch/django_verifications",
    author="Pew Research Center",
    author_email="info@pewresearch.org",
    install_requires=install_requires,
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    include_package_data=True,
    keywords="text processing, data validation, django, pew pew pew",
    license="GPLv2+",
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
