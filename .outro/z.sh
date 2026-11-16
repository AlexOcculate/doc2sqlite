# cd doc2_sqlite_project/
mkdir -p src/doc2sqlite/
touch src/doc2sqlite/__init__.py
touch src/doc2sqlite/core.py
mkdir -p tests/
touch LICENSE
touch pyproject.toml
touch README.md


python -m pip install --upgrade build twine

python -m build



python -m twine upload --repository testpypi dist/*


python -m pip install --upgrade build
pip install --upgrade pip  

python -m build

pip install -e .
pip install --force-reinstall dist/*.whl



To publish a Python package to PyPI (the Python Package Index), structure your project with a pyproject.toml configuration file, build your distribution archives, and upload them using an API token. [1] (https://packaging.python.org/tutorials/packaging-projects/), [2] (https://www.linkedin.com/pulse/build-publish-your-own-python-package-pypi-pratik-joshi-apftc), [3] (https://www.youtube.com/watch?v=OXkFRBb6l3M&vl=en&t=3)
The modern, standard approach uses pyproject.toml and the build and twine tools rather than legacy setup.py scripts. [1] (https://www.linkedin.com/pulse/build-publish-your-own-python-package-pypi-pratik-joshi-apftc), [2] (https://www.youtube.com/watch?v=OXkFRBb6l3M&vl=en&t=3)

1. Structure Your Project

Create a root directory for your project with a nested folder for your actual source code. Ensure the package name you choose is unique and not already taken on PyPI. [1] (https://www.youtube.com/watch?v=Kz6IlDCyOUY&t=21), [2] (https://www.youtube.com/watch?v=h6oa_FwzFwU&t=580), [3] (https://www.youtube.com/watch?v=WKc2BdgmGZE&t=36)
text
my_package_project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── core.py
├── tests/
├── LICENSE
├── pyproject.toml
└── README.md
Use code with caution.
• __init__.py. This file tells Python to treat the directory as a package and lets you expose key functions directly upon import. [1] (https://www.youtube.com/watch?v=Kz6IlDCyOUY&t=21), [2] (https://www.youtube.com/watch?v=OI6M9BRwfJM&t=6)
• README.md. This Markdown file holds your detailed project description and usage examples, which PyPI displays on your package page. [1] (https://www.youtube.com/watch?v=pdyuRk8QL_U&t=41), [2] (https://packaging.python.org/tutorials/packaging-projects/)
• LICENSE. Include the full text of an open-source license, such as the MIT License, so others know how they can use your code. [1] (https://www.youtube.com/watch?v=pdyuRk8QL_U&t=41)

2. Configure pyproject.toml

Create a pyproject.toml file in your root directory. This central metadata file tells build tools how to package your code and lists your project's dependencies. [1] (https://pydevtools.com/handbook/tutorial/publishing-your-first-python-package-to-pypi/), [2] (https://www.linkedin.com/pulse/build-publish-your-own-python-package-pypi-pratik-joshi-apftc)
toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-unique-package-name"
version = "0.1.0"
description = "A short, one-sentence summary of your package."
readme = "README.md"
requires-python = ">=3.8"
license = "MIT"
license-files = ["LICENSE"]
authors = [
  { name = "Your Name", email = "you@example.com" }
]
dependencies = [
  # List required third-party packages here, e.g., "requests>=2.31.0"
]

[project.urls]
Homepage = "https://github.com/yourusername/your-repo"
Use code with caution.

3. Build the Distribution Files

Install the official PyPA build and twine utilities, then compile your project into distributable archives. [1] (https://packaging.python.org/tutorials/packaging-projects/), [2] (https://www.linkedin.com/pulse/build-publish-your-own-python-package-pypi-pratik-joshi-apftc)
1. Install the tools. Run python -m pip install --upgrade build twine in your terminal. [1] (https://packaging.python.org/tutorials/packaging-projects/), [2] (https://www.linkedin.com/pulse/build-publish-your-own-python-package-pypi-pratik-joshi-apftc)
2. Generate the archives. Navigate to your root folder (where pyproject.toml lives) and run python -m build. [1] (https://www.youtube.com/watch?v=pdyuRk8QL_U&t=41), [2] (https://www.youtube.com/watch?v=OXkFRBb6l3M&vl=en&t=3)
3. Verify the output. Check the newly created dist/ folder to confirm it contains both a .whl (wheel) file and a .tar.gz (source archive) file. [1] (https://pydevtools.com/handbook/tutorial/publishing-your-first-python-package-to-pypi/), [2] (https://www.youtube.com/watch?v=pdyuRk8QL_U&t=41)

4. Create an Account and API Token

PyPI requires two-factor authentication and API tokens for uploading packages. [1] (https://www.youtube.com/watch?v=b8GCIc0eW0o&t=44), [2] (https://packaging.python.org/tutorials/packaging-projects/), [3] (https://www.youtube.com/watch?v=pdyuRk8QL_U&t=41)
1. Test first (Recommended). Register an account on TestPyPI to practice uploading without affecting the live index.
2. Create a live account. Register and verify your email on the main PyPI registration page.
3. Generate a token. Go to your PyPI Account Settings, scroll to API tokens, and create a new token. Copy the token immediately (including the pypi- prefix) because it will only be shown once. [1] (https://packaging.python.org/tutorials/packaging-projects/), [2] (https://www.youtube.com/watch?v=pdyuRk8QL_U&t=41), [3] (https://www.youtube.com/watch?v=OXkFRBb6l3M&vl=en&t=3), [4] (https://pydevtools.com/handbook/tutorial/publishing-your-first-python-package-to-pypi/)

5. Upload to PyPI

Use twine to securely upload your built files to the index. [1] (https://www.linkedin.com/pulse/build-publish-your-own-python-package-pypi-pratik-joshi-apftc), [2] (https://www.youtube.com/watch?v=OXkFRBb6l3M&vl=en&t=3)
1. Upload to TestPyPI (Optional). Run python -m twine upload --repository testpypi dist/* to verify everything looks right on the test server.
2. Upload to live PyPI. Run python -m twine upload dist/*.
3. Authenticate. When prompted for a username, enter __token__. When prompted for a password, paste your full API token.
4. Test your installation. Open a fresh virtual environment and run pip install my-unique-package-name to confirm anyone can download and import your library. [1] (https://www.youtube.com/watch?v=rM1SqONoPXs&t=34), [2] (https://packaging.python.org/tutorials/packaging-projects/), [3] (https://www.youtube.com/watch?v=OXkFRBb6l3M&vl=en&t=3)
(Note: If you use uv as your project manager, you can streamline these steps using uv init, uv build, and uv publish instead of build and twine.) [1] (https://www.youtube.com/watch?v=rM1SqONoPXs&t=34), [2] (https://pydevtools.com/handbook/tutorial/publishing-your-first-python-package-to-pypi/)
Would you like to see how to automate future releases using GitHub Actions (Trusted Publishing), or do you need help configuring specific CLI entry points or package dependencies?
