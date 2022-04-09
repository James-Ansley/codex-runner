import tarfile
from pathlib import PurePath

import docker

_PYTHON_IMAGE = "python:3.10-alpine"
_SEPARATOR = "#<ab@17943918#@>#"
_TAR_PATH = PurePath(__file__).parent / 'runner_script.tar'
_SCRIPT_PATH = PurePath(__file__).parent / 'runner_script.py'


class CodeRunner:
    def __init__(self):
        client = docker.from_env()
        images = client.images.list(filters={"reference": _PYTHON_IMAGE})
        if len(images) == 0:
            client.images.pull(_PYTHON_IMAGE)
        self._container = client.containers.create(_PYTHON_IMAGE, tty=True)
        self._container.start()
        with tarfile.open(_TAR_PATH, "w") as tar:
            tar.add(_SCRIPT_PATH, arcname='runner.py')
        with open(_TAR_PATH, "rb") as tar:
            self._container.put_archive("/", tar)

    def run(self, code, stdin):
        params = f"{code}{_SEPARATOR}{stdin}"
        _, result = self._container.exec_run([
            "/bin/sh", "-c",
            f"python runner.py << EOF\n{params}\nEOF",
        ])
        return result.decode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._container.remove(force=True)
