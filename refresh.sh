#!/bin/bash

find -name '*.[ch]' > cscope.files
find -name 'Makefile' >> cscope.files
find -name '*.sh' >> cscope.files
find -name '*.xml' >> cscope.files
find -name '*.java' >> cscope.files
find -name '*.md' >> cscope.files

vim -c '%sort! | write | quit ' cscope.files

cscope -bq
