# Author: Roman Shevtsiv <roman.shevtsiv@gmail.com>
#
# License: MIT

import csv
import sys
import os
import logging
import argparse
from operator import itemgetter
from datetime import datetime as dt
from typing import Tuple, Union


def str2tup(s: str) -> Union[Tuple[int], Tuple[int, int]]:
    """Converts string of digits into tuple of integers

    Parameters
    ----------
    s : str
        The string containing digits

    Returns
    -------
    Split bunch of integers: tuple
    """
    return tuple([int(e) for e in s])


class Df:
    """Class is used to represent aggregated dataset, parse input data and export statistics

    Parameters
    ----------
    data : dictionary
        a dictionary with tupples (product, year) as keys and dictionaries {country: number of complaints} as values
    columns : tuple
        a list of columns headers in the source file to read complaint date, company and product

    Methods
    -------
    read(self, file, date_format='%Y-%m-%d', buff_size = 10485760):
        Reads data from file by chunks of specified size, parses predefined columns and stores aggregate information
        into parameter data
    save(self, file, sort=(0, 1)):
        Exports statistics to output file
    _add(self, line, date_format='%Y-%m-%d'):
        Parses one line extracting relevant fields and updating statistics
    _cmp_count(self, k: Tuple[str, int]) -> int:
        For a given key (product and year pair) returns total number of unique companies
    _cmp_max(self, k: Tuple[str, int]) -> int:
        For a given key (product and year pair) returns maximum number of complaints for one company
    _cpl_count(self, k: Tuple[str, int]) -> int:
        For a given key (product and year pair) returns total number of complaints
    """

    def __init__(self, columns: Tuple[str, str, str] = ('Product', 'Date received', 'Company')):
        """Initialises empty dictionary and predefined columns for data extractions"""

        self.data = {}
        self.columns = columns

    def read(self, file: str, date_format: str = '%Y-%m-%d', buff_size: int = 10485760):
        """ Reads data and computes aggregate information

        Reads data from file by chunks of specified size, parses predefined columns and stores aggregate information
        into parameter data

        Parameters
        ----------
        file : str
            Path to the file with the data to process
        date_format : str, optional
            The format to parse date of complaint (default is '%Y-%m-%d')
        buff_size : int, optional
            Limits the number of bites to read as one chunk from the file (default is 10485760)
        """

        logger = logging.getLogger()

        with open(file, 'r') as f:
            headers = next(csv.reader([f.readline()]))
            positions = [headers.index(c) for c in self.columns]
            # at least 3 predefined columns are needed to conduct further analysis
            if len(positions) < 3:
                # Not all required columns were found
                logger.critical("1: E0001")
                sys.exit()

            i = 2
            lines = f.readlines(buff_size)
            while lines:
                for line in csv.reader(lines):
                    if len(line) == len(headers):
                        try:
                            self._add(itemgetter(*positions)(line), date_format)
                        except ValueError:
                            # Can't convert value to date
                            logger.warning(f"{i}: E0201")
                        except:
                            # Unexpected error
                            logger.warning(f"{i}: E0000")
                    else:
                        # Number of values in the row doesn't match number of columns in the header.
                        logger.warning(f"{i}: E0101")
                    i += 1
                lines = f.readlines(buff_size)

    def save(self, file: str, sort: Union[Tuple[int], Tuple[int, int]] = (0, 1)):
        """Exports statistics to output file.

        Parameters
        ----------
        file : str
            The path to the file where the results of analysis will be stored
        sort : tuple, optional
            determines sort oder and order of columns in the output file (default is (0, 1))
            (0,) - sort by product in alphabetical order;
            (1,) - sort by year in ascending order, output year column first;
            (0, 1) - sort by product in alphabetical order then by year in ascending order;
            (1, 0) - sort by year in ascending order then by product in alphabetical order, output year column first.
        """

        with open(file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if sort:
                keys = sorted(self.data.keys(), key=itemgetter(*sort))
            else:
                keys = self.data.keys()
            if sort:
                sort = (sort[0], 1 - sort[0])
            else:
                sort = (0, 1)
            for k in keys:
                cpl = self._cpl_count(k)
                writer.writerow([k[sort[0]], k[sort[1]], cpl, self._cmp_count(k), round(self._cmp_max(k) / cpl * 100)])

    def _add(self, line: Tuple[str, str, str], date_format: str = '%Y-%m-%d'):
        """Processes on line of input data

        Parses one line of input data extracting relevant fields and updating statistics.

        Parameters
        ----------
        line : tuple
            contains data from predefined fields
        date_format : str, optional
            The format to parse date of complaint (default is '%Y-%m-%d')
        """

        k, c = (line[0].lower(), dt.strptime(line[1], date_format).year), line[2].lower()
        if k in self.data.keys():
            if c in self.data[k].keys():
                self.data[k][c] += 1
            else:
                self.data[k][c] = 1
        else:
            self.data[k] = {c: 1}

    def _cmp_count(self, k: Tuple[str, int]) -> int:
        """Calculates number of companies receiving at least one complaint

        For a given product and year pair determines number of companies receiving at least one complaint.

        Parameters
        ----------
        k : tuple(str, int)
            key (product and year pair)

        Returns
        -------
        Number of companies: int
        """

        return len(self.data[k].keys())

    def _cmp_max(self, k: Tuple[str, int]) -> int:
        """Calculates maximum number of complaints for one company

        For a given product and year pair loops over companies and find maximum complaints received by one company.

        Parameters
        ----------
        k : tuple(str, int)
            key (product and year pair)

        Returns
        -------
        Maximum number of complaints: int
        """

        return max(self.data[k].items(), key=itemgetter(1))[1]

    def _cpl_count(self, k: Tuple[str, int]) -> int:
        """Calculates total number of complaints

        For a given product and year pair loops over companies and sums received complaints.

        Parameters
        ----------
        k : tuple(str, int)
            key (product and year pair)

        Returns
        -------
        Total number of complaints: int
        """

        return sum([i for i in self.data[k].values()])


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Processes complaints by products, years and companies and generates '
                                                 'aggregate statistics.')
    parser.add_argument('input', type=str, help='path to the file with the data to process')
    parser.add_argument('output', type=str, help='path to the file where the results of analysis will be stored')
    parser.add_argument('--buff_size', type=int, default=10485760,  # 10 MB
                        help='read input file by chunks of BUFF_SIZE bytes')
    parser.add_argument('--date_format', type=str, default='%Y-%m-%d',
                        help='format to parse date of complaint (see datetime.strptime for details)')
    parser.add_argument('--log', type=str, default='skip', choices=['skip', 'console', 'file'],
                        help='determines how to log warnings'
                             'skip - will silently skip noncritical issues;'
                             'console - will output to the console all detected issues;'
                             'file - will write all detected issues to the file parse_errors.log.'
                             '* all issue are displayed in the format <line number>: <code>, you can find codes '
                             'description in the documentation.')
    parser.add_argument('--sort', type=str2tup, default=(0, 1), choices=[(0,), (1,), (0, 1), (1, 0)],
                        help='determines sort oder and order of columns in the output file:'
                             '0 - sort by product in alphabetical order;'
                             '1 - sort by year in ascending order, output year column first;'
                             '01 - sort by product in alphabetical order then by year in ascending order;'
                             '10 - sort by year in ascending order then by product in alphabetical order, output year '
                             'column first.')
    args = parser.parse_args()

    if args.log == 'file':
        logging.basicConfig(filename=os.path.join(os.path.dirname(args.input), 'parse_errors.log'),
                            format='%(message)s', filemode='w')
    elif args.log == 'skip':
        logging.basicConfig(level=logging.CRITICAL)

    data = Df()
    data.read(args.input, args.date_format, args.buff_size)
    data.save(args.output, args.sort)

    print("Done!")
