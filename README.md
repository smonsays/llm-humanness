# Are they human? Detecting large language models by probing human memory constraints

This repository contains code accompanying the paper [Are they human? Detecting large language models by probing human memory constraints](https://arxiv.org/abs/2604.00016).

## Structure

- [`/detection`](https://github.com/smonsays/llm-humanness/tree/main/detection) contains code and instructions for running the LLM detection pipeline
- [`/experiment`](https://github.com/smonsays/llm-humanness/tree/main/experiment) contains code and instructions for running the smile-based online experiment

## Abstract

The validity of online behavioral research relies on study participants being human rather than machine.
In the past, it was possible to detect machines by posing simple challenges that were easily solved by humans but not by machines.
General-purpose agents based on large language models (LLMs) can now solve many of these challenges, threatening the validity of online behavioral research.
Here we explore the idea of detecting humanness by using tasks that machines can solve too well to be human.
Specifically, we probe for the existence of an established human cognitive constraint: limited working memory capacity.
We show that cognitive modeling on a standard serial recall task can be used to distinguish online participants from LLMs even when the latter are specifically instructed to mimic human working memory constraints.
Our results demonstrate that it is viable to use well-established cognitive phenomena to distinguish LLMs from humans.

## Citation

```bibtex
@article{schug2026llmhumanness,
  title={Are they human? Detecting large language models by probing human memory constraints},
  author={Schug, Simon and Lake, Brenden M.},
  year={2026},
  url={https://arxiv.org/abs/2604.00016},
  journal={arXiv preprint arXiv:2604.00016}
}
```
