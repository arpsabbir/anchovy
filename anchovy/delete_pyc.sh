#!/bin/bash
cd `dirname $0`/../
# delete pyc files
echo "Deleting all pyc files..."
find . -iname '*.pyc' -exec rm {} \;
echo "Complete."
find . -iname '*.pyc'
