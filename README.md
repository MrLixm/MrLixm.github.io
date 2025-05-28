# MrLixm.github.io

![Last Published](https://img.shields.io/github/last-commit/MrLixm/MrLixm.github.io/gh-pages?label=Last%20Published)

This is my personal website, portfolio and blog. To access it, head over to
https://liamcollod.xyz/.

It is fully built by me in Python as a static site that relies only on standard html
and css to work.

Content is authored with a mix of .rst files and html jinja templates.

You can get more information on the authoring process by
checking https://liamcollod.xyz/.doc.

## structure

- `libs/lxmsite`: the custom-made python library that allow to parse the file-structure
  and build a html website out of it.
- `tests`: unittests for the lib
- `site`: the source files for the site
- `scripts`: individual scripts to perform action such as building the website.
  They make use of `site` and `lxmsite`.

## scripts

### [image-optimize.py](scripts/image-optimize.py)

Usually called with 
```
--quality 60 --maxsize 1500x2500
```