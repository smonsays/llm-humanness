# Cognitive anomaly detection

Run the cognitive anomaly detection pipeline with fake data using

```bash
uv run detection.py
```

Use `--help` to see options

```bash
$ uv run detection.py --help
                                                                                  
 Usage: detection.py [OPTIONS] [N_PARTICIPANTS] [N_TRIALS] [TEST_SIZE] [SEED]     
                     [DATA_PATH]                                                  
                                                                                  
╭─ Arguments ────────────────────────────────────────────────────────────────────╮
│   n_participants      [N_PARTICIPANTS]  Number of fake participants            │
│                                         [default: 300]                         │
│   n_trials            [N_TRIALS]        Number of fake trials [default: 10]    │
│   test_size           [TEST_SIZE]       Fraction used for test set             │
│                                         [default: 0.5]                         │
│   seed                [SEED]            Random seed [default: 1]               │
│   data_path           [DATA_PATH]       Path to *.parquet file to run with     │
│                                         real rather than fake data             │
╰────────────────────────────────────────────────────────────────────────────────╯
```
