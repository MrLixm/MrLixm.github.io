# dev

A python package of developer resources for working on the website. 

> All the content in here does not contribute *directly* to the website. This means
any edit on files done here doesn't need to trigger a publish to master.

# Usage

## CLI

```shell
cd .../Blog
python -m dev --help
# display CLI help
```

### publishing the blog

```shell
cd .../Blog
python -m dev publish
# start the interactive publisher
```

## python

```python
import dev.publish

print(dev.__version__)

dev.publish.interactive_publish()
```