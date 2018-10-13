""" crossword_puzzles.py

SUMMARY:
  Downloads crossword puzzle pdf files from www.puzzlesociety.com.

VERSION:
  0.5.1

AUTHOR:
  David J. Lambert

DATE:
  October 12, 2018

DESCRIPTION:
  Author has a subscription to crossword puzzles published in pdf format 6 days
  per week at www.puzzlesociety.com.  Manually logging into that site and
  manually downloading those puzzles is time-consuming.  This program logs into
  that website and downloads the pdf files for all dates from a starting date,
  entered interactively, to the current date, inclusive.

  Uses "requests" for http and "Beautiful Soup" for parsing web page text (CSS,
  HTML, and javascript).

COMMENT ON THE CONSTRUCTION OF THIS PROGRAM:
  The URL for each puzzle is www.puzzlesociety.com/daily-commuter/yyyy/mm/dd,
  where yyyy is the 4-digit year, mm is the 2-digit month, and dd is the 
  2-digit day.  The first valid date is 2001/10/29.  There is no puzzle on
  Sundays.  There ARE web pages for every day of the week.  Except for Sundays,
  each web page contains a hyperlink to a pdf file containing that day's
  crossword puzzle.  The Sunday web pages have hyperlinks to the pdf file for
  the previous day (Saturday).

  The web pages are in date sequence, so I could just start at 2001/10/29,
  increment the date (skipping Sundays), construct the URL for that day's
  puzzle, go to that URL, and fetch that day's puzzle pdf.  But I do not
  do that, because that bypasses how the web site is constructed.

  End-users are supposed to start on one of the web pages, and use one of two
  arrow controls to go to the next or previous web page containing a puzzle,
  skipping the Sunday web pages.  Thus, this program also does that: it
  examines the HTML for those arrow controls, and goes to the web pages those
  arrow controls take to you.  This is why the program is based on the web
  page URLs, not the dates embedded in the URLs.

  I only increment the date past web pages where the server responds with
  Status Code 500.  For some reason, the web server responds with Status Code
  500 when trying to get the web pages for May 8-15 of 2011.
"""

import requests
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from time import sleep
import os
import sys
from getpass import getpass


# Global string constants.

SKIP = 'skip'
EXIT = 'exit'
SUNDAY = 6
ONE_DAY = timedelta(days=1)
CONTINUE = 'continue'
URL_ROOT = 'https://www.puzzlesociety.com'
SAMPLE_MSG = 'Sample Only. Become a Puzzle Society member to play'
MAX_PUZZLES = 10000


def main():
    """ Main program."""

    num_puzzles = 0

    with requests.Session() as session:
        # Get login credentials
        login_data = get_login_credentials()

        # Log onto website.
        login_url = URL_ROOT + '/sessions'
        login = session.post(url=login_url, data=login_data)
        action = error_check(login.status_code, login_url)

        # Get start date
        date_obj = get_start_date()

        # Get output folder.
        folder = get_folder()

        # Don't loop forever.
        while num_puzzles < MAX_PUZZLES:

            page_url = url_from_date(date_obj)

            # Go to next web page.
            page = session.get(url=page_url)
            if error_check(page.status_code, page_url) == SKIP:
                # Skip this page, go to next one.
                date_obj += ONE_DAY
                continue

            # Get page text, "soup" it.
            page_html = page.text
            if not num_puzzles and page_html.find(SAMPLE_MSG) > -1:
                # Redirected to sample puzzle page, so login failed.
                print('Login failed, exiting.')
                exit(1)
            soup = BeautifulSoup(page_html, 'lxml')

            # Get URL of pdf from page text.
            for link in soup.find_all('a', attrs={'target': '_new'}):
                pdf_url = link.get('href')

            # Fetch next pdf file.
            pdf = session.get(url=pdf_url)
            if error_check(pdf.status_code, page_url) == SKIP:
                # Skip this page, go to next one.
                date_obj += ONE_DAY
                continue

            # Write pdf file to disk.
            file_name = folder + 'tmdcp' + date_obj.strftime('%Y%m%d') + '.pdf'
            with open(file_name, 'wb') as writer:
                writer.write(pdf.content)
            num_puzzles += 1

            # Get URL of the next web page.
            links = soup.find_all('a', attrs={'title': 'Play next puzzle.'})
            for link in links:
                next_page_url = URL_ROOT + link.get('href')

            # Time to quit?
            if not len(links) or page_url == next_page_url:
                print('No more puzzles, exiting.')
                exit(0)

            # Prep for next loop.
            page_url = next_page_url
            date_obj = date_from_url(next_page_url)

            # Show progress.
            if not (num_puzzles % 20):
                print('Puzzle #{}, from {}'.format(num_puzzles, page_url))

            # To keep load on web server low, so it won't kill this connection.
            sleep(1)

        # Reached MAX_PUZZLES.
        print('The next page is {}.'.format(page_url))


