import os
import sys
import math
import logging
import argparse
import shutil
import subprocess
import numpy as np

# -------------------------------------------------------------------
# Setup logging
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# -------------------------------------------------------------------
# Get the base directory from the environment variable
# -------------------------------------------------------------------
base_dir = os.getenv("PSS_VER0_DIR")
if not base_dir:
    logging.error("Error: PSS_VER0_DIR environment variable is not set.")
    sys.exit(1)

# -------------------------------------------------------------------
# Add required paths to sys.path
# -------------------------------------------------------------------
required_paths = [
    "scripts"
]

for relative_path in required_paths:
    full_path = os.path.join(base_dir, relative_path)
    if os.path.exists(full_path):
        sys.path.insert(0, full_path)
        logging.info(f"Added to sys.path: {full_path}")
    else:
        logging.warning(f"Path does not exist: {full_path}")

# -------------------------------------------------------------------
# Import required modules
# -------------------------------------------------------------------
try:
    from read_input_file import *
    from generate_dm_array import *
    from pulsar_search import *
    from candidate_sifting import *
    from removing_duplicate_candidates import *
    from candidate_folding import *
    from ps_to_png import *
    from ml_candidate_classification import *
    from generate_final_outputs import *
    logging.info("Modules imported successfully.")
except ImportError as e:
    logging.error("Error importing required modules.", exc_info=True)
    sys.exit(1)

# -------------------------------------------------------------------
# Parse command line arguments
# -------------------------------------------------------------------
parser = argparse.ArgumentParser(description="PSS Pipeline Runner")
parser.add_argument(
    "-i", "--input",
    required=True,
    help="Path to input configuration file (.txt) OR existing directory"
)

args = parser.parse_args()

input_path = os.path.abspath(args.input)

master_config = os.path.join(base_dir, "input_file_dir", "input_parameters_master.txt")

# -------------------------------------------------------------------
# CASE 1: Input is a .txt file
# -------------------------------------------------------------------
if input_path.endswith(".txt"):

    config_file_path = input_path

    if os.path.exists(config_file_path):
        logging.info(f"Using configuration file: {config_file_path}")

    else:
        logging.warning(f"Configuration file not found: {config_file_path}")

        target_dir = os.path.dirname(config_file_path)

        if not os.path.exists(target_dir):
            logging.error(f"Directory does not exist: {target_dir}")
            sys.exit(1)

        sample_config_path = os.path.join(target_dir, "sample_input_file.txt")

        if os.path.exists(master_config):
            shutil.copy(master_config, sample_config_path)
            logging.info(f"A sample configuration file has been created at: {sample_config_path}")
            logging.info("Please edit this file and rerun the pipeline.")
        else:
            logging.error(f"Master configuration file not found: {master_config}")

        sys.exit(1)

# -------------------------------------------------------------------
# CASE 2: Input is a directory
# -------------------------------------------------------------------
elif os.path.isdir(input_path):

    logging.info(f"Input provided as directory: {input_path}")

    sample_config_path = os.path.join(input_path, "sample_input_file.txt")

    if os.path.exists(master_config):
        shutil.copy(master_config, sample_config_path)
        logging.info(f"A sample configuration file has been created at: {sample_config_path}")
        logging.info("Please edit this file and rerun the pipeline.")
    else:
        logging.error(f"Master configuration file not found: {master_config}")

    sys.exit(1)

# -------------------------------------------------------------------
# CASE 3: Invalid input
# -------------------------------------------------------------------
else:
    logging.error("Invalid input provided.")
    logging.error("Please provide either:")
    logging.error(" - a valid .txt configuration file path, or")
    logging.error(" - an existing directory path")
    sys.exit(1)

# -------------------------------------------------------------------
# Utility function
# -------------------------------------------------------------------
def ensure_directory_exists(directory):
    """Creates the directory if it does not exist."""
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

