from setuptools import setup, find_packages



setup(
    name="pygptcalls",  # Package name
    version="0.1.0",    # Version number
    description="A Python library for GPT-related calls",
    long_description=open('README.md').read(),  # Optional: long description from README.md
    long_description_content_type='text/markdown',  # Optional if README is in Markdown
    author="@fsaint",  # Your name or the author's name
    author_email="fsaint@gmail.com",  # Your email address
    url="https://github.com/fsaint/pygptcalls",  # URL to your GitHub repo (optional)
    packages=['pygptcalls'],
    install_requires=['annotated-types==0.7.0', 'anyio==4.4.0', 'certifi==2024.8.30', 'distro==1.9.0', 'h11==0.14.0', 'httpcore==1.0.5', 'httpx==0.27.2', 'idna==3.10', 'jiter==0.5.0', 'openai==1.46.0', 'pydantic==2.9.2', 'pydantic_core==2.23.4', 'sniffio==1.3.1', 'tqdm==4.66.5', 'typing_extensions==4.12.2'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version required
)
