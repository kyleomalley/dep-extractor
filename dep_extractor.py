import os
import subprocess
from collections import defaultdict, deque
import docker

def find_packages(directory):
    deb_files = []
    rpm_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.deb'):
                deb_files.append(os.path.join(root, file))
            elif file.endswith('.rpm'):
                rpm_files.append(os.path.join(root, file))
    return deb_files, rpm_files

def extract_dependencies_docker(client, image, container_name, package_path, command):
    # Create and start the container
    container = client.containers.run(image, command, name=container_name, volumes={
        package_path: {'bind': '/packages', 'mode': 'ro'}
    }, detach=True)

    # Wait for the container to finish
    exit_code = container.wait()
    output = container.logs().decode('utf-8')
    container.remove()

    if exit_code['StatusCode'] != 0:
        raise RuntimeError(f"Command {command} failed with output: {output}")

    return output

def extract_deb_dependencies(client, image, container_name, deb_file):
    command = ['dpkg-deb', '-I', f'/packages/{os.path.basename(deb_file)}']
    output = extract_dependencies_docker(client, image, container_name, os.path.dirname(deb_file), command)
    dependencies = []
    for line in output.splitlines():
        if line.startswith(' Depends:'):
            deps = line.split('Depends:')[1].strip().split(', ')
            dependencies.extend(dep.split()[0] for dep in deps)
    return dependencies

def extract_rpm_dependencies(client, image, container_name, rpm_file):
    command = ['rpm', '-qpR', f'/packages/{os.path.basename(rpm_file)}']
    output = extract_dependencies_docker(client, image, container_name, os.path.dirname(rpm_file), command)
    dependencies = output.splitlines()
    return dependencies

def resolve_dependencies(client, image, container_name, packages, extract_function):
    all_dependencies = defaultdict(set)
    package_queue = deque(packages)
    
    while package_queue:
        package = package_queue.popleft()
        if package in all_dependencies:
            continue
        
        dependencies = extract_function(client, image, container_name, package)
        all_dependencies[package].update(dependencies)
        
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

def main(directory):
    deb_files, rpm_files = find_packages(directory)
    client = docker.from_env()
    image = 'dependency-extractor:latest'
    container_name = 'dependency_extractor_container'
    
    deb_dependencies = resolve_dependencies(client, image, container_name, deb_files, extract_deb_dependencies)
    rpm_dependencies = resolve_dependencies(client, image, container_name, rpm_files, extract_rpm_dependencies)
    
    for package, deps in deb_dependencies.items():
        print(f"Package: {package}")
        print(f"Dependencies: {', '.join(deps)}")
        print()
    
    for package, deps in rpm_dependencies.items():
        print(f"Package: {package}")
        print(f"Dependencies: {', '.join(deps)}")
        print()

if __name__ == "__main__":
    directory = 'path/to/your/packages'
    main(directory)