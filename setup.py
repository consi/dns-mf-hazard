from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="dns-mf-hazard",
    version="0.0.1",
    install_requires=requirements,
    packages=["mf_hazard"],
    author="Marek Wajdzik",
    author_email="wajdzik.m@gmail.com",
    description="Tool to check if your DNS comply to Polish Ministry of Finance gambling domains restrictions",
    entry_points={
        "console_scripts": ["dns-mf-hazard=mf_hazard.app:main"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
)
