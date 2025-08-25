from setuptools import setup, find_packages

setup(
    name="auteur-studio",
    version="0.1.0",
    description="An AI-powered animation studio pipeline",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MrPenguin(Nipun Kumar)",
    author_email="worknk555@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "google-genai>=0.3.0",
        "requests>=2.25.0",
        "moviepy>=1.0.0",
        "pyngrok>=5.0.0",
        "pillow>=9.0.0",
        "pyyaml>=6.0",
        "tqdm>=4.60.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "auteur=auteur_studio.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "auteur_studio": ["../configs/*.yaml", "../configs/*.json"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
        "Programming Language :: Python :: 3.11",
    ],
)
