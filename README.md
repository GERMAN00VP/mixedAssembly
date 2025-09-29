# Viral Window Priors

This repository provides tools to build and use **empirical priors** for sliding windows along viral genomes.  
These priors summarize the expected variability of aligned viral sequences and allow you to later evaluate whether a new sequence behaves "normally" within each genomic region.

---

## 📌 Usage: How to Build a Priors Table

### Step 1: Prepare your alignment
- You need a multiple sequence alignment in **FASTA** format.  
- One sequence must be designated as the **reference**, which defines the coordinate system.  
- All sequences must be aligned and of the same length (with `-` as gaps if needed).

### Step 2: Build priors
Run the following command:

```bash
python build_priors.py \
    -i alignment.fasta \
    -r ReferenceID \
    -o priors.parquet \
    --win 100 \
    --overlap 10
```
### Command Line Arguments

- `-i / --input` → path to your aligned FASTA file.  
- `-r / --ref` → ID of the reference sequence in the alignment.  
- `-o / --output` → output file, stored in compressed **Parquet** format.  
- `--win` → window size in base pairs (default = 100).  
- `--overlap` → overlap between consecutive windows (default = 10).  

The output file will contain a table with one row per genomic window, including:

- `start`, `end` → window coordinates in reference genome.  
- `nLL_p95`, `nLL_p99` → empirical thresholds at 95th and 99th percentiles.  
- `profile` → probability distribution of bases for each position in the window.  

---

## 🧮 Methodology

### 1. Probability distributions per position

For each window of size `W` bases (e.g., `W = 100`), and for each position `j` within that window, we compute the probability of observing each nucleotide:

\[
P_j(b) = \frac{c_j(b) + \alpha}{\sum_{x \in \{A,C,G,T\}} (c_j(x) + \alpha)}
\]

Where:  
- \(c_j(b)\) = number of sequences with base \(b\) at position \(j\).  
- \(\alpha\) = pseudocount (Laplace smoothing, default \(\alpha = 1\)) to avoid zero probabilities.  
- Bases `N` are ignored in the counts.  

This gives a **per-position categorical distribution**.

---

### 2. Log-likelihood of a sequence in a window

Given a query sequence \(Q\), we compute its probability under the window profile.  
For each valid (non-`N`) position \(j\) with observed base \(q_j\):

\[
\log L(Q \mid \text{window}) = \sum_{j=1}^{W} \log P_j(q_j)
\]

The **normalized negative log-likelihood (nLL)** is:

\[
\text{nLL}(Q) = -\frac{1}{N_{\text{valid}}} \sum_{j=1}^{W} \log P_j(q_j)
\]

Where:  
- \(N_{\text{valid}}\) = number of positions in the window where \(Q\) has a non-`N` base.  

Smaller nLL values indicate sequences more likely under the empirical profile.

---

### 3. Empirical priors

To characterize "normal variation" for each window:

1. Score **all sequences** from the alignment against the window profile.  
2. Collect the distribution of nLL values.  
3. Extract percentiles (e.g., 95th and 99th) to serve as thresholds.  

Thus, for each window we store:  
- The **distribution (profile)**.  
- Empirical thresholds: `nLL_p95` and `nLL_p99`.  

A new sequence can later be compared:  
- If `nLL < nLL_p95` → typical.  
- If `nLL > nLL_p99` → unusually variable, possibly unreliable region.

---

## 📦 Output format

The output is a compressed **Parquet** file, optimized for:  
- **Small size** (columnar + Zstandard compression).  
- **Fast filtering and querying** (e.g., with pandas or pyarrow).

**Example of loading priors in Python:**

```python
import pandas as pd

# Load the priors table
df = pd.read_parquet("priors.parquet")
print(df.head())
```
