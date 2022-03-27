# Codex Runner

Small CLI tool to bulk generate OpenAI Codex completions to simple prompts and
check completions against test suites.

## Requirements

The requirements are listed in `requirements.txt`. One note is, if you intend to
use these scripts to automatically test code, you must have docker running on
your computer.

You must include a `.env` file that contains your `OPENAI_API_KEY`.

## Usage

These scripts are intended to be run sequentially with the output of each
command being checked and cleaned before progressing. The intended sequence of
commands is:

### 1. Generating completions

Example:

```
python codex_runner.py generate-completions data/qdata.toml data/qdata_w_completions.toml --n 50 --max-tokens 32
```

Here, the `generate-completions` command takes input and output toml file paths
as required arguments. The toml file format is described below. Question data is
read from the input TOML file and OpenAI Codex is used to generate completions
which will then written to the output TOML file along with the question data.
OpenAI Codex will often include trailing code which needs to be deleted. It is
recommended you manually clean the completion data to remove this. If you do not
intend to automatically run the completed code through unit tests (e.g. you are
using this for EiPE questions), you can stop at this step.

Optional parameters include:

- `--n`: The number of completions to generate per question
- `--max-tokens`: defaults to 16 (OpenAI's default), signifies the approximate
  number of additional tokens that will be generated
- `--temperature`: defaults to 0.9, controls the temperature of attempts

### 2. Running Tests

Example:

```
python codex_runner.py run-tests data/qdata_w_completions.toml data/qdata_w_tests.toml
```

This will run the completions against the provided test cases and write question
data with additional test case data to the output file.

### 3. Generating a Report

Example:

```
python codex_runner.py write-results data/qdata_w_tests.toml results.csv
```

Writes ratio of passing test cases (i.e. score out of 1) for each completion to
columns in a CSV along with aggregate stats such as mean etc.

## TOML File Format

Questions are represented as an array of tables. Minimally, to get started with
step 1 of the scripts you will need a toml file with the following structure:

```toml
[[questions]]
id = 'some_unique_name'
prompt = '''
The exact prompt that will be given to codex
'''
# Optional answer preload that will be appended to the prompt and prepended to completions
answer_preload = 'def foo(bar):'

# Optional testcases if you intend to automatically test completions
[[questions.testcases]]
# Code will be appended to the completion to create a runnable test
code = '''
foo('Baz')
'''
# Stdin that will effectively be piped to the test case
stdin = ''''''
# expected output from stdout that will be checked against the actual output of the test case
expect = '''How much foo could a foo bar bar if a foo bar could bar foo!'''
```

During steps 1 and 2 of the scripts the following information will be added to
the generated TOML files:

```toml
[[questions]]
...  # question info

# Step 2 completions (the output of codex are added)
# These will usually neeed to be manually checked and cleaned
[[questions.completions]]
completion = '''
def foo(bar):
    baz = bar * 5
    print(baz)
'''
# In step 3 the results of the test cases are added
results = [false, true, true]

...  # test cases
```
