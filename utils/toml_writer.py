# Horrible manual toml generation
# because no package writes NICE looking toml files

def question_to_toml(question):
    return ("[[questions]]\n"
            f"id = '{question.id}'\n"
            "prompt = '''\n"
            f"{question.prompt}'''\n"
            f"answer_preload = '''{question.answer_preload}'''\n\n"
            + ('\n\n'.join(answer_as_toml(c)
                           for c in question.completions)
               if question.completions else '')
            + ('\n\n' if question.testcases and question.completions else '')
            + ('\n\n'.join(testcase_as_toml(tc) for tc in question.testcases)
               if question.testcases else ''))


def testcase_as_toml(case):
    nl = '\n'
    return '\n'.join((
        f"[[questions.testcases]]",
        f"code = '''{nl if nl in case.code else ''}{case.code}'''",
        f"stdin = '''{nl if nl in case.stdin else ''}{case.stdin}'''",
        f"expect = '''{nl if nl in case.expect else ''}{case.expect}'''",
    ))


def answer_as_toml(answer):
    test_results = ", ".join("true" if res else "false"
                             for res in answer.results)
    return '\n'.join((
        "[[questions.completions]]",
        f"completion = '''\n{answer.completion.rstrip()}\n'''",
        (f'results = '
         f'[{test_results}]'
         if answer.results else '')
    ))
