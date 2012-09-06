#!/bin/bash
#
# Removes all compiled Python files with suffix pyc

rm -fv `find ../.. -type f | grep \.pyc$`