import textwrap
from contextlib import contextmanager

import docker as docker


@contextmanager
def make_container():
    """
    A context manager to handle setting up and tearing down a docker container.
    """
    client = docker.from_env()
    client.images.pull("python:3.10-alpine")
    container = client.containers.create(
        "python:3.10-alpine",
        read_only=True,
        tty=True,
    )
    container.start()
    try:
        yield container
    finally:
        container.stop()
        container.remove()


def _run_code(container, code, stdin=None):
    if stdin:
        code = _prefix_stdin(code, stdin)
    _, output = container.exec_run(
        ['python', '-c', code],
        stderr=True,
    )
    return output.decode().rstrip('\n')


def _prefix_stdin(code, stdin):
    """
    A horrible hack to make stdin work – might just be best to not use
    questions that require stdin. Partly taken from the coderunner
    python3_w_input qtype.
    """
    prefix = textwrap.dedent(f'''
        import sys
        from io import StringIO
        sys.stdin = StringIO("""{stdin.encode('unicode_escape').decode()}""")
        __saved_input__ = input
        def input(prompt=''):
            s = __saved_input__(prompt)
            print(s)
            return s
        ''')
    return prefix + '\n\n' + code


def run_test(container, testcase, answer):
    test_code = answer.completion + '\n\n' + testcase.code
    result = _run_code(container, test_code, testcase.stdin)
    answer.results.append(result.strip() == testcase.expect.strip())
