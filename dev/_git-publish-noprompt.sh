
COMMITNAME=$1
VERSION=$2
DEV_COMMIT="[published][v$VERSION]:$COMMITNAME"
MASTER_COMMIT="[publish][v$VERSION]:$COMMITNAME"

echo "[_git-publish-noprompt.sh] Started publish process with commit: $MASTER_COMMIT"

cd ..
echo "[_git-publish-noprompt.sh] Working directory: $PWD"

# 1. generate site and comit to master:

pelican content -o output -s publishconf.py

ghp-import -m "$MASTER_COMMIT" -b master output # push ./output to local master

git push origin master  # push local master to remote

echo "[_git-publish-noprompt.sh] Site published to origin/master."

# 2. Now commit the /dev branch :

git add .  # add all the modification in the repo for commit
git commit -m "$DEV_COMMIT"  # commit to local
git push origin dev  # push to remote dev branch

echo "[_git-publish-noprompt.sh] dev branch pushed remotely"
