# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name="yaml_rulz",
    version="0.0.1",
    description="A YAML validator",
    license="MIT",
    author="Milan Boleradszki",
    author_email="bmilan1985@gmail.com",
    maintainer="Milan Boleradszki",
    maintainer_email="bmilan1985@gmail.com",
    url="https://github.com/milonoir/yaml_rulz",
    packages=["yaml_rulz"],
    install_requires=["PyYAML", "prettytable"],
    tests_require=["mock"],
    classifiers=[
        # "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        # "Development Status :: 6 - Mature",
        # "Development Status :: 7 - Inactive",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Topic :: Text Processing :: Markup",
    ],
    entry_points={
        "console_scripts": [
            "yaml_rulz = yaml_rulz.cli:main",
        ],
    },
)
