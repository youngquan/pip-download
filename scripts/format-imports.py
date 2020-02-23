import subprocess
import sys
from pathlib import Path

project_code_dir = "pipdownload"
bin_path = Path(sys.executable).parent

isort_cmd = f"{bin_path / 'isort'} --recursive  --force-single-line-imports --thirdparty {project_code_dir} --apply {project_code_dir} tests"
subprocess.run(isort_cmd, shell=True, check=True)
