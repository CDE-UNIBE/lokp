#!/bin/bash

cd ..
sencha create jsb -a http://localhost:6543/ -p app.jsb3
sencha build -p app.jsb3 -d .
mv -v app-all.js static/main-ext-all.js
rm -fv app.jsb3 all-classes.js
