import os
import shutil

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