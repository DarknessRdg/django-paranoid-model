import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('version.txt') as version_file:
    version = version_file.read().strip()

requires = [
    'Django>=1.11.0',
]

extras_require = {
    'test': [
        'Faker==5.0.1',
        'model-bakery==1.2.0',  # 1.2.1 broke tests
        'ipdb==0.10.1',
        'pytest==6.2.1',
        'pytest-django==4.1.0',
        'pytest-cov==2.11.1',
        'tox==3.21.2',
    ],
}


setuptools.setup(
    name='django-paranoid-model',
    version=version,
    url='https://github.com/DarknessRdg/django-paranoid-model',
    keywords='django paranoid safedelete softdelete',

    author='Luan Rodrigues',
    author_email='luanrodriguesbusiness@hotmail.com',

    description='Django abstract model with paranoid behavior.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=setuptools.find_packages(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=requires,
    extras_require=extras_require,
    python_requires='>=3.4',

    project_urls={
        'Bug Reports': 'https://github.com/DarknessRdg/django-paranoid-model/issues',
        'Source': 'https://github.com/DarknessRdg/django-paranoid-model/'
    },
    include_package_data=True
)
