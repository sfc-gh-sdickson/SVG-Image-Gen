#!/usr/bin/env python3
"""
Helper script to automatically detect missing type stubs from mypy output,
suggest or add the correct types-<package> to requirements-dev.txt, and optionally install them.
"""
import re
import subprocess
import sys
from pathlib import Path
from typing import Set

REQUIREMENTS_DEV = Path("requirements-dev.txt")

# Regex to match mypy missing type stub errors
MISSING_TYPE_RE = re.compile(r'Skipping analyzing "([\w_\-]+)": no type hints found')

# Map some common package names to their typeshed names if they differ
PACKAGE_MAP = {
    # Standard library mappings
    "yaml": "PyYAML",
    "dateutil": "python-dateutil",
    "setuptools": "setuptools",
    "pkg_resources": "setuptools",  # pkg_resources is part of setuptools
    # Common third-party packages
    "requests": "requests",
    "pytz": "pytz",
    "six": "six",
    "jinja2": "Jinja2",
    "markdown": "Markdown",
    "docutils": "docutils",
    "click": "click",
    "flask": "Flask",
    "werkzeug": "Werkzeug",
    "sqlalchemy": "SQLAlchemy",
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "scipy": "scipy",
    "scikit-learn": "scikit-learn",
    "tensorflow": "tensorflow",
    "torch": "torch",
    "pytest": "pytest",
    "pytest_mock": "pytest-mock",
    "pytest_cov": "pytest-cov",
    "coverage": "coverage",
    "black": "black",
    "flake8": "flake8",
    "mypy": "mypy",
    "ruff": "ruff",
    "isort": "isort",
    "pre_commit": "pre-commit",
    "bandit": "bandit",
    "safety": "safety",
    "cryptography": "cryptography",
    "bcrypt": "bcrypt",
    "passlib": "passlib",
    "python_dotenv": "python-dotenv",
    "structlog": "structlog",
    "prometheus_client": "prometheus-client",
    "sentry_sdk": "sentry-sdk",
    "twine": "twine",
    "build": "build",
    "hatchling": "hatchling",
    "semantic_release": "python-semantic-release",
    "gitpython": "GitPython",
    "python_gitlab": "python-gitlab",
    "responses": "responses",
    "factory_boy": "factory-boy",
    "freezegun": "freezegun",
    "mkdocs": "mkdocs",
    "mkdocs_material": "mkdocs-material",
    "mkdocstrings": "mkdocstrings",
    "mkdocs_gen_files": "mkdocs-gen-files",
    "mkdocs_literate_nav": "mkdocs-literate-nav",
    "mkdocs_section_index": "mkdocs-section-index",
    # Database and ORM
    "psycopg2": "psycopg2-binary",
    "mysql": "mysql-connector-python",
    "sqlite3": None,  # Built-in, no stub needed
    "redis": "redis",
    "pymongo": "pymongo",
    "elasticsearch": "elasticsearch",
    # Web frameworks and tools
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "gunicorn": "gunicorn",
    "celery": "celery",
    "django": "django",
    "django_rest_framework": "djangorestframework",
    # Cloud and deployment
    "boto3": "boto3",
    "botocore": "botocore",
    "google": "google-cloud-storage",
    "azure": "azure-storage-blob",
    "kubernetes": "kubernetes",
    "docker": "docker",
    # Data processing and analysis
    "openpyxl": "openpyxl",
    "xlrd": "xlrd",
    "xlwt": "xlwt",
    "tabula": "tabula-py",
    "beautifulsoup4": "beautifulsoup4",
    "lxml": "lxml",
    "xml": None,  # Built-in, no stub needed
    "json": None,  # Built-in, no stub needed
    "csv": None,  # Built-in, no stub needed
    # Testing and mocking
    "mock": "mock",
    "unittest": None,  # Built-in, no stub needed
    "pytest_asyncio": "pytest-asyncio",
    # Development tools
    # Add more mappings as needed
}


def run_mypy() -> str:
    """Run mypy and capture output."""
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "src/"], capture_output=True, text=True
    )
    return result.stdout + "\n" + result.stderr


def parse_missing_types(mypy_output: str) -> Set[str]:
    """Parse mypy output for missing type stubs."""
    missing = set()
    for line in mypy_output.splitlines():
        match = MISSING_TYPE_RE.search(line)
        if match:
            pkg = match.group(1)
            # Map to typeshed name if needed
            mapped_pkg = PACKAGE_MAP.get(pkg, pkg)
            if mapped_pkg is not None:  # Skip None values (built-in modules)
                missing.add(f"types-{mapped_pkg}")
    return missing


def update_requirements(missing_stubs: Set[str]) -> bool:
    """Add missing stubs to requirements-dev.txt if not already present."""
    if not missing_stubs:
        print("No missing type stubs detected.")
        return False
    if not REQUIREMENTS_DEV.exists():
        print(f"{REQUIREMENTS_DEV} not found!")
        return False
    with REQUIREMENTS_DEV.open("r") as f:
        lines = [line.strip() for line in f.readlines()]
    added = []
    for stub in sorted(missing_stubs):
        if not any(stub in line for line in lines):
            lines.append(stub)
            added.append(stub)
    if added:
        with REQUIREMENTS_DEV.open("w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"Added to {REQUIREMENTS_DEV}: {', '.join(added)}")
    else:
        print("All missing stubs already present in requirements-dev.txt.")
    return bool(added)


def install_stubs(missing_stubs: Set[str]) -> None:
    """Install the missing stubs using pip."""
    if not missing_stubs:
        return
    print(f"Installing: {' '.join(missing_stubs)}")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", *missing_stubs], check=False
    )


def main() -> None:
    print("Running mypy to detect missing type stubs...")
    mypy_output = run_mypy()
    missing_stubs = parse_missing_types(mypy_output)
    if not missing_stubs:
        print("No missing type stubs detected!")
        return
    print(f"Missing type stubs detected: {', '.join(missing_stubs)}")
    updated = update_requirements(missing_stubs)
    if updated:
        install = input("Install new stubs now? [Y/n]: ").strip().lower()
        if install in ("", "y", "yes"):
            install_stubs(missing_stubs)
    else:
        print("No new stubs to install.")


if __name__ == "__main__":
    main()
