read -p "This will publish the output directory to github that will update the web-page, would you like to continue ?
(y/n): " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

cd ..
echo $PWD

pelican content  # build to the /output directory using pelicanconf.py

<<<<<<< HEAD
ghp-import output -b temp

git push origin temp:master

echo "Site published to master"
=======
ghp-import output
>>>>>>> parent of a08055d... Update documentation
