# PSS Pulsar Search Pipeline

This repository contains a modular Python-based pipeline for performing pulsar search, candidate sifting, folding, and classification using uGMRT filterbank data.

The pipeline is designed to be flexible, GPU-enabled, and easily configurable through external input parameter files.

---

## Features

- Modular architecture for end-to-end pulsar search
- PRESTO based paralell search on given DM range and step
- Candidate sifting and duplicate removal
- Candidate folding and visualization
- Machine-learning based candidate classification
- Fully configurable via external input files

---

## Prerequisites

- Python 3.x
- NumPy
- Required custom modules located in `$PSS_VER0_DIR/scripts`
- Properly configured environment variable:

```bash
export PSS_VER0_DIR=/path/to/pss_pipeline_root