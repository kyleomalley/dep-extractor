import os
import subprocess
from collections import defaultdict, deque
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)

def find_packages(packages_dir):
    package_files = []
    for root, _, files in os.walk(packages_dir):
        for file in files:
            if file.endswith('.deb') or file.endswith('.rpm'):
                package_files.append(os.path.join(root, file))
    return package_files

def extract_dependencies_deb(package_path):
    dependencies = set()
    command = ['dpkg-deb', '-I', package_path]
    output = subprocess.check_output(command, text=True)
    for line in output.splitlines():
        if line.startswith(' Depends:'):
            deps = line.split('Depends:')[1].strip().split(', ')
            dependencies.update(dep.split()[0] for dep in deps)
    return dependencies

def extract_dependencies_rpm(package_path):
    dependencies = set()
    command = ['rpm', '-qpR', package_path]
    output = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL)

    pattern = re.compile(r'^\w+(?:-\w+)*\s*(?:=\s*.+)?$')
    for line in output.split("\n"):
        match = pattern.match(line)
        if match:
            dependencies.add(match.group(0).split('=')[0].strip())

    return dependencies


def extract_dependencies(package_path):
    if package_path.endswith('.deb'):
        return extract_dependencies_deb(package_path)
    elif package_path.endswith('.rpm'):
        return extract_dependencies_rpm(package_path)
    else:
        raise ValueError("Unsupported package format")

def resolve_dependencies(package_files):
    all_dependencies = defaultdict(set)
    package_queue = deque(package_files)
    
    while package_queue:
        package_file = package_queue.popleft()
        if package_file in all_dependencies:
            continue
        
        dependencies = extract_dependencies(package_file)
        all_dependencies[package_file].update(dependencies)
        
        for dep in dependencies:
            dep_file = find_package_file(dep)
            if dep_file and dep_file not in all_dependencies:
                package_queue.append(dep_file)
    
    return all_dependencies

def find_package_file(package_name):
    # Implement a function to find the actual package file in the directory
    # based on the package name. This can be a bit tricky and may need
    # heuristics or mapping to identify the correct file.
    return None

def generate_install_command(package_file, dependencies):
    if package_file.endswith(".rpm"):
        install_command = "dnf install -y"
    elif package_file.endswith(".deb"):
        install_command = "apt-get install -y"
    else:
        raise ValueError("Unsupported package type. Supported types are 'rpm' and 'deb'.")

    install_command += " " + " ".join(dependencies)
    return install_command

def main(packages_dir):
    package_files = find_packages(packages_dir)
    
    if not package_files:
        logging.error("No package files found in the specified directory.")
        return
    
    dependencies = resolve_dependencies(package_files)
    
    for package_file, deps in dependencies.items():
        print(f"Package File: {package_file}")
        print(f"Dependencies: {', '.join(deps)}")
        
        # Generate installation command
        install_command = generate_install_command(package_file, deps)
        print(f"Installation command: {install_command}")
        print()



if __name__ == "__main__":
    packages_dir = '/app/packages_dir'
    main(packages_dir)
