""" aact_downloads.py

SUMMARY:
1.  Go to https://aact.ctti-clinicaltrials.org/download.
2.  Download all the pipe-delimited files, which are packaged into zip
    files whose names start with a data formatted as yyyymmdd.
3.  Extract "studies.txt" from each zip file and naming it yyyymmdd.txt.
4.  Delete the zip file, since we no longer need it, and since each zip file is
    approximately 5.4 times the size of the unzipped "source.txt".

REPOSITORY:
  https://github.com/DavidJLambert/beautifulSoup

AUTHOR:
  David J. Lambert

DATE:
  May 12, 2024

DESCRIPTION:
  In 2021, a student of mine had downloaded 56 of these zip files, manually
  extracted "source.txt" from each zip file, and asked me to help him analyze
  the data in these 56 copies of "source.txt", which I did.

  In May 2024, this student wanted to analyze all the data released up to then.
  But at the start of 2023, the source of these zip files,
  aact.ctti-clinicaltrials.org, had stopped combining the data into monthly
  summaries, and started releasing data daily.  By May 12, 2024, a total of 537
  files had been released, too many to manually download and unzip.

  This program, aact_downloads.py, was written to automatically perform the
  steps listed in the summary above.  It was executed, and took more than 24
  hours to run to completion, downloading 475 zip files in the process, creating
  138 GB of text files.

  This program was written so that it could be stopped by pressin control-C, and
  execution resumed later, skipping the zip files that had been downloaded
  earlier.

  Two of the zip files cannot be downloaded, since the URL for them is invalid,
  so this program has to be able to continue running in spite of errors.
"""

import os
import traceback
import glob
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile

# Constants.
URL = "https://aact.ctti-clinicaltrials.org"
FOLDER = "E:/MattM/Step1-Read_Files/data/"

# Clean up any temp files.
file_list = glob.glob(FOLDER + "*.zip") + glob.glob(FOLDER + "studies.txt")
for file_path in file_list:
    print(f"Removing {file_path}...")
    os.remove(file_path)
else:
    print("Done cleaning up files.")

# Get the HTML for this web page.
response = requests.get(URL + "/download")

# Process HTML with Beautiful Soup.
soup = BeautifulSoup(response.text, features="lxml")

# Get a list of all the "select" tags.
select_list = soup.find_all("select")

# Get the 4th "select" tag.
select4 = select_list[3]

# Find all anchors under this selection.
anchor_list = select4.find_all("a")
print(f"Number of anchors: {len(anchor_list)}.")

# Iterate through anchors.  Each anchor is for a zip file to download.
for anchor in anchor_list:
    try:
        file_name = anchor.getText().strip()
        # Extract the date part (yyyymmdd) from the zip file name.
        yyyymmdd = file_name.split("_")[0]
        destination = FOLDER + yyyymmdd + ".txt"
        # Check to see if <yyyymmdd>.txt exists.
        if os.path.exists(destination):
            print(f"File {destination} already exists.")
        else:
            print(f"Downloading {file_name}.")
            file_url = URL + anchor.get("href")
            # Try to get this zip file.
            response = requests.get(file_url)
            # Raise exception if there's trouble.
            response.raise_for_status()
            # Write zip file.
            with open(FOLDER + file_name, mode="wb") as writer:
                writer.write(response.content)
            # From the zip file, extract "studies.txt" as <yyyymmdd>.txt
            # See https://stackoverflow.com/questions/44079913/renaming-the-extracted-file-from-zipfile
            with ZipFile(FOLDER + file_name, mode="r") as zipfile:
                zipfile.getinfo("studies.txt").filename = yyyymmdd + ".txt"
                zipfile.extract(member="studies.txt", path=FOLDER)
            # Delete the zip file.
            os.remove(FOLDER + file_name)
            # Rename "studies.txt" to <yyyymmdd>.txt.
            # os.rename(FOLDER+"studies.txt", destination)
    except KeyboardInterrupt:
        print("Keyboard Interrupt received, exiting now.")
        break
    except Exception:
        print(traceback.print_exc())

print("ALL DONE.")