def error_check(status_code, url):
    """ Checks the HTTP Status Code for all HTTP commands issued.

    Args:
        status_code (int): status code for the most recent HTTP command.
        url (string): the URL targeted by the most recent HTTP command.
    Returns:
        action (string): action to take based on Status Code
    Raises:
        none.
    """
    msg = 'Status code {} for {}, {}.'
    if status_code == 500:
        # Status Code 500.
        action = SKIP
        print(msg.format(status_code, url, action))
    elif (status_code//100) != 2:
        # Status Code not 2XX.
        action = EXIT
        print(msg.format(status_code, url, action))
        exit(status_code)
    elif status_code != 200:
        # Status Code 2XX, but not 200.
        action = CONTINUE
        print(msg.format(status_code, url, action))
    else:
        # Status Code 200, print nothing, take no special action.
        action = None
    return action


def get_start_date():
    """ Gets valid date string from user.  The first valid date is 2001/10/29.

    Args:
        none.
    Returns:
        Date (date object).  Date object corresponding to entered start date.
    Raises:
        none.
    """
    first_date = date(2001, 10, 29)  # Date object.
    last_date = date.today() + ONE_DAY  # Date object.

    while True:
        date_string = input('Enter puzzle start date (format "yyyy/mm/dd"): ')
        try:
            date_obj = date_from_string(date_string)
            if first_date <= date_obj <= last_date:  # Date objects.
                break
            else:
                msg = '{} is not between {} and {}.  Please try again.'
                print(msg.format(date_string, first_date, last_date))
        except ValueError:
            print('{} is not in "yyyy/mm/dd" format.'.format(date_string))
    if date_obj.weekday() == SUNDAY:
        date_obj += ONE_DAY
        print("Your start date is Sunday, so we'll start the next day.")
    return date_obj


def get_folder():
    """ Gets folder path from user with write permissions to it.

    Args:
        none.
    Returns:
        folder (string): path of folder that's writeable.
    Raises:
        none.
    """
    while True:
        folder = input('Enter output folder path with slashes (/): ')
        if not os.path.isdir(folder):
            print('"{}" does not exist or is not a folder'.format(folder))
        elif not os.access(folder, os.W_OK):
            print('"{}" is not writeable'.format(folder))
        else:
            break
    if folder[-1] != '/':
        folder += '/'
    return folder


def get_login_credentials():
    """ Gets username and password from end-user.

    Args:
        none.
    Returns:
        login data (dict).
    Raises:
        none.
    """
    username = input('Enter website username: ')

    prompt = 'Enter website password: '
    if sys.stdin.isatty():
        # Using terminal, OK to use getpass.
        password = getpass(prompt)
    else:
        # Use "input" (echoes password).  Getpass detects Eclipse & IDLE (warns
        # & uses "input"), doesn't detect PyCharm & hangs, don't know what other
        # environments do, just play it safe & use "input".
        password = input(prompt)
    return {'username': username, 'password': password}


def url_from_date(date_obj):
    """ Gets URL for given date.

    Args:
        date_obj (date object):
    Returns:
        url (string):
    Raises:
        none.
    """
    return URL_ROOT + '/daily-commuter/' + date_obj.strftime('%Y/%m/%d')


def date_from_url(url):
    """ URL contains date, in 'yyyy/mm/dd' format, convert it to date object.

    Args:
        url (string): the URL targeted by the most recent HTTP command.
    Returns:
        date (date object): the date object for the date embedded in the url.
    Raises:
        none.
    """
    return date_from_string(url[-10:])


def date_from_string(date_string):
    """ Converts date, in 'yyyy/mm/dd' format, to corresponding date object.

    Args:
        date_string (string): the URL targeted by the most recent HTTP command.
    Returns:
        date (date object): the date object for date_string.
    Raises:
        none.
    """
    return datetime.strptime(date_string, '%Y/%m/%d').date()


if __name__ == '__main__':
    main()
