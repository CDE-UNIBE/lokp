#!/bin/bash

cd ..
sencha create jsb -a http://localhost:6543/ -p app.jsb3
sencha build -p app.jsb3 -d .
# Move and rename app-all.js script
mv -v app-all.js static/main-ext-all.js
# Clean up
rm -fv app.jsb3 all-classes.js