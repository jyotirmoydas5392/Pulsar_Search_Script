import os
import numpy as np
import itertools

def consecutive(data, stepsize=1):
    """Identify consecutive groups in an array."""
    return np.split(data, np.where(np.diff(data) != stepsize)[0] + 1)

def candidate_sifting(input_dir, output_dir, fil_file, DM_array, accel_bin, period_tol_sort, DM_filtering_cut_10, DM_filtering_cut_1000, low_period, high_period, SNR_cut, dm_step, start_DM, end_DM):
    # Extract the file_name by removing the ".fil" extension from the fil_file name
    file_name = os.path.splitext(os.path.basename(fil_file))[0]
    
    cand_len = []  # Initialize list to store candidate lengths

    # Loop through DM trials and extract candidate data
    for m in range(len(DM_array)):
        file_path = os.path.join(input_dir, f"{file_name}_DM{DM_array[m]}_ACCEL_{accel_bin}")
        
        # Ensure file exists
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}")
            continue
        
        with open(file_path) as f:
            lines = f.readlines()

        # Identify all separator line positions
        separator_indices = [i for i, line in enumerate(lines) if set(line.strip()) == {'-'}]

        if len(separator_indices) < 2:
            print(f"Warning: Less than two separator lines found in {file_path}")
            continue

        # Get the second separator line
        b = separator_indices[1]
        cand_len.append(b)
        
        cand_len.append(b)

    # Wait before proceeding
    os.system("sleep 5")
    
    if not cand_len:
        print("No valid candidates found. Exiting.")
        return
    
    max_cand_len = int(max(cand_len))

    # Initialize arrays with NaN values
    Sigma_array = np.full((len(DM_array), max_cand_len), np.nan)
    Coherent_Power_array = np.full((len(DM_array), max_cand_len), np.nan)
    Periodicity_array = np.full((len(DM_array), max_cand_len), np.nan)
    r_bin_array = np.full((len(DM_array), max_cand_len), np.nan)
    z_bin_array = np.full((len(DM_array), max_cand_len), np.nan)

    # Populate arrays with extracted candidate data
    for m in range(len(DM_array)):
        file_path = os.path.join(input_dir, f"{file_name}_DM{DM_array[m]}_ACCEL_{accel_bin}")
        
        with open(file_path) as f:
            lines = f.readlines()

        # Identify all separator line positions
        separator_indices = [i for i, line in enumerate(lines) if set(line.strip()) == {'-'}]

        if len(separator_indices) < 2:
            print(f"Warning: Less than two separator lines found in {file_path}")
            continue

        # Get the second separator line
        b = separator_indices[1]
        cand_len.append(b)

        for j in range(3, b - 4):
            line_split = list(filter(lambda x: x != "", lines[j].split(" ")))

            if low_period <= float(line_split[5].split("(")[0]) <= high_period:
                try:
                    Sigma_array[m][j] = float(line_split[1])
                    Coherent_Power_array[m][j] = float(line_split[3])
                    Periodicity_array[m][j] = float(line_split[5].split("(")[0])
                    r_bin_array[m][j] = float(line_split[7].split("(")[0])
                    z_bin_array[m][j] = float(line_split[9].split("(")[0])
                except (IndexError, ValueError):
                    print(f"Warning: Malformed data on line {j+1} in {file_path}")
                    continue

    # Filtering unique r_bin values
    r_bin_flatten = r_bin_array.flatten()
    filtered_r_bin_list0 = [x for x in np.unique(r_bin_flatten) if not np.isnan(x)]
    uniq_r_bin_list0, r_tol_array = [], []

    print(f"Filtered unique r_bin list length: {len(filtered_r_bin_list0)}")

    while len(filtered_r_bin_list0) > 0:
        indices = np.where(filtered_r_bin_list0 <= filtered_r_bin_list0[0] + filtered_r_bin_list0[0] * (period_tol_sort / 100.0))
        uniq_r_bin_list0.append(filtered_r_bin_list0[0])
        r_tol_array.append(filtered_r_bin_list0[0] * (period_tol_sort / 100.0))
        filtered_r_bin_list0 = np.delete(filtered_r_bin_list0, indices[0])

    # Final filtering and output
    output_file = os.path.join(output_dir, f"{file_name}_all_sifted_candidates.txt")
    
    # Ensure that there are valid candidates before writing
    candidates_found = False
    with open(output_file, "w") as file:
        file.write("Candidate_indeces(DM and Cand no)  Period(sec)   SNR\n")

    print(f"Writing output to {output_file}")

    for i, uniq_r_bin in enumerate(uniq_r_bin_list0):
        if i == 0:
            index = np.where(r_bin_array <= uniq_r_bin + r_tol_array[i] / 2)
        else:
            index = np.where((r_bin_array > uniq_r_bin_list0[i - 1] + r_tol_array[i - 1] / 2) &
                             (r_bin_array <= uniq_r_bin + r_tol_array[i] / 2))

        if not index[0].size:
            continue

        DM_index, cand_index = index[0], index[1]
        DM_groups = consecutive(np.unique(DM_index))

        DM_slope = (DM_filtering_cut_1000 - DM_filtering_cut_10) / 0.990
        DM_intercept = DM_filtering_cut_10 - (DM_slope * 0.010)

        DM_filtering_cut = int((DM_intercept + (DM_slope * Periodicity_array[index[0][0]][index[1][0]]/1000)) / dm_step)

        # New condition to ensure DM_filtering_cut doesn't exceed allowable range
        max_DM_filtering_cut = int((end_DM - start_DM) / dm_step)
        if DM_filtering_cut > max_DM_filtering_cut:
            DM_filtering_cut = max_DM_filtering_cut
            print(f"DM_filtering_cut is greater than the allowable range. It has been set to {DM_filtering_cut}.")

        print(f"For Period {Periodicity_array[index[0][0]][index[1][0]]/1000} sec, DM tolerance is {DM_filtering_cut * dm_step} pc/cc")

        for group in DM_groups:
            if len(group) >= DM_filtering_cut:
                Filtered_SNR_array = np.full(Sigma_array.shape, np.nan)

                for dm_idx in group:
                    DM_cand_indices = np.where(DM_index == dm_idx)
                    Filtered_SNR_array[dm_idx, cand_index[DM_cand_indices]] = Sigma_array[dm_idx, cand_index[DM_cand_indices]]

                # Ensure we have at least one valid SNR value
                if np.all(np.isnan(Filtered_SNR_array)):
                    continue

                maxima_index = np.unravel_index(np.nanargmax(Filtered_SNR_array), Filtered_SNR_array.shape)
                if Sigma_array[maxima_index] >= SNR_cut:
                    candidates_found = True
                    with open(output_file, "a") as file:
                        file.write(f"{maxima_index[0]}   {maxima_index[1]-2}   {Periodicity_array[maxima_index]:.5f}     {Sigma_array[maxima_index]:.2f}\n")

    if not candidates_found:
        print("No candidates passed the filtering criteria.")
    else:
        print("Finished processing and writing all sifted candidates.")
