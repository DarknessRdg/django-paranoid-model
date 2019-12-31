import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-paranoid-model',
    version='0.0.3',
    url='https://github.com/DarknessRdg/django-paranoid-model',
    keywords='django paranoid safedelete softdelete',

    author='Luan Rodrigues',
    author_email='luanrodriguesbusiness@hotmail.com',
    
    description='Django abstract model with paranoid behavior,',
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

    install_requires=['Django'],
    extra_requires={
        'test': ['Faker']
    },
    python_requires='>=3.4',

    project_urls={
        'Bug Reports': 'https://github.com/DarknessRdg/django-paranoid-model/issues',
        'Source': 'https://github.com/DarknessRdg/django-paranoid-model/'
    }
)