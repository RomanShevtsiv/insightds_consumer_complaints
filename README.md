# Data Engineering coding challenge
## Overview
This repo was created to respond to the [Insight Data Engineering](https://insightfellows.com/data-engineering) coding 
challenge.  

The federal government provides a way for consumers to file complaints against companies regarding different financial 
products, such as payment problems with a credit card or debt collection tactics.

Description of the expected input data structure can be found in the 
[Consult the Consumer Finance Protection Bureau's technical documentation](https://cfpb.github.io/api/ccdb/fields.html). 

The challenge is about identifying the number of complaints filed and how they're spread across different companies.

## Description

Python script will do some magic for you. 

## Usage

Just follow these simple steps to process you data and ge the expected results: 
* put your data as `./input/complaints.csv` file;
* run `run.sh` script in your shell;
* inspect the results in `./output/report.csv` file.

*You can always adjust input file name and path and output file name and path in `run.sh` script to meet your needs or 
even run the adjusted command directly in you terminal.*  

### Command line arguments
You can get help by specifying `-h` key to the `consumer_complaints.py`:

<code>~ % python ./src/consumer_complaints.py -h</code>

You can employ the following options:
* `--buff_size`: will read file in chunks of the specified size in bytes (values between 10 MB 
and 100 MB should be fine);
* `--date_format`: format to parse date of complaint (see datetime.strptime for details and posiible options)
* `--sort`: determines sort oder and order of columns in the output file
     * **0** - sort by product in alphabetical order;
     * **1** - sort by year in ascending order, output year column first;
     * **01** - sort by product in alphabetical order then by year in ascending order;
     * **10** - sort by year in ascending order then by product in alphabetical order, output year column first;
* `--log`: determines how to log warnings
     * **skip** - will silently skip noncritical issues;
     * **console** - will output to the console all detected issues;
     * **file** - will write all detected issues to the file parse_errors.log.

*You can find defaults in the console help.*

### Goodies

1. One can change the order of columns in the input file.
2. Some columns can be missing or empty, the script will only require `Product`, `Date received` and `Company` columns 
to be present and non empty.

### Warnings and Issues

What can go wrong?
1. Script will stop if input file doesn't exist.
2. Script will stop if one of the thee required column headers is missing in the first line of the file.
3. Script will skip line if number of values doesn't match the number of columns in the header.
4. Script will skip line if the date of complaint value can't be converted using specified format.
5. Script will treat empty value in the product field as separate product type.
6. Script will treat empty value in the company field as separate company name.
7. Script not try to guess the correct order of values in some line if they are shuffled.
8. Script not try to guess if required values are available in some line if the number of values for that line doesn't 
match the number of headers.

All issue are displayed or written to the file in the format `<line number>: <code>`, you can find codes description 
below.

Warning codes:
* `E0000`: unknown error;
* `E0001`: not all required columns were found;
* `E0101`: number of values in the row doesn't match number of columns in the header;
* `E0201`: can't convert value to date using specified format.

## Tests

You can find tests in `./insight_testsuite/` folder.

## Author

This repository was made by **Roman Shevtsiv**.

You can reach me by email [roman.shevtsiv@gmail.com](roman.shevtsiv@gmail.com) or 
via [LinkedIn](roman./shevtsiv@gmail.com).

