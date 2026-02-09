import os
import subprocess
from multiprocessing import Pool

def read_candidates(input_file):
    """Reads the candidate file and extracts DM index, candidate index, period, and SNR."""
    candidates = []
    with open(input_file, "r") as f:
        next(f)   # Skip header
        
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

        dm_value = DM_array[dm_index]

        accel_file = os.path.join(dat_file_dir, f"{file_name}_DM{dm_value}_ACCEL_{accel_bin}.cand")

        # ---- DAT folding ----
        dat_file_path = os.path.join(dat_file_dir, f"{file_name}_DM{dm_value}.dat")

        if os.path.exists(dat_file_path):

            dat_cmd = (
                f"prepfold -accelcand {cand_index} -accelfile {accel_file} "
                f"-nodmsearch -noxwin -nosearch -zerodm -o "
                f"{file_name}_DM{dm_value}_DAT "
                f"{dat_file_path} "
                f">> {os.path.join(output_dir, 'prepfold.log')} 2>&1"
            )

            dat_folding_strings.append(dat_cmd)

        else:
            print(f"Warning: .dat file not found: {dat_file_path}")

        # ---- FIL folding ----
        fil_file_path = os.path.join(fil_file_dir, f"{file_name}.fil")

        if os.path.exists(fil_file_path):

            fil_cmd = (
                f"prepfold -accelcand {cand_index} -accelfile {accel_file} "
                f"-dm {dm_value} -nodmsearch -noxwin -nopdsearch -zerodm -o "
                f"{file_name}_DM{dm_value}_FIL "
                f"{fil_file_path} "
                f">> {os.path.join(output_dir, 'prepfold.log')} 2>&1"
            )

            fil_folding_strings.append(fil_cmd)

        else:
            print(f"Warning: .fil file not found: {fil_file_path}")

    return dat_folding_strings, fil_folding_strings


def folding_in_dir(args):
    """Execute folding command inside a specific directory."""
    cmd, workdir = args
    try:
        print(f"Running folding command in {workdir}: {cmd}")
        subprocess.run(cmd, shell=True, check=True, cwd=workdir)
    except subprocess.CalledProcessError as e:
        print(f"Error executing folding command: {e}")


def candidate_folding(input_dir, output_dir, fil_file_dir, dat_file_dir, fil_file,
                      accel_bin, workers, fold_type, DM_array):
    """
    Reads candidates from input file, generates folding commands,
    and executes them in parallel in correct directories.
    """

    file_name = os.path.splitext(os.path.basename(fil_file))[0]

    input_file = os.path.join(input_dir, f"{file_name}_all_sifted_filtered_candidates.txt")

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    if not os.path.exists(input_file):
        print(f"Error: Candidate file '{input_file}' not found in '{input_dir}'.")
        return

    os.makedirs(output_dir, exist_ok=True)

    candidates = read_candidates(input_file)

    if not candidates:
        print(f"No candidates found in '{input_file}'. Exiting.")
        with open(os.path.join(output_dir, "prepfold.log"), "w") as log_file:
            log_file.write("No candidates found.\n")
        return

    dat_folding_strings, fil_folding_strings = generate_folding_commands(
        candidates, file_name, accel_bin, output_dir, fil_file_dir, dat_file_dir, DM_array
    )

    if not dat_folding_strings and not fil_folding_strings:
        print("No valid prepfold commands generated. Exiting.")
        with open(os.path.join(output_dir, "prepfold.log"), "w") as log_file:
            log_file.write("No valid prepfold commands generated.\n")
        return

    with Pool(workers) as pool:

        # ---------- DAT FOLDING ----------
        if fold_type == 0.0 or fold_type == 2.0:
            if len(dat_folding_strings) > 0:

                dat_output_dir = os.path.join(output_dir, "dat_foldings")
                os.makedirs(dat_output_dir, exist_ok=True)

                print("Total number of DAT candidates:", len(dat_folding_strings))

                tasks = [(cmd, dat_output_dir) for cmd in dat_folding_strings]
                pool.map(folding_in_dir, tasks)

        # ---------- FIL FOLDING ----------
        if fold_type == 1.0 or fold_type == 2.0:
            if len(fil_folding_strings) > 0:

                fil_output_dir = os.path.join(output_dir, "fil_foldings")
                os.makedirs(fil_output_dir, exist_ok=True)

                print("Total number of FIL candidates:", len(fil_folding_strings))

                tasks = [(cmd, fil_output_dir) for cmd in fil_folding_strings]
                pool.map(folding_in_dir, tasks)


if __name__ == "__main__":

    input_dir = "input_directory"
    output_dir = "output_directory"
    fil_file_dir = "fil_file_directory"
    dat_file_dir = "dat_file_directory"

    fil_file = "your_file.fil"

    accel_bin = "200"
    workers = 4

    # 0 -> only DAT folding
    # 1 -> only FIL folding
    # 2 -> both
    fold_type = 0.0

    DM_array = [0.0, 1.0, 2.0, 3.0, 4.0]

    candidate_folding(
        input_dir,
        output_dir,
        fil_file_dir,
        dat_file_dir,
        fil_file,
        accel_bin,
        workers,
        fold_type,
        DM_array
    )