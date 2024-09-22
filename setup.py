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
    install_requires=['openai==1.46.0', 'pydantic==2.9.2'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version required
)
