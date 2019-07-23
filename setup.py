from setuptools import setup

setup(
    name="minerva",
    version="0.0.1",
    description="A text mining library.",
    author="Marco Basaldella",
    author_email="basaldella.marco@gmail.com",
    packages=["minerva"],
    install_requires=["nltk==3.4.4"],
)
