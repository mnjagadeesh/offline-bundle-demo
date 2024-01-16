from setuptools import find_packages, setup
from package import BundlePackage

setup(
    name="offline-demo",
    version="1.0.0a",
    author="Jagadeesh Malakannavar",
    author_email="mnjagadeesh@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    cmdclass={
                "package": BundlePackage
    }
)
