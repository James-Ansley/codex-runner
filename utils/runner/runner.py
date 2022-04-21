import tarfile
from collections.abc import Iterable
from pathlib import PurePath

import docker

from utils.question import SupportFile

_PYTHON_IMAGE = "python:3.10-alpine"
_SEPARATOR = "#<ab@17943918#@>#"
_TAR_PATH = PurePath(__file__).parent / "runner_script.tar"
_SCRIPT_PATH = PurePath(__file__).parent / "runner_script.py"
_DOCKER_WORKING_DIRECTORY = "/code_runner"


class CodeRunner:
    def __init__(self, files: Iterable[SupportFile] = tuple()):
        self._get_image()
        self._container = self._make_container()
        self._export_runner_script()
        self._export_support_files(files)

    def run(self, code, stdin):
        params = f"{code}{_SEPARATOR}{stdin}"
        _, result = self._container.exec_run(
            [
                "/bin/sh", "-c",
                f"python runner.py << EOF\n{params}\nEOF",
            ],
            workdir=_DOCKER_WORKING_DIRECTORY
        )
        return result.decode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._container.remove(force=True)

    @staticmethod
    def _get_image():
        client = docker.from_env()
        images = client.images.list(filters={"reference": _PYTHON_IMAGE})
        if len(images) == 0:
            client.images.pull(_PYTHON_IMAGE)

    @staticmethod
    def _make_container():
        client = docker.from_env()
        container = client.containers.create(_PYTHON_IMAGE, tty=True)
        container.start()
        container.exec_run([
            "/bin/sh", "-c",
            f"mkdir {_DOCKER_WORKING_DIRECTORY}",
        ])
        return container

    def _export_runner_script(self):
        with tarfile.open(_TAR_PATH, "w") as tar:
            tar.add(_SCRIPT_PATH, arcname='runner.py')
        with open(_TAR_PATH, "rb") as tar:
            self._container.put_archive(_DOCKER_WORKING_DIRECTORY, tar)

    def _export_support_files(self, support_files: Iterable[SupportFile]):
        for file in support_files:
            self._container.exec_run(
                [
                    "/bin/sh", "-c",
                    f"cat << EOF > {file.name}\n{file.text}\nEOF"
                ],
                workdir=_DOCKER_WORKING_DIRECTORY
            )
