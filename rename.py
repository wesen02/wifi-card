def rename_file(old_path, new_filename):
    # Extract directory and old filename
    directory, old_filename = os.path.split(old_path)
    
    # Replace the old filename with the new one
    new_path = os.path.join(directory, new_filename)
    
    # Rename the file
    try:
        os.rename(old_path, new_path)
        print(f"File renamed from '{old_path}' to '{new_path}'")
    except FileNotFoundError:
        print(f"Error: '{old_path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied for renaming '{old_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")