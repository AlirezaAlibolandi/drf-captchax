from setuptools import setup, find_packages

setup(
    name='drf-captchax',
    version='0.1.2',
    description='Pluggable captcha support for Django REST Framework',
    author='Alireza Alibolandi',
    author_email='alirezaalibolandi@duck.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'Django>=3.2',
        'djangorestframework>=3.12',
        'Pillow>=8.0',
    ],
    include_package_data=True,
    zip_safe=False,
)
