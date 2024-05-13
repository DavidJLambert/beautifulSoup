""" beautiful_mitre.py

SUMMARY:
1.  Go to https://attack.mitre.org/tactics/TA0043.
2.  Scrape and print the contents of the Techniques table on this webpage.

REPOSITORY:
  https://github.com/DavidJLambert/beautifulSoup

AUTHOR:
  David J. Lambert

DATE:
  July 10, 2020

DESCRIPTION:
"""

import requests
from bs4 import BeautifulSoup

print("Starting.")

url = "https://attack.mitre.org/tactics/TA0043"
response = requests.get(url)
if response.status_code != 200:
    print(response.status_code)
soup = BeautifulSoup(response.content, 'html.parser')

trs = soup.find_all('tr')

for tr in trs:
    # Find all cells in this row.
    tds = tr.find_all('td')
    for td in tds:
        anchors = td.find_all('a')
        for anchor in anchors:
            print("anchor", anchor['href'])
        # Get the text in this cell.
        cell = td.text.strip()
        print("cell", cell)

print("Done.")
