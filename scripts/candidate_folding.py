import os
import subprocess
from multiprocessing import Pool

def read_candidates(input_file):
    """Reads the candidate file and extracts DM index, candidate index, period, and SNR."""
    candidates = []
    with open(input_file, "r") as f:
        # Skip the first row (header)
        next(f)
        
        for line in f:
            parts = line.split()
            if len(parts) < 4:
                continue
            dm_index = int(parts[0])
            cand_index = int(parts[1])
            period = float(parts[2])
            snr = float(parts[3])
            candidates.append((dm_index, cand_index, period, snr))
    return candidates

def generate_folding_commands(candidates, file_name, accel_bin, output_dir, fil_file_dir, dat_file_dir, DM_array):
    """Generates prepfold commands for both .dat and .fil files with logging."""
    dat_folding_strings = []
    fil_folding_strings = []

    for dm_index, cand_index, period, snr in candidates:
        # Fetch DM value from DM_array based on dm_index
        dm_value = DM_array[dm_index]  # DM value from the array
        accel_file = os.path.join(dat_file_dir, f"{file_name}_DM{dm_value}_ACCEL_{accel_bin}.cand")

        # Construct commands for .dat files (check file existence)
        dat_file_path = os.path.join(dat_file_dir, f"{file_name}_DM{dm_value}.dat")
        if os.path.exists(dat_file_path):
            dat_cmd = (f"prepfold -accelcand {cand_index} -accelfile {accel_file} "
                       f"-dm {dm_value} -nodmsearch -noxwin -nosearch -zerodm -o "
                       f"{file_name}_DM{dm_value}_DAT "
                       f"{dat_file_path} "
                       f">> {os.path.join(output_dir, 'prepfold.log')} 2>&1")
            dat_folding_strings.append(dat_cmd)
        else:
            print(f"Warning: .dat file not found: {dat_file_path}")

        # Construct commands for .fil files (check file existence)
        fil_file_path = os.path.join(fil_file_dir, f"{file_name}.fil")
        if os.path.exists(fil_file_path):
            fil_cmd = (f"prepfold -accelcand {cand_index} -accelfile {accel_file} "
                       f"-dm {dm_value} -nodmsearch -noxwin -nopdsearch -zerodm -o "
                       f"{file_name}_DM{dm_value}_FIL "
                       f"{fil_file_path} "
                       f">> {os.path.join(output_dir, 'prepfold.log')} 2>&1")
            fil_folding_strings.append(fil_cmd)
        else:
            print(f"Warning: .fil file not found: {fil_file_path}")

    return dat_folding_strings, fil_folding_strings

def folding(cmd):
    """Execute fold command."""
    try:
        print(f"Running folding command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing ddp command: {e}")

def candidate_folding(input_dir, output_dir, fil_file_dir, dat_file_dir, fil_file, accel_bin, workers, fold_type, DM_array):
    """
    Reads candidates from `input_file` (located in `input_dir`),
    generates folding commands, and executes them inside `output_dir`.
    """
    # Extract the file_name by removing the ".fil" extension from the fil_file name
    file_name = os.path.splitext(os.path.basename(fil_file))[0]
    
    input_file = os.path.join(input_dir, f"{file_name}_all_sifted_filtered_candidates.txt")
    
    # Ensure input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return
    
    # Ensure input file exists
    if not os.path.exists(input_file):
        print(f"Error: Candidate file '{input_file}' not found in '{input_dir}'.")
        return

    # Read candidate data
    candidates = read_candidates(input_file)
    
    # If no candidates found, exit
    if not candidates:
        print(f"No candidates found in '{input_file}'. Exiting.")
        with open(os.path.join(output_dir, "prepfold.log"), "w") as log_file:
            log_file.write("No candidates found.\n")
        return
    
    dat_folding_strings, fil_folding_strings = generate_folding_commands(candidates, file_name, accel_bin, output_dir, fil_file_dir, dat_file_dir, DM_array)

    # If no commands were generated, log and exit
    if not dat_folding_strings and not fil_folding_strings:
        print("No valid prepfold commands generated. Exiting.")
        with open(os.path.join(output_dir, "prepfold.log"), "w") as log_file:
            log_file.write("No valid prepfold commands generated.\n")
        return

    def main():
        """Runs folding commands in parallel."""
        base_dir = os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        os.chdir(output_dir)

        with Pool(workers) as pool:
            if fold_type == 0.0:
                print("Total number of candidates:", len(dat_folding_strings), "and total number of foldings:", len(dat_folding_strings))
                pool.map(folding, dat_folding_strings)
            elif fold_type == 1.0:
                print("Total number of candidates:", len(fil_folding_strings), "and total number of foldings:", len(fil_folding_strings))
                pool.map(folding, fil_folding_strings)
            else:
                print("Total number of candidates:", len(dat_folding_strings), "and total number of foldings:", len(dat_folding_strings) + len(fil_folding_strings))
                pool.map(folding, dat_folding_strings)
                pool.map(folding, fil_folding_strings)

        os.chdir(base_dir)
    
    main()

if __name__ == "__main__":
    # Define input and output directories
    input_dir = "input_directory"  # Change this to the actual directory containing the input file
    output_dir = "output_directory"  # Directory where folding will be executed and logs will be stored
    fil_file_dir = "fil_file_directory"  # Directory where .fil file is located
    dat_file_dir = "dat_file_directory"  # Directory where .dat and accel file are located
    fil_file = "your_file.fil"  # Change to the actual .fil file (full path)
    accel_bin = "1"  # Acceleration search bin
    workers = 4  # Number of parallel processes
    fold_type = 0.0  # 0 for .dat, 1 for .fil, 2 for both

    # Example DM array (replace with actual values)
    DM_array = [0.0, 1.0, 2.0, 3.0, 4.0]  # Array of DM values
    
    # Run the folding process
    candidate_folding(input_dir, output_dir, fil_file_dir, dat_file_dir, fil_file, accel_bin, workers, fold_type, DM_array)