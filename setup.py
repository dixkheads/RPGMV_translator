from setuptools import setup, find_packages

setup(
    name='RPGMV_translator',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'RPGMV_translator=rpgmv_translator.main:main',
        ],
    },
    # Add other metadata like author, description, etc.
)
