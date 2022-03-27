import os

import openai
from backoff import on_exception, expo
from dotenv import load_dotenv
from openai.error import RateLimitError
from ratelimit import limits, RateLimitException

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


@on_exception(expo, (RateLimitException, RateLimitError), max_tries=8)
@limits(calls=20, period=60)
def generate_completion(
        question: 'Question', n: int, temperature: float, max_tokens: int
) -> list[str]:
    # See https://beta.openai.com/docs/api-reference/completions/create
    response = openai.Completion.create(
        engine="code-davinci-002",
        prompt=question.codex_prompt,
        n=n,
        temperature=temperature,
        # len prompt // 4 approx offsets prompt tokens
        max_tokens=max_tokens + len(question.codex_prompt) // 4,
    )
    answers = [resp['text'].rstrip() for resp in response['choices']]
    if question.answer_preload is not None:
        answers = [question.answer_preload + answer for answer in answers]
    return answers
