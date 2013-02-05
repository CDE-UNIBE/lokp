#!/bin/bash
#
# Open lmkp.views.views and remove the moderate permission in order to run this
# script! There seems to be no way to run the sencha create command with HTTP
# Basic Authentication.
#

cd ..
sencha create jsb -a http://localhost:6543/administration -p app.jsb3
sencha build -p app.jsb3 -d .
# Move and rename app-all.js script
mv -v app-all.js static/administration-ext-all.js
# Clean up
rm -fv app.jsb3 all-classes.js