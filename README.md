# PSS: Pulsar Search Script

This repository contains a modular Python-based pipeline for performing pulsar search, candidate sifting, folding, and classification for the uGMRT or any-other telescopes filterbank data.

The pipeline is designed to be flexible, and easily configurable through external input parameter files.

---

## Features

- Modular architecture for end-to-end pulsar search
- PRESTO based parallel search on given DM range and step
- Candidate sifting and duplicate removal
- Candidate folding and visualization
- Machine-learning based candidate classification
- Fully configurable via external input files

---

## Prerequisites

- Python 3.x
- Python 2.X (Path need to be added in input_configuration file)
- NumPy
- PRESTO

- Properly configure the enviroment variables:

```bash
export PSS_VER0_DIR=/path/to/pss_pipeline_root

This directory should contain the scripts folder and other required pipeline modules.

Input Configuration File

All pipeline parameters are controlled through an external configuration file.
This file defines input data locations, search parameters, and processing options.

If an invalid or non-existent configuration file is provided, the pipeline will automatically generate a template file named:

sample_input_file.txt


in the same directory as the provided path, copied from:

$PSS_VER0_DIR/input_file_dir/input_parameters_master.txt


You can then edit this template and rerun the pipeline.

Basic Usage

The pipeline is executed from the command line by providing an input configuration file.

Running the Pipeline Directly
python pss_pipeline.py -i <path_to_input_file>


Example:

python pss_pipeline.py -i ../input_files/input_parameters.txt

Using the Makefile

For convenience, a Makefile is provided to launch the pipeline:

make run INPUT=../input_files/input_parameters.txt


If the INPUT argument is not provided, the Makefile will display usage instructions.

Output Structure

The pipeline automatically creates required output directories based on the input configuration. Typical generated directories include:

search_output_dir/
├── folding_outputs/
├── classifier_outputs/


All intermediate and final products are stored inside these directories.

Cleaning Temporary Files

To remove temporary logs and cache files:

make clean

Notes

Ensure PRESTO is properly installed and accessible in the system PATH.

Python 2.x is required only for the legacy machine-learning classifier module.

All custom scripts are automatically loaded from $PSS_VER0_DIR/scripts.


---
