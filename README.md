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

The following software and libraries are required to run the pipeline:

- Python 3.x  
- Python 2.x (path needs to be provided in the input configuration file)  
- NumPy  
- PRESTO  

### Environment Variable

Before running the pipeline, set the following environment variable to point to the pipeline root directory:

```bash
export PSS_VER0_DIR=/path/to/pss_pipeline_root
```

This directory should contain the `scripts` folder and all required pipeline modules.

---

## Setup

Ensure that:

- PRESTO is installed and available in your system PATH  
- Required Python packages (like NumPy) are installed  

No additional installation is necessary beyond this setup.

---

## Input Configuration File

All pipeline parameters are controlled through an external input configuration file.

This file defines:

- Input data locations  
- Search parameters  
- Sifting and folding options  
- Classification settings  

### Automatic Template Generation

If an incorrect or non-existent configuration file is provided, the pipeline will automatically create a sample configuration file named:

```
sample_input_file.txt
```

in the same directory as the provided path.

This template is copied from:

```
$PSS_VER0_DIR/input_file_dir/input_parameters_master.txt
```

You can then edit this file with correct parameters and rerun the pipeline.

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

## Output Structure

The pipeline automatically creates required output directories based on the input configuration.

A typical output directory structure looks like:

```
search_output_dir/
├── folding_outputs/
├── classifier_outputs/
```

All intermediate products and final results are stored inside these directories.

---

## Troubleshooting

If you encounter issues:

- Confirm PRESTO is correctly installed and in your system PATH  
- Check that `$PSS_VER0_DIR` is properly set  
- Verify that all required scripts exist inside `$PSS_VER0_DIR/scripts`  
- If the pipeline fails due to configuration errors, edit the auto-generated sample input file and try again  

---

## Notes

- Python 2.x is required only for the legacy machine-learning classifier module  
- The pipeline is telescope-independent and can be used with any PRESTO-compatible filterbank data  

---

## Contributing

Contributions, improvements, and bug reports are welcome.

Feel free to:

- Open an issue for bug reports  
- Suggest new features  
- Submit pull requests with improvements  

---

## License

This project is released for academic and research use.  
Please cite appropriately if you use this pipeline for published research.
