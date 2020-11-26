import os

from setuptools import setup, find_packages

requires = []

setup(
    name="si-eng-prefix",
    version="0.3",
    description="SI Engineering Prefix",
    classifiers=[
        "Programming Language :: Python",
    ],
    author="PowerCore Engineering",
    author_email="john@powercoreeng.com",
    url="",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    install_requires=requires,
)
