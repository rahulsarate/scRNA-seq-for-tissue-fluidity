import pandas as pd, numpy as np, anndata as ad, gc, time, traceback, sys, gzip, shutil
from scipy.sparse import csr_matrix, vstack as sparse_vstack
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
base = Path('data/counts/GSE234269/extracted')

samples = [
    ('GSM7461430_3d_wound_3DE_genematrix.csv.gz', 'wound_3d', '3d'),
    ('GSM7461431_7d_wound_3DE_genematrix.csv.gz', 'wound_7d', '7d'),
    ('GSM7461432_14d_wound_3DE_genematrix.csv.gz', 'wound_14d', '14d'),
]

for fname, condition, tp in samples:
    out = Path(f'data/counts/GSE234269/GSE234269_{condition}.h5ad')
    if out.exists():
        print(f'SKIP {condition}: {out} exists')
        continue
    try:
        t0 = time.time()
        gz_path = base / fname
        
        # Read gzip CSV directly with python engine (avoids C tokenizer gzip bug)
        print(f'Reading {condition} with python engine ...')
        
        chunks = []
        genes = []
        barcodes = None
        for i, chunk in enumerate(pd.read_csv(gz_path, index_col=0, compression='gzip',
                                               chunksize=500, engine='python')):
            if barcodes is None:
                barcodes = chunk.columns.tolist()
            genes.extend(chunk.index.astype(str).tolist())
            sparse_chunk = csr_matrix(chunk.values, dtype=np.float32)
            chunks.append(sparse_chunk)
            del chunk
            if (i+1) % 10 == 0:
                print(f'  ...{len(genes)} genes')
        
        print(f'  {len(genes)} genes total, stacking {len(chunks)} chunks...')
        gxc = sparse_vstack(chunks, format='csr')
        del chunks
        gc.collect()
        
        print(f'  Transposing {gxc.shape} ...')
        X = gxc.T.tocsr()
        del gxc
        gc.collect()
        
        print(f'  Creating AnnData {X.shape} ...')
        adata = ad.AnnData(X=X, obs=pd.DataFrame(index=barcodes), var=pd.DataFrame(index=genes))
        adata.var_names_make_unique()
        adata.obs_names_make_unique()
        adata.obs['sample'] = condition
        adata.obs['condition'] = condition
        adata.obs['timepoint'] = tp
        adata.obs['dataset'] = 'GSE234269'
        adata.obs['organism'] = 'Mus musculus'
        del X
        gc.collect()
        
        print(f'  Writing {out} ...')
        adata.write_h5ad(str(out))
        sz = out.stat().st_size / 1e6
        print(f'  OK: {adata.n_obs} cells x {adata.n_vars} genes, {sz:.1f} MB, {time.time()-t0:.1f}s')
        del adata
        gc.collect()
    except Exception as e:
        traceback.print_exc()
        print(f'  FAILED: {condition}: {e}')

print('All done')
