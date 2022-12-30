cd ..
pelican --debug
pelican --delete-output-directory
pelican content -o output -s publishconf.py
