#!/bin/bash

chown root:www-data django
chown root:www-data media_root

chmod 775 ./django
chmod 775 ./media_root

