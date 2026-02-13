# PSS: Pulsar Search Script

This repository contains a modular Python-based pipeline for performing pulsar search, candidate sifting, folding, and classification for uGMRT or any other telescope filterbank data.

The pipeline is designed to be flexible and easily configurable through external input parameter files.

---

## Features

- Modular architecture for end-to-end pulsar search  
- PRESTO-based parallel search on a given DM range and step  
- Candidate sifting and duplicate removal  
- Candidate folding and visualization  
- Machine-learning and AI-based candidate classification  
- Fully configurable via external input files  

---

## Classification Support

The pipeline currently supports two independent candidate classification frameworks:

### 1. GHVFDT-based Machine Learning Classifier

- Traditional machine-learning based classifier  
- Operates on PRESTO `.pfd` based candidate features  
- Requires Python 2.x environment  
- Integrated directly within the pipeline  

### 2. PICS-based AI Classifier (Integrated)

- Deep-learning based pulsar candidate classifier  
- Uses trained neural network models  
- Provides robust candidate ranking and selection  
- Fully integrated into the pipeline  
- No separate installation required  

The PICS classifier used in this pipeline is based on the original open-source project:

PICS (Pulsar Image-based Classification System)  
Source: https://github.com/zhuww/ubc_AI.git  

We gratefully acknowledge the authors of the PICS framework for making their implementation publicly available.

The `ubc_AI` package is already included and integrated within this pipeline. Users do not need to install it separately. Only the general prerequisites listed below need to be satisfied.

---

## Prerequisites

The following software and libraries are required to run the pipeline:

- Python 3.x (for main pipeline execution)  
- Python 2.x (required for classification modules)  
- NumPy  
- PRESTO  

### Requirements for PICS Classifier

Since the PICS (ubc_AI) framework is already integrated into the pipeline, users only need to ensure that:

- Python 2.x is properly available  
- Required Python 2.x dependencies are installed  
- PRESTO is properly configured
- PICS prerequisites are installed properly (see: https://github.com/zhuww/ubc_AI.git)

No separate installation of `ubc_AI` is required.

---

## Environment Variable

Before running the pipeline, set the following environment variable to point to the pipeline root directory:

```bash
export PSS_VER0_DIR=/path/to/pss_pipeline_root
```

This directory should contain the `scripts` folder and all required pipeline modules.

---

## Setup

Ensure that:

- PRESTO is installed and available in your system PATH  
- Required Python packages (such as NumPy) are installed  
- Python 2.x is available for running classifier modules  

No additional installation is required beyond this setup.

---

## Input Configuration File

All pipeline parameters are controlled through an external input configuration file.

This file defines:

- Input data locations  
- Search parameters  
- Sifting and folding options  
- Classification settings  
  - Selection of classifier (GHVFDT or PICS)  
  - Probability threshold for classification  
  - Path to Python 2.x executable  

### Automatic Template Generation

If an incorrect or non-existent configuration file is provided, the pipeline will automatically create a sample configuration file named:

```
sample_input_file.txt
```

in the same directory as the provided path.

This template file is copied from:

```
$PSS_VER0_DIR/input_file_dir/input_parameters_master.txt
```

You can then edit this file with appropriate parameters and rerun the pipeline.

---

## Basic Usage

The pipeline is executed from the command line by specifying an input configuration file.

### Running the Pipeline Directly

```bash
python pulsar_search.py -i <path_to_input_file>
```

Example:

```bash
python pulsar_search.py -i ../input_files/input_parameters.txt
```

---

## Classification Options

Candidate classification is fully configurable via the input configuration file.

You may choose only one classifier at a time:

- GHVFDT-based ML classifier  
- PICS-based AI classifier  

The pipeline will automatically execute the selected classifier on the folded candidates and organize the results into:

```
classifier_outputs/
├── positive_candidates/
├── negative_candidates/
```

based on the probability threshold specified in the configuration file.

---

## Output Structure

The pipeline automatically creates required output directories based on the input configuration.

A typical output directory structure looks like:

```
search_output_dir/
├── folding_outputs/
├── classifier_outputs/
├── final_outputs/
```

All intermediate products and final results are stored inside these directories.

---

## Troubleshooting

If you encounter issues:

- Confirm PRESTO is correctly installed and in your system PATH  
- Check that `$PSS_VER0_DIR` is properly set  
- Verify that the Python 2.x path is correctly provided in the input configuration file  
- Ensure that required Python 2.x dependencies are installed  
- If the pipeline fails due to configuration errors, edit the auto-generated sample input file and try again  

---

## Notes

- Python 2.x is required only for the candidate classification modules  
- The pipeline is telescope-independent and can be used with any PRESTO-compatible filterbank data  
- Only one classifier (GHVFDT or PICS) can be used at a time  

---

## Contributing

Contributions, improvements, and bug reports are welcome.

Feel free to:

- Open an issue for bug reports  
- Suggest new features  
- Submit pull requests with improvements  

---

## Contact

For questions, suggestions, or collaboration related to this pipeline, please feel free to contact:

**Email:** tataidas5392@gmail.com

---

## License

This project is released for academic and research use.  
Please cite appropriately if you use this pipeline for published research.

