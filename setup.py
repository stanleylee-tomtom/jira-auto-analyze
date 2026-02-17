from setuptools import setup, find_packages

setup(
    name="jira-auto-analyze",
    version="0.1.0",
    description="CLI tool to analyze Jira bug tickets using GitHub Copilot",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "jira-analyze=src.cli:cli",
        ],
    },
    python_requires=">=3.8",
)
