import os
import platform
import subprocess

def install_dependencies():
    # Navigate to the project directory
    project_directory = './'
    os.chdir(project_directory)

    # List of packages to install
    packages = [
        'Flask',
        'flask-cors',
        'Flask-SQLAlchemy',
        'python-decouple',
        'mysql-connector-python'
    ]

    # Install the packages
    for package in packages:
        subprocess.call(['pip', 'install', package])

if __name__ == '__main__':
    install_dependencies()
