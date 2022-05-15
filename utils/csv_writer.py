from statistics import mean, median, stdev

import list2csv


def write_csv_data(f, questions, test_case_strategy, question_scoring_strategy):
    scores = [
        question_scoring_strategy(question.completions, test_case_strategy)
        for question in questions
    ]

    writer = list2csv.Writer(f)
    writer.add_column('qid', lambda q_s: q_s[0].id)
    writer.add_multi(
        'response {}',
        lambda q_s: q_s[1],
        len(scores[0]),
        '{:.4f}',
        aggregate_ids={'scores'},
    )
    writer.add_aggregator('scores', 'average', mean, '{:.4f}')
    writer.add_aggregator('scores', 'median', median, '{:.4f}')
    writer.add_aggregator('scores', 'min', min, '{:.4f}')
    writer.add_aggregator('scores', 'max', max, '{:.4f}')
    writer.write_header()
    writer.write_all(zip(questions, scores))
