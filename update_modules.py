import os
import shutil
import subprocess
import pandas as pd
from pathlib import Path
import glob
from tqdm import tqdm  # Add tqdm for progress bar

# Recreate 'repos' and 'modules' directories
for d in ['repos', 'modules']:
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)

# Load the Excel file
df = pd.read_excel('modules.xlsx')

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
            output_file = f"repos/{file_prefix}_{tag}.tar.gz"
            print(f"Downloading {base_url} to {output_file}")
            subprocess.run(['wget', '-c', base_url, '-O', output_file], check=True)

            # Extract the tar.gz
            subprocess.run(['tar', '-xzf', output_file, '-C', 'repos'], check=True)

            # Identify extracted folder
            extracted_folder = next(Path('repos').glob(f'*{tag}'))
            os.chdir(extracted_folder)

        elif branch and not tag:
            # Clone repo
            repo_name = git_repo.rstrip('/').split('/')[-1].replace('.git', '')
            clone_path = f'repos/{repo_name}'
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
            subprocess.run(['cp', omod, '../../modules'], check=True)

    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        with open("error_logs.txt", "a") as log_file:
            log_file.write(f"Row {idx} ({modules}): {e}\n")
    finally:
        os.chdir('../../')  # Reset to root directory
