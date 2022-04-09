from dataclasses import dataclass, field
from typing import BinaryIO

import tomli


@dataclass
class Question:
    id: str
    prompt: str
    answer_preload: str = None
    testcases: list['Testcase'] = field(default_factory=list)
    completions: list['Completion'] = field(default_factory=list)

    @classmethod
    def load_all_from_toml(cls, f: BinaryIO):
        data = tomli.load(f)
        return [Question.from_toml(q_data) for q_data in data['questions']]

    @staticmethod
    def dump_all(questions):
        return "\n\n".join(q.to_toml() for q in questions)

    @classmethod
    def from_toml(cls, data):
        testcases = [Testcase.from_toml(tc)
                     for tc in data.pop('testcases', [])]
        completions = [Completion.from_toml(c)
                       for c in data.pop('completions', [])]
        return (cls(
            **data,
            testcases=testcases,
            completions=completions
        ))

    def to_toml(self):
        return "\n".join((
            "[[questions]]",
            f"id = '{self.id}'",
            f"prompt = '''\n{self.prompt}\n'''",
            (
                f"answer_preload = '''\n{self.answer_preload.rstrip()}\n'''"
                if self.answer_preload else
                "answer_preload = ''"
            ),
            "",
            ("\n\n".join(comp.to_toml() for comp in self.completions)),
            "",
            ("\n\n".join(tc.to_toml() for tc in self.testcases)),
        ))


@dataclass
class Testcase:
    code: str
    stdin: str
    expect: str

    def make_code(self, completion_code):
        return f"{completion_code}\n\n{self.code}"

    def to_toml(self):
        return "\n".join((
            "[[questions.testcases]]",
            (f"code = '''\n{self.code}\n'''" if self.code else "code = ''"),
            (f"stdin = '''\n{self.stdin}\n'''" if self.stdin else "stdin = ''"),
            (f"expect = '''\n{self.expect}\n'''"
             if self.expect else "expect = ''"),
        ))

    @classmethod
    def from_toml(cls, data):
        return cls(
            data['code'].rstrip(),
            data['stdin'].rstrip(),
            data['expect'].rstrip(),
        )


@dataclass
class Completion:
    code: str
    results: list['TestResult'] = field(default_factory=list)

    def to_toml(self):
        return "\n".join((
            "[[questions.completions]]",
            f"code = '''\n{self.code}\n'''",
            ("\n".join(tr.to_toml() for tr in self.results))
        ))

    @classmethod
    def from_toml(cls, data):
        results = [TestResult.from_toml(tr)
                   for tr in data.pop('test_results', [])]
        return cls(**data, results=results)


@dataclass
class TestResult:
    testcase: 'Testcase'
    got: str

    @property
    def is_correct(self):
        return self.testcase.expect.strip() == self.got.strip()

    def to_toml(self):
        return "\n".join((
            "[[questions.completions.test_results]]",
            (f"code = '''\n{self.testcase.code}\n'''"
             if self.testcase.code else "code = ''"),
            (f"stdin = '''\n{self.testcase.stdin}\n'''"
             if self.testcase.stdin else "stdin = ''"),
            (f"expect = '''\n{self.testcase.expect}\n'''"
             if self.testcase.expect else "expect = ''"),
            (f"got = '''\n{self.got.strip()}\n'''"
             if self.got.strip() else "got = ''"),
        ))

    @classmethod
    def from_toml(cls, data):
        got = data.pop('got', '').rstrip()
        return cls(Testcase(**data), got)