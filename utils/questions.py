from dataclasses import dataclass, field
from typing import BinaryIO, TextIO

import tomli

from utils.codex_api import generate_completion
from utils.toml_writer import question_to_toml

SEPARATOR = "#<ab@17943918#@>#"
PRINT_SEPARATOR = f'\nprint("{SEPARATOR}")\n'


@dataclass
class Testcase:
    code: str
    stdin: str
    expect: str


@dataclass
class Answer:
    completion: str
    results: list[bool] = field(default_factory=list)


@dataclass
class Question:
    id: str
    prompt: str
    answer_preload: str = None
    testcases: list['Testcase'] = field(default_factory=list)
    completions: list['Answer'] = field(default_factory=list)

    @property
    def codex_prompt(self):
        if self.answer_preload is None:
            return self.prompt
        return self.prompt + '\n\n' + self.answer_preload

    def generate_completions(self, n, temperature, max_tokens):
        self.completions.extend(
            [Answer(completion) for completion in
             generate_completion(self, n, temperature, max_tokens)]
        )

    @classmethod
    def load_from_toml(cls, f: BinaryIO):
        data = tomli.load(f)['questions']
        questions = []
        for qdata in data:
            testcases = [Testcase(**tc) for tc in qdata.pop('testcases', [])]
            completions = [Answer(**c)
                           for c in qdata.pop('completions', [])]
            questions.append(cls(
                **qdata,
                testcases=testcases,
                completions=completions
            ))
        return questions

    @staticmethod
    def write_to_toml(questions, f: TextIO):
        f.write('\n\n\n\n'.join(question_to_toml(q) for q in questions))
