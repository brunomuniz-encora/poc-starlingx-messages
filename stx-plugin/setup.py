from setuptools import setup, find_packages

setup(
    name='k8sapp-poc-starlingx',
    version='1.1.0',
    packages=['k8sapp_poc_starlingx'],
    install_requires=[
        # List your dependencies here
        "requests~=2.31.0",
        "matplotlib~=3.7.1"
    ],
    entry_points={
        'console_scripts': [
            'poc-starlingx = k8sapp_poc_starlingx.entry_module:main_function'
        ]
    },
    author='Bruno Muniz',
    author_email='bruno.muniz@encora.com',
    description='Description of your project',
    url='https://github.com/bmuniz-daitan/poc-starlingx-messages',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
