import subprocess
import sys

stdin = sys.stdin.read()
code, stdin = stdin.split("#<ab@17943918#@>#")

code = f"""
import sys
__saved_input__ = input
def input(prompt=""):
    s = __saved_input__(prompt)
    print(s)
    return s
    
{code}
"""

process = subprocess.Popen(
        ["python3", "-c", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        text=True,
)
try:
    output, _ = process.communicate(input=stdin, timeout=1)
except subprocess.TimeoutExpired:
    output = "*** TIMEOUT ***"
print(output)
