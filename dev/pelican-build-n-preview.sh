cd ..
pelican --debug
pelican --delete-output-directory
pelican content
start http://127.0.0.1:8000
pelican --autoreload --listen
