#!/usr/bin/env python3
"""
Command-line script to run the Mixed Assembly pipeline.

Usage example:
python run_mixed_assembly.py \
  --input /path/to/alignment.aln \
  --ref REF_ID_IN_ALIGNMENT \
  --prior /path/to/priors.parquet \
  --output_dir /path/to/output_dir

This script performs:
 1) loads alignment (expects a function load_alignment in utils.py)
 2) extracts reference coordinates via extract_ref_positions (from utils.py)
 3) creates sliding windows (sliding_windows from utils.py)
 4) scores windows and decides QC (create_windows_df)
 5) builds consensus from windows (create_consensus)
 6) re-inserts IRMA insertions removed by initial filtering (add_irma_insertions)
 7) writes results: windows_trace.csv, final fasta and qc.json
"""
import argparse
import logging
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Import helper functions from the package modules
from .utils_mixed_assembly import (
    create_windows_df,
    create_consensus,
    add_irma_insertions,
    qc_process,
    logger as um_logger
)

from .utils import load_alignment, extract_ref_positions, sliding_windows


# configure top-level logger
logger = logging.getLogger("run_mixed_assembly")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(um_logger.handlers[0].formatter)
logger.addHandler(ch)


def parse_args():
    p = argparse.ArgumentParser(description="Run Mixed Assembly pipeline (IRMA + ABACAS mix)")
    p.add_argument("--input", required=True, type=Path, help="Path to input alignment file (.aln)")
    p.add_argument("--ref", required=True, type=str, help="Reference sequence ID present in the alignment file")
    p.add_argument("--prior", required=True, type=Path, help="Path to prior parquet file")
    p.add_argument("--output_dir", required=True, type=Path, help="Output directory to write results")
    return p.parse_args()


def main():
    args = parse_args()
    input_path: Path = args.input
    ref_id: str = args.ref
    prior_path: Path = args.prior
    output_dir: Path = args.output_dir

    try:
        # Basic validations
        if not input_path.exists():
            logger.error("Input alignment file not found: %s", input_path)
            sys.exit(2)
        if not prior_path.exists():
            logger.error("Prior file not found: %s", prior_path)
            sys.exit(2)

        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Output directory: %s", output_dir)

        # Read prior table
        logger.info("Loading prior table from %s", prior_path)
        prior_table = pd.read_parquet(prior_path)

        # Load alignment
        logger.info("Loading alignment from %s", input_path)
        ids, seqs = load_alignment(str(input_path))
        original_seqs = {ids[index]: seqs[index] for index in range(len(ids))}

        if ref_id not in ids:
            logger.error("Reference id '%s' not found in alignment IDs", ref_id)
            sys.exit(2)

        # Filter alignment by reference coordinates
        logger.info("Extracting reference-coordinates sequences using ref id '%s'", ref_id)
        seqs_filtered, ref_seq = extract_ref_positions(ids=ids, seqs=seqs, ref_id=ref_id)
        filtered_seqs = {ids[index]: seqs_filtered[index] for index in range(len(ids))}

        # Build sliding windows (example: win=100 ovlp=50 as in your notebook)
        logger.info("Creating sliding windows")
        windows = sliding_windows(len(filtered_seqs[ref_id]), win_size=100, overlap=50)

        # Create windows df based on priors and scores
        logger.info("Scoring windows and creating windows dataframe")
        window_df = create_windows_df(windows, filtered_seqs, prior_table=prior_table)

        window_csv = output_dir / "windows_trace.csv"
        window_df.to_csv(window_csv, index=False)
        logger.info("Windows trace written to %s", window_csv)

        # Create mixed consensus
        logger.info("Creating mixed consensus from ABACAS and IRMA sequences")
        abacas_key = "ordered_" + ref_id  # as in your code
        irma_key = "01_irma"
        if abacas_key not in filtered_seqs or irma_key not in filtered_seqs:
            logger.error("Expected keys %s and %s in filtered_seqs", abacas_key, irma_key)
            sys.exit(2)

        cons = create_consensus(abacas_seq=filtered_seqs[abacas_key],
                                irma_seq=filtered_seqs[irma_key],
                                window_df=window_df)

        # Insert IRMA insertions found in the original aligned IRMA vs REF
        logger.info("Detecting and re-inserting IRMA insertions removed by filtering")
        final_with_ins, insertions = add_irma_insertions(irma_aln=original_seqs[irma_key],
                                                         ref_aln=original_seqs[ref_id],
                                                         final_seq=cons)

        # Write final fasta (remove '-' gaps if any)
        fin_arr = np.array(final_with_ins.split("-"))
        fin_text = "".join(fin_arr[fin_arr != ""])
        base_name = input_path.name
        if base_name.endswith(".aln"):
            base_name = base_name[:-4]
        fasta_path = output_dir / f"{base_name}-MIX_ASSEMBLY.fasta"
        header = f">{base_name}-MIX_ASSEMBLY\n"
        with open(fasta_path, "w") as fh:
            fh.write(header)
            fh.write(fin_text + "\n")
        logger.info("Final mixed assembly FASTA written to %s", fasta_path)

        # Perform QC and write qc.json
        qc_path = output_dir / "qc.json"
        qc_process(filtered_seqs=filtered_seqs, mixed_seq=cons, insertions=insertions, write=str(qc_path))

        logger.info("QC written to %s", qc_path)
        logger.info("Pipeline finished successfully")

    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
