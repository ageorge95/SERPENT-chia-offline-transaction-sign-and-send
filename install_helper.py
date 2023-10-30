from sys import version_info

invalid_python_versions = [
    '3.12' # not compatible with blspy
]

current_python_version = f'{version_info.major}.{version_info.minor}'

if current_python_version in invalid_python_versions:
    raise Exception(f'Invalid python version {current_python_version}')
else:
    print('Your python version seems fine. Proceeding ...')