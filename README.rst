crossword_puzzles.py
--------------------

SUMMARY:
  Downloads crossword puzzle pdf files from www.puzzlesociety.com.
  NOT RUNNABLE, THE SUBSCRIPTION TO THE CROSSWORD PUZZLE WEBSITE HAS EXPIRED.

VERSION:
  0.5.3

AUTHOR:
  David J. Lambert

DATE:
  June 4, 2019

DESCRIPTION:
  Author has a subscription to crossword puzzles published in pdf format 6 days
  per week at www.puzzlesociety.com.  Manually logging into that site and
  manually downloading those puzzles is time-consuming.  This program logs into
  that website and downloads the pdf files for all dates from a starting date,
  entered interactively, to the current date, inclusive.

  Uses "requests" for http and "Beautiful Soup" for parsing web page text.

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
