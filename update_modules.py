import os
import shutil
import subprocess
import pandas as pd
from pathlib import Path
import glob
from tqdm import tqdm  # Add tqdm for progress bar

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG_PATH = os.path.join(BASE_DIR, "error_logs.txt")

# Clear contents of 'repos' and 'modules' directories, but keep the directories themselves
for d in ['repos', 'modules']:
    dir_path = os.path.join(BASE_DIR, d)
    if os.path.exists(dir_path):
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        os.makedirs(dir_path, exist_ok=True)

# Load the Excel file
df = pd.read_excel(os.path.join(BASE_DIR, 'modules.xlsx'))

# Add tqdm progress bar for the rows
for idx, row in tqdm(list(df.iterrows()), total=len(df), desc="Processing modules"):
    modules = row['modules']
    git_repo = row['git_repo']
    branch = str(row['branch']).strip() if not pd.isna(row['branch']) else ''
    tag = str(row['tag']).strip() if not pd.isna(row['tag']) else ''

    try:
        if tag and not branch:
            # Construct the download URL
            if git_repo.endswith('.git'):
                base_url = git_repo[:-4]
            else:
                base_url = git_repo

            file_prefix = modules if modules else "download"
            output_file = os.path.join(BASE_DIR, f"repos/{file_prefix}_{tag}.tar.gz")
            print(f"Downloading {base_url} to {output_file}")
            subprocess.run(['wget', '-c', base_url, '-O', output_file], check=True)
            module_name = modules.strip()

            # output directory
            output_directory = os.path.join(BASE_DIR, f"repos/{module_name}")
            subprocess.run(['mkdir', '-p', output_directory], check=True)

            # Extract the tar.gz
            subprocess.run(['tar', '-xzf', output_file, '-C', output_directory], check=True)

            # Identify extracted folder
            all_folders = set(p for p in Path(output_directory).iterdir() if p.is_dir())
            matching_dirs = [d for d in all_folders if module_name in d.name]
            extracted_folder = matching_dirs[0]
            os.chdir(extracted_folder)

        elif branch and not tag:
            # Clone repo
            repo_name = git_repo.rstrip('/').split('/')[-1].replace('.git', '')
            clone_path = os.path.join(BASE_DIR, f'repos/{repo_name}')
            print(f"Cloning {git_repo} branch {branch}")
            subprocess.run(['git', 'clone', '-b', branch, git_repo, clone_path], check=True)
            os.chdir(clone_path)
        else:
            print(f"Skipping row {idx}: branch and tag are both present or both missing.")
            continue

        # Run mvn clean install
        print("Running mvn clean install...")
        subprocess.run(['mvn', 'clean', 'install', '-DskipTests'], check=True)

        # Find and copy .omod
        omod_files = glob.glob('**/target/*.omod', recursive=True)
        for omod in omod_files:
            subprocess.run(['cp', omod, os.path.join(BASE_DIR, 'modules')], check=True)

    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        try:
            with open(ERROR_LOG_PATH, "a") as log_file:
                log_file.write(f"Row {idx} ({modules}): {e}\n")
        except PermissionError:
            print(f"Permission denied: Unable to write to {ERROR_LOG_PATH}")
    finally:
        os.chdir(BASE_DIR)  # Reset to base directory
