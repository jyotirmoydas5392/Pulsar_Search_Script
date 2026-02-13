import os
from pathlib import Path
from PIL import Image
from multiprocessing import Pool


# ============================================================
# IMAGE PROCESSING WORKER
# ============================================================
def process_image(args):
    image_path, scale_factor = args

    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")

            if scale_factor < 1.0:
                new_size = (
                    int(img.width * scale_factor),
                    int(img.height * scale_factor)
                )
                img = img.resize(new_size, Image.LANCZOS)

            return img

    except Exception as e:
        print(f"[Worker ERROR] {image_path}: {e}")
        return None


# ============================================================
# PARALLEL PNG → PDF (WITH PROGRESS)
# ============================================================
def pngs_to_pdf_parallel(
    input_dir,
    output_dir,
    data_id,
    keyword,
    scale_factor=0.4,
    jpeg_quality=40,
    max_workers=4
):

    print("\n=========================================")
    print(f"Starting PDF generation for: {keyword}")
    print("=========================================")

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    png_files = sorted(input_path.glob("*.png")) + sorted(input_path.glob("*.PNG"))

    total_files = len(png_files)
    print(f"Found {total_files} PNG files in {input_dir}")

    if total_files == 0:
        print("No PNG files found. Skipping.")
        return

    target_file = output_path / f"{data_id}_final_folded_{keyword}_candidates.pdf"

    print(f"Using {max_workers} workers...")
    print("Starting parallel image processing...")

    args_list = [(str(p), scale_factor) for p in png_files]
    processed_images = []

    with Pool(processes=max_workers) as pool:

        for i, img in enumerate(pool.imap(process_image, args_list), 1):

            if img is not None:
                processed_images.append(img)

            # Progress update every 20 images
            if i % 20 == 0 or i == total_files:
                print(f"Processed {i}/{total_files} images...")

    print("Finished parallel processing.")

    if not processed_images:
        print("No valid images found. Skipping PDF save.")
        return

    print("Saving PDF...")

    processed_images[0].save(
        target_file,
        save_all=True,
        append_images=processed_images[1:],
        format="PDF",
        quality=jpeg_quality
    )

    print(f"PDF saved successfully: {target_file}")
    print("=========================================\n")


# ============================================================
# STEP 9: GENERATE FINAL PDF OUTPUTS
# ============================================================
def generate_final_pdfs(
    fil_file,
    params,
    folding_output_dir,
    classifier_output_dir,
    final_output_dir
):

    print("\n########## STEP 9: PDF GENERATION ##########")

    Path(final_output_dir).mkdir(parents=True, exist_ok=True)

    fold_type = params.get('fold_type')
    workers = params.get('workers', 4)

    print(f"Fold type: {fold_type}")
    print(f"Workers requested: {workers}")

    file_name = fil_file.replace(".fil", "")

    dirs_to_process = []

    if fold_type == 0:
        dirs_to_process = [
            os.path.join(folding_output_dir, "dat_foldings")
        ]

    elif fold_type == 1:
        dirs_to_process = [
            os.path.join(folding_output_dir, "fil_foldings"),
            os.path.join(classifier_output_dir, "positive_candidates"),
            os.path.join(classifier_output_dir, "negative_candidates")
        ]

    elif fold_type == 2:
        dirs_to_process = [
            os.path.join(folding_output_dir, "dat_foldings"),
            os.path.join(folding_output_dir, "fil_foldings"),
            os.path.join(classifier_output_dir, "positive_candidates"),
            os.path.join(classifier_output_dir, "negative_candidates")
        ]

    else:
        print("Invalid fold_type. Skipping PDF generation.")
        return

    label_map = {
        "dat_foldings": "dat",
        "fil_foldings": "fil",
        "positive_candidates": "positive",
        "negative_candidates": "negative"
    }

    for cand_dir in dirs_to_process:

        print(f"\nChecking directory: {cand_dir}")

        if not os.path.exists(cand_dir):
            print("Directory does not exist. Skipping.")
            continue

        dir_name = os.path.basename(cand_dir)
        label = label_map.get(dir_name, dir_name)

        pngs_to_pdf_parallel(
            input_dir=cand_dir,
            output_dir=final_output_dir,
            data_id=file_name,
            keyword=label,
            max_workers=workers
        )

    print("########## STEP 9 COMPLETE ##########\n")


# ============================================================
# MULTIPROCESSING SAFETY
# ============================================================
if __name__ == "__main__":
    print("PDF generation module loaded successfully.")