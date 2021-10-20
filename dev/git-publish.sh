read -p "This will publish the output directory to github that will update the web-page, would you like to continue ?
(y/n): " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

read -p "Give a name to this commit (change made): " "cname"

cd ..
echo $PWD

pelican content  # build to the /output directory using pelicanconf.py

ghp-import -m "publish: $cname" -b master output # push /output to master

git push origin master  # push master

echo "[master] Site published to master. commit: $cname"

git add .
git commit -m "published version: $cname"
git push origin dev

echo "[dev] dev branch pushed remotely"
