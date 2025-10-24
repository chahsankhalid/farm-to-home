import toml

with open('VERSION') as version_file:
    version = version_file.read().strip()

with open('pyproject.toml', 'r') as pyproject_file:
    pyproject_data = toml.load(pyproject_file)

pyproject_data['tool']['poetry']['version'] = version

with open('pyproject.toml', 'w') as pyproject_file:
    toml.dump(pyproject_data, pyproject_file)

print(f'Updated pyproject.toml to version {version}')
