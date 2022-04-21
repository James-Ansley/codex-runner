from collections.abc import Callable
from dataclasses import dataclass, field
from typing import BinaryIO

import tomli


@dataclass
class Question:
    id: str
    prompt: str
    answer_preload: str = ''
    testcases: list['Testcase'] = field(default_factory=list)
    completions: list['Completion'] = field(default_factory=list)
    support_files: list['SupportFile'] = field(default_factory=list)

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
        support_files = [SupportFile.from_toml(sf)
                         for sf in data.pop('support_files', [])]
        return cls(
            **data,
            testcases=testcases,
            completions=completions,
            support_files=support_files,
        )

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
            "",
            ("\n\n".join(sf.to_toml() for sf in self.support_files)),
        ))


@dataclass
class SupportFile:
    name: str
    text: str

    @classmethod
    def from_toml(cls, data):
        return cls(**data)

    def to_toml(self):
        return "\n".join((
            "[[questions.support_files]]",
            f"name = '{self.name}'",
            f"text = '''{self.text}'''"
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

    def score(self, strategy: Callable[..., float]):
        return strategy(self.testcase.expect, self.got)

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
        data.pop('is_correct')
        return cls(Testcase(**data), got)
