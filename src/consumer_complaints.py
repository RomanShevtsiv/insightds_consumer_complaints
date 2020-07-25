# imports
import csv
import sys
import os
import logging
import argparse
from operator import itemgetter
from datetime import datetime as dt


def str2tup(s):
    return tuple([int(e) for e in s])


class Df:
    def __init__(self, date_format='%Y-%m-%d', buff_size=300, columns=('Product', 'Date received', 'Company')):
        self.data = {}
        self.date_format = date_format
        self.buff_size = buff_size
        self.columns = columns

    def read(self, file):
        logger = logging.getLogger()

        with open(file, 'r') as f:
            headers = next(csv.reader([f.readline()]))
            positions = [headers.index(c) for c in self.columns]
            # at least 3 predefined columns are needed to conduct further analysis
            if len(positions) < 3:
                # "Not all required columns were found
                logger.critical("1: E0001")
                sys.exit()

            i = 2
            lines = f.readlines(self.buff_size)
            while lines:
                for line in csv.reader(lines):
                    if len(line) == len(headers):
                        try:
                            self.add(itemgetter(*positions)(line))
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
                lines = f.readlines(self.buff_size)

    def add(self, line):
        k, c = (line[0].lower(), dt.strptime(line[1], self.date_format).year), line[2].lower()
        if k in self.data.keys():
            if c in self.data[k].keys():
                self.data[k][c] += 1
            else:
                self.data[k][c] = 1
        else:
            self.data[k] = {c: 1}

    def cpl_count(self, k):
        return sum([i for i in self.data[k].values()])

    def cmp_count(self, k):
        return len(self.data[k].keys())

    def cmp_max(self, k):
        return max(self.data[k].items(), key=itemgetter(1))[1]

    def save(self, file, sort=(0, 1)):
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
                cpl = self.cpl_count(k)
                writer.writerow([k[sort[0]], k[sort[1]], cpl, self.cmp_count(k), round(self.cmp_max(k) / cpl * 100)])


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Processes complaints by products, years and companies and generates '
                                                 'aggregate statistics.')
    parser.add_argument('input', type=str, help='path to the file with the data to process')
    parser.add_argument('output', type=str, help='path to the file where the results of analysis will be stored')
    parser.add_argument('--buff_size', type=int, default=1024000,
                        help='read input file by chunks of BUFF_SIZE bytes')
    parser.add_argument('--date_format', type=str, default='%Y-%m-%d',
                        help='format to pasrse date of complaint (see datetime.strptime for details)')
    parser.add_argument('--log', type=str, default='skip', choices=['skip', 'console', 'file'],
                        help='determines how to log warnings')
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

    data = Df(args.date_format, args.buff_size)
    data.read(args.input)
    data.save(args.output, args.sort)

    print("Done!")
