# MrLixm.github.io

![Last Published](https://img.shields.io/github/last-commit/MrLixm/MrLixm.github.io/master?label=Last%20Published)

This is my personal website, portfolio and blog.

Made using [Pelican](<https://blog.getpelican.com/>) as the static site
generator.
A customized version of [m.css](https://mcss.mosra.cz/>) is used as theme.

# Development

## Git

There is 2 active branchs `dev` and `master`.

- `master` is where the builded static website lives.
- `dev` is where the code for the website lives.

You **never** checkout `master` nor push directly to it.

Any edit shoudl be performed in the `dev` branch then use the actions to build 
and publish the website.

You can create any branch from `dev` but you have to merge them back to dev,
THEN publish `dev`. This means it is not recommended to work directly on `dev`.


## Dependencies

Developed under Windows, using another OS might lead to unexpected results.

### Python

See [pyproject.toml](pyproject.toml) for packages required.

### Misc

Git Bash for Windows at `C:\Program Files\Git\bin\sh.exe`

# Workflow

See the [./dev](./dev) package to see the tools accessible.

```shell
python -m dev --help
```