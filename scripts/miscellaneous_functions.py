import os
import shutil

# Function to clean a directory and prepare it for a fresh run after an imcomplete run
def clear_directory(directory):

    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return

    if not os.path.isdir(directory):
        print(f"Given path is not a directory: {directory}")
        return

    for item in os.listdir(directory):

        item_path = os.path.join(directory, item)

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)

            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")

    print(f"Successfully cleared all contents of: {directory}")


# Function to remove duplicate canddiates with same period from sifted output files
def remove_duplicate_candidates(input_dir, output_dir, fil_file):
    
    # Extract the file_name by removing the ".fil" extension from the fil_file name
    file_name = os.path.splitext(os.path.basename(fil_file))[0]

    input_file = os.path.join(input_dir, f"{file_name}_all_sifted_candidates.txt")
    output_file = os.path.join(output_dir, f"{file_name}_all_sifted_filtered_candidates.txt")

    candidates = {}

    with open(input_file, "r") as infile:
        lines = infile.readlines()

    header = lines[0]  # Preserve the header
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue  # Skip malformed lines

        dm_index = parts[0]
        cand_index = parts[1]
        period = float(parts[2])  # Convert period to float for accurate comparisons
        snr = float(parts[3])  # Convert SNR to float for comparisons

        if period not in candidates or snr > candidates[period][2]:
            candidates[period] = (dm_index, cand_index, period, snr)

    with open(output_file, "w") as outfile:
        outfile.write(header)
        for _, (dm_index, cand_index, period, snr) in sorted(candidates.items()):
            outfile.write(f"{dm_index}   {cand_index}   {period:.5f}     {snr:.2f}\n")

    print(f"Filtered candidates written to: {output_file}")