# -------------------------------------------------------------------
# Main pipeline execution
# -------------------------------------------------------------------
def main():
    """
    Main function to execute astro-accelerate jobs on available GPU nodes.
    """

    # Step 1: Load configuration
    try:
        params = load_parameters(config_file_path)
    except Exception as e:
        logging.error(f"Error reading configuration file: {config_file_path}")
        logging.error(f"Reason: {e}")

        target_dir = os.path.dirname(config_file_path)
        sample_config_path = os.path.join(target_dir, "sample_input_file.txt")

        if os.path.exists(master_config):
            shutil.copy(master_config, sample_config_path)
            logging.info(f"A sample configuration file has been generated at: {sample_config_path}")
            logging.info("Please correct the input file format and rerun the pipeline.")
        else:
            logging.error(f"Master configuration file not found: {master_config}")

        sys.exit(1)

    # Extract directories
    search_input_file_dir = params.get('search_input_file_dir')
    search_output_dir = params.get('search_output_dir')

    # Define derived directories
    sifting_input_dir = search_output_dir
    sifting_output_dir = search_output_dir
    folding_input_dir = search_output_dir
    folding_output_dir = os.path.join(search_output_dir, "folding_outputs")
    classifier_input_dir = os.path.join(folding_output_dir, "fil_foldings")
    classifier_output_dir = os.path.join(search_output_dir, "classifier_outputs")
    final_output_dir = os.path.join(search_output_dir, "final_outputs")

    # Ensure all directories exist
    for dir_path in [search_output_dir, folding_output_dir, classifier_output_dir, final_output_dir]:
        ensure_directory_exists(dir_path)

    # Step 2: Form the DM array
    start_DM = params.get('start_DM')
    end_DM = params.get('end_DM')
    dm_step = params.get('dm_step')

    DM_array = generate_dm_array(start_DM, end_DM, dm_step)

    # Step 3: Pulsar search part
    fil_file = params.get('fil_file')
    total_obs_time = params.get('total_obs_time')
    sampling_time = params.get('sampling_time')
    num_dm = params.get('num_dm')
    accel_bin = params.get('accel_bin')
    workers = params.get('workers')

    # Run the search if selected
    search_type = params.get('search_type')
    
    if search_type == 0:
        print("Loding setup done. Congratulaitions, now running the pulsar search from very begenning.....")

        search_pulsar(
            search_input_file_dir,
            search_output_dir,
            fil_file,
            DM_array,
            dm_step,
            total_obs_time,
            sampling_time,
            num_dm,
            accel_bin,
            workers
        )

    # Step 4: Candidate sifting
    period_tol_sort = params.get('period_tol_sort')
    DM_filtering_cut_10 = params.get('DM_filtering_cut_10')
    DM_filtering_cut_1000 = params.get('DM_filtering_cut_1000')
    low_period = params.get('low_period')
    high_period = params.get('high_period')
    SNR_cut = params.get('SNR_cut')

    candidate_sifting(
        sifting_input_dir,
        sifting_output_dir,
        fil_file,
        DM_array,
        accel_bin,
        period_tol_sort,
        DM_filtering_cut_10,
        DM_filtering_cut_1000,
        low_period,
        high_period,
        SNR_cut,
        dm_step,
        start_DM,
        end_DM
    )

    # Step 5: Remove duplicates
    remove_duplicate_candidates(sifting_output_dir, sifting_output_dir, fil_file)

    # Step 6: Candidate folding
    fold_type = params.get('fold_type')

    candidate_folding(
        folding_input_dir,
        folding_output_dir,
        search_input_file_dir,
        search_output_dir,
        fil_file,
        accel_bin,
        workers,
        fold_type,
        DM_array
    )

    # Step 7: Convert PS files to PNG based on folding flag
    fold_type = params.get('fold_type')

    dirs_to_process = []

    if fold_type == 0:
        dirs_to_process = [os.path.join(folding_output_dir, "dat_foldings")]

    elif fold_type == 1:
        dirs_to_process = [os.path.join(folding_output_dir, "fil_foldings")]

    elif fold_type == 2:
        dirs_to_process = [
            os.path.join(folding_output_dir, "dat_foldings"),
            os.path.join(folding_output_dir, "fil_foldings")
        ]
    else:
        print("Select appropriate folding flag for PS to PNG conversion.")

    for ps_dir in dirs_to_process:

        batch_convert_ps_to_png(
            ps_dir,
            ps_dir,
            workers,
            keyword=os.path.splitext(os.path.basename(fil_file))[0]
        )

    # Step 8: Candidate classification
    fold_type = params.get('fold_type')
    ml_path = os.path.join(base_dir, "Machine_learning")
    python2_path = params.get("python2_path")
    do_classify = params.get('do_classify')
    use_GHVFDT = params.get('use_GHVFDT')
    use_PICS = params.get('use_PICS')
    threshold = params.get('threshold')

    # Check folding and classifier flag to run classifier
    if (fold_type in [1, 2]) and do_classify == 1:

        if use_GHVFDT == 1 and use_PICS == 1:
            print("Both classifiers are on. Please select only one classifier at a time.")

        elif use_GHVFDT == 1:
            run_ml_classifier(
                classifier_input_dir,
                classifier_output_dir,
                python2_path,
                ml_path
            )
        
        elif use_PICS == 1:
            pics_script = os.path.join(base_dir, "scripts", "ai_candidate_classification.py")
            cmd = [
                python2_path,
                pics_script,
                classifier_input_dir,
                classifier_output_dir,
                "--threshold",
                str(threshold)
            ]
            print("Running PICS classifier:")
            print(" ".join(cmd))
            
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError as e:
                print("Error running PICS classifier:", e)
        else:
            print("Classifier flag is on. Please select a classifier model appropriately.")
    else:
        print("Select appropriate folding and classifier flags to run classifier on filterbank folded PFD files.")

    # Step 9: Generate final output PDF files of classified as well as all folded candidates
    # All paths are passes with params, no need to specify here.

    generate_final_pdfs(
        fil_file=fil_file,
        params=params,
        folding_output_dir=folding_output_dir,
        classifier_output_dir=classifier_output_dir,
        final_output_dir=final_output_dir
    )
    
    # Print the final message.....
    print("\n==========================================")
    print("\n🎉 Processing complete!")
    print("Yay, your processing is done.")
    print("Now grab a cup of coffee ☕ and check the results after that.\n")
    print("==========================================\n")



if __name__ == "__main__":
    main()