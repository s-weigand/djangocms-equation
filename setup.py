#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = [
    "django-cms>=3.4,<3.8",
    "django>=1.11,!=2.0.*,<3.0",
    "djangocms-text-ckeditor>=3.2.1",
]

setup(
    author="Sebastian Weigand",
    author_email="s.weigand.phy@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="DjangoCMS plugin to write equations, utilizing KaTeX",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="djangocms-equation django-cms django cms equation latex katex mhchem",
    name="djangocms-equation",
    packages=find_packages(include=["djangocms_equation"]),
    python_requires=">=3.5",
    test_suite="tests.settings.run",
    url="https://github.com/s-weigand/djangocms-equation",
    project_urls={
        "Documentation": "https://djangocms-equation.readthedocs.io/",
        "Source": "https://github.com/s-weigand/djangocms-equation",
        "Tracker": "https://github.com/s-weigand/djangocms-equation/issues",
    },
    version="0.2.0",
    zip_safe=False,
)
