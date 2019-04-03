#!/bin/bash

chown root:www-data django/db.sqlite3
chown root:www-data django

chmod 664 django/db.sqlite3
chmod 775 ./django

