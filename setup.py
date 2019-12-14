import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-paranoid-model", # Replace with your own username
    version="0.0.1",
    author="Luan Rodrigues",
    author_email="luanrodriguesbusiness@hotmail.com",
    description="Django abstract model with paranoid behavior,",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DarknessRdg/django-paranoid-model",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)