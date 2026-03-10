"""
Copyright (c) Simon Schug
All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import uuid
from typing import Annotated

import arviz as az
import bambi as bmb
import numpy as np
import plotly.express as px
import polars as pl
import typer
from plotly.graph_objects import Figure
from scipy.special import logsumexp
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from typer import Argument


def compute_working_memory_features(lf: pl.LazyFrame) -> pl.LazyFrame:
  return lf.with_columns(
    primacy=(1.0 / (pl.col('target_index') + 1.0)),
    recency=(1.0 / (pl.col('set_size') - pl.col('target_index'))),
  ).with_columns(
    [
      (pl.col(name) - pl.col(name).mean()).alias(f'{name}_c')
      for name in ['set_size', 'primacy', 'recency', 'trial']
    ]
  )


def fit_working_memory_model(
  lf: pl.LazyFrame, seed: int
) -> tuple[bmb.Model, az.InferenceData]:
  for key in ['set_size', 'target_index', 'probe_type', 'participant_id', 'hit', 'trial']:
    assert key in lf.collect_schema().names()

  fixed_effects = '1 + set_size_c + primacy_c + recency_c'
  random_effects = '(1 + set_size_c + primacy_c + recency_c | participant_id)'

  model = bmb.Model(
    formula=f'hit ~ {fixed_effects} + {random_effects}',
    data=lf.collect().to_pandas(),
    family='bernoulli',
    link='logit',
    noncentered=True,
    center_predictors=False,
  )

  return (model, model.fit(random_seed=seed))


def compute_log_predictive_density(
  model: bmb.Model, idata: az.InferenceData, lf: pl.LazyFrame, seed: int
) -> pl.LazyFrame:
  """Compute the mean log pointwise predictive density under the posterior."""

  # Ensure the participant IDs are seen as new groups by Bambi
  df = (
    lf.with_columns(participant_id=pl.format('new_{}', pl.col('participant_id')))
    .collect()
    .to_pandas()
  )

  idata_eval = model.predict(
    idata,
    data=df,
    kind='response_params',
    inplace=False,
    sample_new_groups=True,
    random_seed=seed,
  )

  p = idata_eval.posterior['p']
  y = df['hit'].values
  ll = y * np.log(p) + (1 - y) * np.log(1 - p)

  # Marginalize over posterior samples, 'chain' (axis 0) and 'draw' (axis 1).
  n_samples = ll.sizes['chain'] * ll.sizes['draw']
  lppd = logsumexp(ll.values, axis=(0, 1)) - np.log(n_samples)

  return (
    pl.LazyFrame(
      dict(
        participant_id=df['participant_id'].str.removeprefix('new_'),
        score=lppd,
      )
    )
    .group_by('participant_id')
    .mean()
  )


def plot_roc_curves(df_scores: pl.DataFrame) -> Figure:
  human_scores = (
    df_scores.filter(pl.col('participant_type').eq('human'))
    .get_column('score')
    .to_numpy()
  )

  def compute_roc(df_pt: pl.DataFrame) -> pl.DataFrame:
    pt_scores = df_pt.get_column('score').to_numpy()
    labels = np.concatenate([np.ones(len(human_scores)), np.zeros(len(pt_scores))])
    scores = np.concatenate([human_scores, pt_scores])
    fpr, tpr, _ = roc_curve(y_true=labels, y_score=scores)
    auroc = roc_auc_score(y_true=labels, y_score=scores, average='macro')

    return pl.DataFrame(
      {
        'participant_type': df_pt.get_column('participant_type')[0],
        'fpr': fpr,
        'tpr': tpr,
        'auroc': auroc * np.ones_like(tpr),
      }
    )

  # Compute roc curves per participant_type
  df_roc = df_scores.filter(pl.col('participant_type') != 'human')
  df_roc = df_roc.group_by('participant_type').map_groups(compute_roc).to_pandas()
  print(
    'AUROC per participant type\n',
    df_roc.groupby('participant_type').agg({'auroc': 'first'}),
  )

  fig = px.line(
    df_roc,
    x='fpr',
    y='tpr',
    color='participant_type',
    labels={
      'fpr': 'False positive rate',
      'tpr': 'True positive rate',
      'participant_type': 'Participant type',
    },
  )
  fig.add_scatter(
    x=[0, 1],
    y=[0, 1],
    mode='lines',
    line=dict(color='lightgrey', dash='dash'),
    showlegend=False,
  )

  return fig


def generate_mock_participant_trials(
  n_participants: int, n_trials: int, seed: int
) -> pl.LazyFrame:
  """Create participant/trial structure with covariates but no hit column.
  ┌────────────────┬──────────────────┬───────┬──────────┬──────────────┬─────────────┐
  │ participant_id ┆ participant_type ┆ trial ┆ set_size ┆ target_index ┆ probe_type  │
  │ ---            ┆ ---              ┆ ---   ┆ ---      ┆ ---          ┆ ---         │
  │ str            ┆ str              ┆ i64   ┆ i64      ┆ i64          ┆ str         │
  └────────────────┴──────────────────┴───────┴──────────┴──────────────┴─────────────┘
  """
  rng = np.random.default_rng(seed)
  n_samples = n_participants * n_trials

  set_size = rng.integers(3, 13, n_samples)
  target_index = rng.integers(0, set_size)
  probe_type = rng.choice(['position', 'association'], n_samples)
  participant_type = np.repeat(['human', 'llm_a', 'llm_b'], n_participants // 3)

  participants = pl.DataFrame(
    {
      'participant_id': [str(uuid.uuid4())[:8] for _ in range(n_participants)],
      'participant_type': participant_type,
    }
  )
  df = participants.join(pl.DataFrame({'trial': range(n_trials)}), how='cross')

  return df.with_columns(
    set_size=set_size,
    target_index=target_index,
    probe_type=probe_type,
  ).lazy()


def generate_mock_trial_outcomes(lf: pl.LazyFrame, seed: int) -> pl.LazyFrame:
  """Add mock trial outcomes with participant_type dependent working memory profiles."""
  rng = np.random.default_rng(seed)

  # Generate random intercepts and slopes for participants (but only use for humans)
  participant_ids = (
    lf.select('participant_id').unique().collect().get_column('participant_id').sort()
  )
  participant_effects = pl.DataFrame(
    {
      'participant_id': participant_ids,
      'intercept': rng.normal(loc=0.0, scale=0.5, size=len(participant_ids)),
      'slope_set_size': rng.normal(loc=-1.0, scale=0.5, size=len(participant_ids)),
      'slope_primacy': rng.normal(loc=2.0, scale=0.5, size=len(participant_ids)),
      'slope_recency': rng.normal(loc=2.0, scale=0.5, size=len(participant_ids)),
    }
  ).lazy()

  lf = (
    lf.join(participant_effects, on='participant_id', how='left')
    .with_columns(
      eta=(
        pl.col('intercept')
        + pl.col('slope_set_size') * pl.col('set_size_c')
        + pl.col('slope_primacy') * pl.col('primacy_c')
        + pl.col('slope_recency') * pl.col('recency_c')
      )
    )
    .with_columns(p_human=1.0 / (1.0 + (-pl.col('eta')).exp()))
  )

  hit_expr = (
    pl.when(pl.col('participant_type') == 'human')
    .then(
      pl.col('p_human').map_batches(
        lambda s: pl.Series(rng.binomial(n=1, p=s.to_numpy())), return_dtype=pl.Int64
      )
    )
    .when(pl.col('participant_type') == 'llm_a')
    .then(pl.lit(1))
    .otherwise(pl.lit(0))
  )

  return lf.with_columns(hit=hit_expr).drop(
    ['intercept', 'slope_set_size', 'slope_primacy', 'slope_recency', 'eta', 'p_human']
  )


def main(
  n_participants: Annotated[int, Argument(help='Number of fake participants')] = 300,
  n_trials: Annotated[int, Argument(help='Number of fake trials')] = 10,
  test_size: Annotated[float, Argument(help='Fraction used for test set')] = 0.5,
  seed: Annotated[int, Argument(help='Random seed')] = 1,
  data_path: Annotated[
    str, Argument(help='Path to *.parquet file to run with real rather than fake data')
  ] = '',
) -> None:
  if data_path:
    lf = pl.scan_parquet(data_path).pipe(compute_working_memory_features)
    print('Loaded data', lf.collect())
  else:
    # Generate mock data with working memory features
    lf = (
      generate_mock_participant_trials(n_participants, n_trials, seed)
      .pipe(compute_working_memory_features)
      .pipe(generate_mock_trial_outcomes, seed=seed)
    )
    print('Generated mock data', lf.collect())

  # Split data for training and evaluation
  train_human_ids = (
    lf.filter(pl.col('participant_type') == 'human')
    .select('participant_id')
    .unique()
    .collect()
    .get_column('participant_id')
    .sample(fraction=1 - test_size, seed=seed)
    .implode()
  )
  lf_train = lf.filter(pl.col('participant_id').is_in(train_human_ids))
  lf_eval = lf.filter(~pl.col('participant_id').is_in(train_human_ids))

  # Train the anomaly detection model and score new participants
  model, idata = fit_working_memory_model(lf_train, seed=seed)
  lf_lppd = compute_log_predictive_density(model, idata, lf_eval, seed=seed)
  df_lppd = lf_lppd.join(
    lf_eval.select('participant_id', 'participant_type').unique(),
    on='participant_id',
    how='left',
  ).collect()
  print(
    'Average LPPD per participant type \n',
    df_lppd.group_by('participant_type').mean().drop(pl.col('participant_id')),
  )

  # Plot ROC per participant type
  fig = plot_roc_curves(df_lppd)
  fig.show()

  # Label anomalies using a very basic threshold selection criterium
  # In practice, threshold should be selected more carefully (e.g. using cross-validation)
  df_lppd = df_lppd.with_columns(
    is_anomaly=pl.col('score')
    < pl.col('score').filter(pl.col('participant_type') == 'human').min()
  )
  print(df_lppd)


if __name__ == '__main__':
  typer.run(main)
