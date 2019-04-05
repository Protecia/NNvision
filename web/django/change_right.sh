#!/bin/bash

chown root:www-data django/database/db.sqlite3
chown root:www-data django/database
chown root:www-data django
chown root:www-data media_root

chmod 664 django/database/db.sqlite3
chmod 775 ./django
chmod 775 django/database
chmod 775 media_root

