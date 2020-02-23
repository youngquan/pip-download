import subprocess
import sys
from pathlib import Path

project_code_dir = "pipdownload"
bin_path = Path(sys.executable).parent

autoflake_cmd = f"{bin_path / 'autoflake'} --remove-all-unused-imports --recursive --remove-unused-variables --in-place {project_code_dir} tests --exclude=__init__.py"
subprocess.run(autoflake_cmd, shell=True, check=True)

black_cmd = f"{bin_path / 'black'} {project_code_dir} tests"
subprocess.run(black_cmd, shell=True, check=True)

isort_cmd = f"{bin_path / 'isort'} --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --thirdparty {project_code_dir} --apply {project_code_dir} tests"
subprocess.run(isort_cmd, shell=True, check=True)
