import typer
from tqdm import tqdm
from typer import Option, Argument

from utils.codex import generate_completion
from utils.csv_writer import write_csv_data
from utils.question import Question, Completion, TestResult
from utils.runner.runner import CodeRunner

app = typer.Typer()


def bar(prefix, iterable):
    return tqdm(
        iterable,
        desc=prefix,
        bar_format='{desc:>25}{percentage:3.0f}%|{bar:100}{r_bar}',
        leave=False,
    )


@app.command(help="Generates Completions")
def gen(
        in_: str = Argument(..., help="Input TOML file path"),
        out: str = Argument(..., help="Output TOML file path"),
        n: int = Option(1, help="Number of completions to generate"),
        temp: float = Option(
            0.9, help="Temperature to use when generating completions"
        )
):
    with open(in_, 'rb') as f:
        questions = Question.load_all_from_toml(f)
    for q in bar("Answering Questions", questions):
        q.completions = [
            Completion(result) for result in generate_completion(q, n, temp)
        ]
    with open(out, 'w') as f:
        f.write(Question.dump_all(questions))


@app.command(help="Runs questions with completions against test cases.")
def check(
        in_: str = Argument(..., help="Input TOML file path with completions"),
        out: str = Argument(..., help="Output TOML file path"),
):
    with open(in_, 'rb') as f:
        questions = Question.load_all_from_toml(f)
    with CodeRunner() as cr:
        _run_checks(questions, cr)
    with open(out, 'w') as f:
        f.write(Question.dump_all(questions))


def _run_checks(questions, cr):
    for q in bar("Grading Questions", questions):
        for cmp in bar("Checking Answer", q.completions):
            for tc in bar("Against Testcase", q.testcases):
                output = cr.run(tc.make_code(cmp.code), tc.stdin)
                result = TestResult(tc, output)
                cmp.results.append(result)


@app.command(help="Generates summary CSV file")
def summary(
        in_: str = Argument(
            ..., help="Input TOML file path with scored completions"
        ),
        out: str = Argument(..., help="Output CSV file path"),
):
    with open(in_, 'rb') as f:
        questions = Question.load_all_from_toml(f)
    with open(out, 'w') as f:
        write_csv_data(f, questions)


if __name__ == '__main__':
    app()
