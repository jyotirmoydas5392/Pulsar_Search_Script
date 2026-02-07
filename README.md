# PSS: Pulsar Search Script

This repository contains a modular Python-based pipeline for performing pulsar search, candidate sifting, folding, and classification for uGMRT or any other telescope filterbank data.

The pipeline is designed to be flexible and easily configurable through external input parameter files.

---

## Features

- Modular architecture for end-to-end pulsar search  
- PRESTO-based parallel search on a given DM range and step  
- Candidate sifting and duplicate removal  
- Candidate folding and visualization  
- Machine-learning based candidate classification  
- Fully configurable via external input files  

---

## Prerequisites

- Python 3.x  
- Python 2.x (path needs to be added in the input configuration file)  
- NumPy  
- PRESTO  

### Environment Variable

Before running the pipeline, set the following environment variable to point to the pipeline root directory:

```bash
export PSS_VER0_DIR=/path/to/pss_pipeline_root
