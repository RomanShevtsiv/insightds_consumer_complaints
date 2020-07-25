# imports
import csv
import sys
import os
import logging
from operator import itemgetter
from datetime import datetime as dt

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
                # print('Chunk done')


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

    def save(self, file, sort=False):
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if sort:
                keys = sorted(self.data.keys(), key=itemgetter(*sort))
            else:
                keys = self.data.keys()
            if sort:
                sort = (sort[0], 1-sort[0])
            else:
                sort = (0,1)
            for k in keys:
                cpl = self.cpl_count(k)
                writer.writerow([k[sort[0]], k[sort[1]], cpl, self.cmp_count(k), round(self.cmp_max(k)/cpl*100)])


if __name__ == '__main__':

    if len(sys.argv) < 3:
        # Not enough arguments
        sys.exit("Not enough arguments, at least two required.")

    params = {
        'date_format': '%Y-%m-%d',
        'buff_size': 300,
        'sort': (0, 1),
        'log': 'skip',
        'input': sys.argv[-2],
        'output': sys.argv[-1]
    }

    if not os.path.isfile(params['input']):
        # Input file doesn't exist
        sys.exit("Input file with data doesn't exist.")

    i = 1
    while i < len(sys.argv)-2:
        if sys.argv[i] == '-date_format':
            params['date_format'] = sys.argv[i+1]
            i += 2
        if sys.argv[i] == '-log':
            params['log'] = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == '-buff_size':
            params['buff_size'] = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '-sort':
            params['sort'] = tuple([int(l) for l in sys.argv[i + 1]])
            i += 2
        else:
            i += 1

    if params['log'] == 'file':
        logging.basicConfig(filename=os.path.join(os.path.dirname(params['input']), 'parse_errors.log'),
                            format='%(message)s', filemode='w')
    elif params['log'] == 'skip':
        logging.basicConfig(level=logging.CRITICAL)

    data = Df(params['date_format'], params['buff_size'])
    data.read(params['input'])
    data.save(params['output'], params['sort'])

    print("Done!")
