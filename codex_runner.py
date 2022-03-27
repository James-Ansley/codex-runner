import typer
from tqdm import tqdm
from typer import Argument, Option

from utils.code_runner import make_container, run_test
from utils.csv_writer import write_csv_data
from utils.questions import Question

QDATA_HELP = "The directory of the TOML containing question data"
N_HELP = \
    "The number of completions that will be generated for each question"
TEMP_HELP = "The temperature used for completions"
MAX_TOKENS_HELP = "The approximate tokens in addition to prompts"
OUTPUT_COMPLETIONS_HELP = \
    "The directory that will be written to with question data containing " \
    "completions"
OUTPUT_TESTS_HELP = \
    "The directory that will be written to with question data containing " \
    "test results"
OUTPUT_WRITE_HELP = \
    "The directory that will be written to containing average test scores"

app = typer.Typer()


def bar(prefix, iterable):
    return tqdm(
        iterable,
        desc=prefix,
        bar_format='{desc:>25}{percentage:3.0f}%|{bar:100}{r_bar}',
        leave=False,
    )


@app.command(
    help="Outputs question data with OpenAI Codex completions to a TOML file."
)
def generate_completions(
        qdata: str = Argument(..., help=QDATA_HELP),
        output: str = Argument(..., help=OUTPUT_COMPLETIONS_HELP),
        n: int = Option(1, help=N_HELP),
        temperature: float = Option(0.9, help=TEMP_HELP),
        max_tokens: int = Option(16, help=MAX_TOKENS_HELP),
):
    with open(qdata, 'rb') as f:
        questions = Question.load_from_toml(f)
    for question in bar('Generating Completions', questions):
        question.generate_completions(n, temperature, max_tokens)
    with open(output, 'w') as f:
        Question.write_to_toml(questions, f)


@app.command(help="Runs question completions against test cases.")
def run_tests(
        qdata: str = Argument(..., help=QDATA_HELP),
        output: str = Argument(..., help=OUTPUT_TESTS_HELP)
):
    with open(qdata, 'rb') as f:
        questions = Question.load_from_toml(f)
    with make_container() as container:
        _run_tests(container, questions)
    with open(output, 'w') as f:
        Question.write_to_toml(questions, f)


def _run_tests(container, questions):
    for question in bar('Processing Questions', questions):
        for test in bar('Running Test', question.testcases):
            for answer in bar('Checking Answer', question.completions):
                run_test(container, test, answer)


@app.command(help="Writes average test scores to CSV")
def write_results(
        qdata: str = Argument(..., help=QDATA_HELP),
        output: str = Argument(..., help=OUTPUT_WRITE_HELP)
):
    with open(qdata, 'rb') as f:
        questions = Question.load_from_toml(f)
    with open(output, 'w') as f:
        write_csv_data(f, questions)


if __name__ == '__main__':
    app()
