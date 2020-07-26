#!/bin/bash

echo "Test 1"
python3.8 ../src/consumer_complaints.py ./test_1/input/complaints.csv ./test_1/output/report.csv

echo "Test 2"
python3.8 ../src/consumer_complaints.py ./test_2/input/complaints.csv ./test_2/output/report.csv

echo "Test 3"
python3.8 ../src/consumer_complaints.py --date_format %m/%d/%y ./test_3/input/complaints.csv ./test_3/output/report.csv

echo "Test 4"
python3.8 ../src/consumer_complaints.py ./test_4/input/complaints.csv ./test_4/output/report.csv

echo "Test 5"
python3.8 ../src/consumer_complaints.py --log file ./test_5/input/complaints.csv ./test_5/output/report.csv

echo "Test 6"
python3.8 ../src/consumer_complaints.py --log file ./test_6/input/complaints.csv ./test_6/output/report.csv
