from setuptools import setup, find_packages

requires =[
        'flask',
        'flask-sqlalchemy',
        'psycopg2',
        ]

setup(
        name='Auswertung Bienchen',
        version='0.1',
        description='Vorbereitung zur Auswertungsdarstellung mit flask',
        author='Evgenij Kremer',
        author_email='evgenij.kremer@tu-dortmund.de',
        keywords='web flask',
        packages=find_packages(),
        include_package_data=True,
        install_requires=requires
        )
