# MrLixm.github.io

![Last Published](https://img.shields.io/github/last-commit/MrLixm/MrLixm.github.io/master?label=Last%20Published)

This is my personal website, portfolio and blog.

Made using [Pelican](<https://blog.getpelican.com/>) as the static site
generator.
A customized version of [m.css](https://mcss.mosra.cz/>) is used as theme.

# Development

## Git

The branch `dev` **should always be active**. Commit and push on this branch
whenever you have enough important changes.

Once `dev` considered publish-ready you can push it to `master` using 
[publish-online.py](./dev/publish-online.py).

`gh-pages` branch is only used as an intermediate by the script. Nothing should
be manually commited to this branch.

## Dependencies

Built using `Python==3.6.8`.
See [pyproject.toml](pyproject.toml) for packages required.

## [dev/](./dev)

Contains a bunch of useful stuff used to work on the website.

### [new-article.py](./dev/writer/new-article.py)

Run and input new article details in the terminal.
Will create the hierarchy and prepare the .rst template.

### [publish-online.py](./dev/publish-online.py)

Automatize the process of publishing the website online on GitHub.