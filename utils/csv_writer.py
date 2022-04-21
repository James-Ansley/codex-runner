from statistics import mean, median, stdev

import list2csv


def write_csv_data(f, questions, strategy, aggregation):
    num_completions = len(questions[0].completions)
    writer = list2csv.Writer(f)
    writer.add_column('qid', 'id')
    writer.add_multi(
        'response {}',
        lambda q: aggregation(q.completions, strategy),
        num_completions,
        '{:.4f}',
        aggregate_ids={'scores'},
    )
    writer.add_aggregator('scores', 'average', mean, '{:.4f}')
    writer.add_aggregator('scores', 'median', median, '{:.4f}')
    writer.add_aggregator('scores', 'stdev', stdev, '{:.4f}')
    writer.add_aggregator('scores', 'min', min, '{:.4f}')
    writer.add_aggregator('scores', 'max', max, '{:.4f}')
    writer.write_header()
    writer.write_all(questions)
