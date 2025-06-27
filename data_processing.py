
"""data_processing.py – merge raw JSONL to tidy parquet."""
import json, pathlib, pandas as pd
raw_dir = pathlib.Path('data/raw')
files = list(raw_dir.glob('*.jsonl'))
dfs = [pd.read_json(f, lines=True) for f in files]
if not dfs:
    print('No raw files'); exit()
df = pd.concat(dfs, ignore_index=True)
# toy skill extraction
df['skills'] = df['title'].fillna('').str.lower().str.split().apply(lambda L: [w for w in L if len(w) > 2])
df.to_parquet('data/jobs.parquet', index=False)
print('Wrote', len(df), 'rows to data/jobs.parquet')
