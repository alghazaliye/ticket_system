from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ticket_system/__init__.py
from ticket_system import __version__ as version

setup(
    name="ticket_system",
    version=version,
    description="نظام متكامل لحجز التذاكر وإدارة المسارات والوكلاء",
    author="المنتصر للنقل الدولي",
    author_email="support@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
