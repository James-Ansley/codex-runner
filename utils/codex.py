import os
from itertools import chain

import openai
from backoff import on_exception, expo
from dotenv import load_dotenv
from openai.error import RateLimitError
from ratelimit import limits, RateLimitException

from utils.question import Question

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_completion(
        question: Question, n: int, temperature: float
) -> list[str]:
    # n is limited to 20 using Edit engine – must be chunked
    chunked_n = [20] * (n // 20)
    if n % 20:
        chunked_n.append(n % 20)
    completion_groups = (
        _generate_completion(question, group, temperature)
        for group in chunked_n
    )
    return list(chain(*completion_groups))


@on_exception(expo, (RateLimitException, RateLimitError), max_tries=8)
@limits(calls=20, period=60)
def _generate_completion(
        question: Question, n: int, temperature: float
) -> list[str]:
    response = openai.Edit.create(
        engine='code-davinci-edit-001',
        instruction=question.prompt,
        input=f'# Python 3\n{question.answer_preload.rstrip()}',
        n=n,
        temperature=temperature,
    )
    answers = [resp['text'].rstrip() for resp in response['choices']]
    return answers
