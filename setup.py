from setuptools import setup, find_packages

# Utility function to read the requirements file
def parse_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()

setup(
    name="pygptcalls",  # Package name
    version="0.1.0",    # Version number
    description="A Python library for GPT-related calls",
    long_description=open('README.md').read(),  # Optional: long description from README.md
    long_description_content_type='text/markdown',  # Optional if README is in Markdown
    author="@fsaint",  # Your name or the author's name
    author_email="fsaint@gmail.com",  # Your email address
    url="https://github.com/fsaint/pygptcalls",  # URL to your GitHub repo (optional)
    packages=find_packages(),  # Automatically find all packages in this directory
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version required
)
