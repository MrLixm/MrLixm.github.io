
COMMITNAME=$1
VERSION=$2
TARGET_BRANCH=$3
DEV_COMMIT="[published][v$VERSION]:$COMMITNAME"
MASTER_COMMIT="[publish][v$VERSION]:$COMMITNAME"
CURRENT_BRANCH=$(git branch --show-current)

echo ""
echo "[build-n-publish.sh] Started publish process with commit message : \"$MASTER_COMMIT\""
echo "[build-n-publish.sh] working directory : $PWD"
echo "[build-n-publish.sh] current branch : $CURRENT_BRANCH"
echo "[build-n-publish.sh] target branch : $TARGET_BRANCH"

# 1. generate site and comit to master:

pelican content -o output -s publishconf.py

# copy the README to output before commit so it's pushed to master
cp -v README.md output/README.md

ghp-import -m "$MASTER_COMMIT" -b master output # push ./output to local master

git push origin $TARGET_BRANCH  # push local master to remote

echo "[build-n-publish.sh] blog pushed to \"origin/$TARGET_BRANCH\"."

# 2. Now commit the current branch :

git add .  # add all the modification in the repo for commit
git commit -m "$DEV_COMMIT"  # commit to local
git push

echo "[build-n-publish.sh] branch \"$CURRENT_BRANCH\" pushed remotely"
echo "[build-n-publish.sh] Finished."
