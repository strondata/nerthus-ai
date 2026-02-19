from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nerthus-ai",
    version="0.1.0",
    author="Strondata",
    description="Biblioteca Python e CLI interativo que provê as capacidades de inteligência, análise contextual e orquestração desenvolvidas para o ecossistema Nerthus.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/strondata/nerthus-ai",
    packages=find_packages(),
    package_data={
        "nerthus_ai.resources": ["*.yaml", "templates/*.md"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nerthus=nerthus_ai.cli.main:main",
        ],
    },
)
