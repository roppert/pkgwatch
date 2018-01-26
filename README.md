# pkgwatch
Tool to check for upgradeable packages on debian based systems and mail result

Looks for a config file called pkgwatch.ini in user home with fallback
to look for that config file in same directory program is started from.

**Note** This tool relies on the package database being updated in some other manner (using cron-apt for example)
