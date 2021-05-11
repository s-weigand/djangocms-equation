#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages
from setuptools import setup

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = [
    "django-cms>=3.4,<3.8",
    "django>=1.11,!=2.0.*,<3.0",
    "djangocms-text-ckeditor>=3.2.1,<4.0.0",
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
        "Framework :: Django CMS :: 3.4",
        "Framework :: Django CMS :: 3.5",
        "Framework :: Django CMS :: 3.6",
        "Framework :: Django CMS :: 3.7",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
    python_requires=">=3.6",
    test_suite="tests.settings.run",
    url="https://github.com/s-weigand/djangocms-equation",
    project_urls={
        "Documentation": "https://djangocms-equation.readthedocs.io/",
        "Source": "https://github.com/s-weigand/djangocms-equation",
        "Tracker": "https://github.com/s-weigand/djangocms-equation/issues",
        "Changelog": "https://djangocms-equation.readthedocs.io/en/latest/history.html",
    },
    version="0.2.4",
    zip_safe=False,
)
