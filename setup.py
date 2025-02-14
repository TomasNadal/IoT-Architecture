from setuptools import setup, find_packages

setup(
    name="iot-architecture",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "sqlalchemy",
        "psycopg2-binary",
        "python-jose",
        "python-dotenv",
    ]
) 