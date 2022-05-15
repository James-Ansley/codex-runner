# Codex Runner

Scripts to assist in using OpenAI Codex to generate completions to questions.

## Usage

You must have docker running on your machine to run the automatic checking
functionality of these scripts.

You must have a `.env` file with your `OPENAI_API_KEY` set.

### Available Commands:

```text
Usage: codex_runner.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  gen      Generates Completions
  summary  Generates summary CSV file
  test     Runs questions with completions against test cases.
```

### Command: `gen`

```text
Usage: codex_runner.py gen [OPTIONS] IN OUT

  Generates Completions

Arguments:
  IN   Input TOML file path  [required]
  OUT  Output TOML file path  [required]

Options:
  --n INTEGER   Number of completions to generate  [default: 1]
  --temp FLOAT  Temperature to use when generating completions  [default: 0.9]
  --help        Show this message and exit.
```

e.g.

```text
python codex_runner.py gen data/qdata.toml data/qdata_comp.toml --n 10
```

### Command: `test`

```text
Usage: codex_runner.py test [OPTIONS] IN OUT

  Runs questions with completions against test cases.

Arguments:
  IN   Input TOML file path with completions  [required]
  OUT  Output TOML file path  [required]

Options:
  --help  Show this message and exit.
```

e.g.

```text
python codex_runner.py test data/qdata_comp.toml data/qdata_checked.toml
```

### Command: `summary`

```text
Usage: codex_runner.py summary [OPTIONS] IN OUT

  Generates summary CSV file

Arguments:
  IN   Input TOML file path with scored completions  [required]
  OUT  Output CSV file path  [required]

Options:
  --test-strat [exact|fuzzy_w_cutoff|fuzzy]
                                  Strategy to use when testing completion
                                  correctness  [default: Options.exact]
  --scoring-strat [basic|expected|finite-expected|all-or-nothing]
                                  Strategy to use when scoring questions
                                  [default: Options.basic]
  --help                          Show this message and exit.

```

e.g.

```text
python codex_runner.py summary data/qdata_checked.toml data/results.csv --test-strat fuzzy
```

#### Strategies

**Test Strategies**

Test strategies are used to score the expected vs actual results of testcases.
They are:

- *exact*: 0 or 1 based on a strict equality check between the expected vs
  actual output
- *fuzzy*: Indel distance ratio (weighted levenshtein distance) between expected
  vs actual output
- *fuzzy_w_cutoff*: 0 or 1 based on an Indel distance ratio (weighted
  levenshtein distance) between expected vs actual output being above 90

**Scoring Strategies**

Scoring strategies are used to give an overall mark to an attempt – combining
one or several responses. They are:

- _basic_: reports average number of passing testcases for each completion
- _expected_: reports the approximate expected score codex would get with
  infinite attempts using the following penalty scheme:
  (`1.0, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.5, ...`).
- _finite-expected_: Uses the above penalty scheme but is limited to 12 attempts
- _all-or-nothing_: gives 1 for each completion that passes all test cases and 
  0 otherwise.

### Question Format

To start, question data must be added to a TOML file that contains for each
question:

- A unique ID
- A prompt
- An answer preload (optional but recommended)
- Several testcases each containing (optional):
    - Code
    - Stdin
    - Expected output
- Several support files that will be placed in the working dir each containing
  (optional):
    - Name
    - Text

Additional data will be generated by these scripts that does not need to be
manually added.

The general TOML format is as follows:

```toml
# You can have several questions in one file
[[questions]]
id = 'greeting'
prompt = '''
Write a function called greeting(name) that takes a name as input and prints Hello, <name>! as in the examples below.

>>> greeting("James")
Hello, James!
>>> greeting("Sue")
Hello, Sue!
'''
# Optional but recommended a function header is included here.
answer_preload = '''
def greeting(name):
'''

# Generated by running the gen and check commands
# You do not need to write these yourself
[[questions.completions]]
code = '''
# Python 3
def greeting(name):
    print(f"Hello, {name}!")
'''
[[questions.completions.test_results]]
code = '''
greeting("James")
'''
stdin = ''
expect = '''
Hello, James!
'''
got = '''
Hello, James!
'''
[[questions.completions.test_results]]
code = '''
greeting("Sue")
'''
stdin = ''
expect = '''
Hello, Sue!
'''
got = '''
Hello, Sue!
'''

# Optional – You will need to write testcases yourself
# If no testcases are provided you will not be able to auto-mark questions
[[questions.testcases]]
code = '''
greeting("James")
'''
stdin = ''
expect = '''
Hello, James!
'''

[[questions.testcases]]
code = '''
greeting("Sue")
'''
stdin = ''
expect = '''
Hello, Sue!
'''

# Optional – You will need to write these yourself
# These will be added to the working directory as files
[[questions.support_files]]
name = 'my_file.txt'
text = '''some file data'''

[[questions.support_files]]
name = 'my_other_file.txt'
text = '''some file data
in another file.'''
```
