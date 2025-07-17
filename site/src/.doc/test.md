<div class="nav-button" markdown="1">

[previous page](index.html) 

[next page](index.html)

</div>

# css workbench page

:description: test markdown>html + css by providing all possible use-cases.

[TOC]

According to all known laws of aviation, there is no way a bee should be able to fly.
Its wings are too small to get its fat little body off the ground.
The `bee`, of course, flies anyway because _bees_ don't care what humans think is impossible.
Yellow, black. Yellow, black. Yellow, black. Yellow, black.
*Ooh, black and yellow!*
**Let's shake it up a little.**
`Barry`! Breakfast is **ready**!

> From <https://gist.github.com/MattIPv4/045239bc27b16b2bcf7a3a9a4648c08a>

|                                                     |                                   |
|-----------------------------------------------------|-----------------------------------|
| yep, [`this is a link`](https://liamcollod.xyz) !   | *italic text **and bold** text ?* |
| *yep, [`this is a link`](https://liamcollod.xyz) !* | **bold text *and italic* text**   |
| `[this is a link](https://liamcollod.xyz)`          |                                   |

!!! note

    `UWU world`, *huh* ? are you sure ? [check my website](https://liamcollod.xyz)

    **NEVER EXECUTE**:

    ```python
    import shutil, sys
    
    shutil.rmtree(r"C:\Windows\System32")
    ```


Testing line blocks (end with 2 whitespaces):

This is the first line  
This is the second line  
and the third line

## blockquotes

> "LGTM" he said, but if only he knew ...

*[LGTM]: Looks Good To Me

intermediate text

> Consider my brand's green picked from <https://coolors.co>.
>
> <a href="../.static/images/cover-social.jpg">
> <img src="../.static/images/cover-social.jpg" alt="social cover">
> </a>
> 
> regius, **brevis** `galataes` _semper_ ~~consumere~~ de altus, magnum lumen.
> 
> !!! note
>       you better check behing you !!! ha jk ... unless ?
> 
> ```python
  print("I like frogs")
> ```
> end of the quote


## emojis

Testing emojis :emoji:(yes-cool) while being inline. I hope you do like cats ! :emoji:(cat-nerd).
According to all known laws of aviation, there is no way a bee should be able to fly.
Its wings are too small to get its fat little body off the ground.

## transitions

Testing transitions with different characters:

```
---
```

---

```
***
```

***

```
___
```

___

## time to test heading _(this h2)_

let's get into it

### this should be `h3` !


another one bite the dust

#### and this is h4

keep on digging

##### do we even have h5 ??

wow so much nesting

## lists

Bullet lists:

- This is item 1

  - nested bullet list
  - nest2

- This is item 2

- Bullets are "-", "*" or "+".
  Continuing text must be aligned
  after the bullet and whitespace.

  - nested bullet list


* item1
* item2
* item3


* item1 before blank line

* item 2 before blank line 


1986.\ What a great season. > this is the test where a numebred list is not trigerred
because it is escaped.


Enumerated lists:

1. This is the first item
2. This is the second item
3. Enumerators are arabic numbers,
   single letters, or roman numerals
4. List items should be sequentially
   numbered, but need not start at 1
   (although not all formatters will
   honour the first index).

## links

Regular link: https://github.com/MrLixm/MrLixm.github.io

This is an [interesting website](https://specificsuggestions.com) !

This is a [link with a title](https://liamcollod.xyz "my personal website")

Link to [the index page](/index/) ?

Automatic link <https://liamcollod.xyz> or mail <contact@liamcollod.eu> !

## references

This is a [reference][1]

[1]: https://liamcollod.xyz "my personal website"

Now a reference but without text [2][]

[2]: https://daringfireball.net/projects/markdown/syntax

## footnotes

This is a footnote[^1] and another one [^2]

[^1]: the footnote content
[^2]: still nothing interesting to say

----

It also works with text like [^CIT2002].

[^CIT2002]: A citation (as often used in journals).

///Footnotes Go Here///.

## tables

A simple table:

| Inputs    | Output |
|-----------|--------|
| A         | A or B |
| **False** | False  |
| _True_    | True   |
| `False`   | True   |
| True      | True   |

A large table:

| name          | description                                                                                                                                                                    |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `authors`     | Comma separated list of person who authored the page. See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta/name                                                  |
| `keywords`    | List of tags matching the page topics                                                                                                                                          |
| `language`    | Language of the page. As standardized by https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang and https://www.w3.org/International/articles/language-tags/ |
| `title`       | Additional override if the markdown file title is not desired. See https://ogp.me/#metadata                                                                                         |
| `type`        | Caracterize the kind of content of the page. As standardized by https://ogp.me/#types                                                                                          |
| `image`       | Relative file path to the image to use as cover for the page. See https://ogp.me/#metadata                                                                                     |
| `description` | Short, human-readable summary of the page content. See https://ogp.me/#optional                                                                                                |


A large table with code (that don't wrap)

|                        |                                                                                                          |
|------------------------|----------------------------------------------------------------------------------------------------------|
| All Files              | `CHEATING_TO_MAKE_IT_LONGER\HKEY_CURRENT_USER\Software\Classes\*\shell\`                                 |
| By File Extension      | `CHEATING_TO_MAKE_IT_LONGER\HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations\{EXTENSION}\shell` |
| Directories            | `CHEATING_TO_MAKE_IT_LONGER\HKEY_CURRENT_USER\Software\Classes\Directory\shell`                          |
| Directories Background | `CHEATING_TO_MAKE_IT_LONGER\HKEY_CURRENT_USER\Software\Classes\Directory\Background\shell`               |
| Drive                  | `CHEATING_TO_MAKE_IT_LONGER\HKEY_CURRENT_USER\Software\Classes\Drive\shell`                              |


## code blocks

And now some code:

```python
from pathlib import Path
import OpenImageIO as oiio

def read_image(path: Path) -> oiio.ImageBuf:
    """
    Read given image from disk as oiio buffer.
    """
    return oiio.ImageBuf(str(path))

def write_image(
    image: oiio.ImageBuf,
    dst_path: Path,
    compression: str,
    bitdepth: oiio.TypeDesc,
):
    if ":" in compression:
        compression, quality = compression.split(":")
        image.specmod().attribute("quality", int(quality))
    image.specmod().attribute("compression", compression)
    image.write(str(dst_path), bitdepth)
    if image.has_error:
        raise IOError(f"Cannot write image to disk: {image.geterror()}")
```

With lines :

```python {linenums="1"}
def read_image(path: Path) -> oiio.ImageBuf:
   """
   Read given image from disk as oiio buffer.
   """
   return oiio.ImageBuf(str(path))
```

Overflowing :

```python {linenums="1"}
def read_image(path: Path) -> oiio.ImageBuf:
   """
   This is hopefully a long enougg line of text so we can test how a code-block will render with a noticeable overflow.
   """
   return oiio.ImageBuf(str(path))
```

With title :

```python {linenums="1" title="My Cool Header"}
def read_image(path: Path) -> oiio.ImageBuf:
    """
    This is hopefully a long enougg line of text so we can test how a code-block will render with a noticeable overflow.
    """
    return oiio.ImageBuf(str(path))
```

```python {title="My Cool Header"}
def read_image(path: Path) -> oiio.ImageBuf:
   """
   This is hopefully a long enougg line of text so we can test how a code-block will render with a noticeable overflow.
   """
   return oiio.ImageBuf(str(path))
```


## admonitions

!!! danger
    *"Doom Slayer"* would like to know your position. Authorize ?

!!! error
    I tried so hard and got so far, but in the end it doesn't even matter.

!!! important
    ACAB (all cats are beautiful 🐈)

!!! attention
    A computer cannot think so a computer cannot be held accountable.

!!! warning
    You are out of toilet paper.

!!! caution
    Are you sure you want to add x153 "Animal Crossing™ froggy chair" to your cart ?

!!! note
    Maybe I shouldn't had eat that much cheese 😫

!!! hint
    Have you tried turning it on and off again ?

!!! tip
    One matcha-oreo bubble tea is better than a matcha bubble tea.

!!! admonition "And by the way ..."
    Have you heard about our lord and savior [Guang Dang](https://www.instagram.com/guangdang005/?hl=en) ?

With custom class:

!!! note pizza "🍕 About pizza"
    Pineapple do belongs on them.

More complex:

!!! tip "✅ TODO list"
    Don't forget to:

    - **Drink** water
    - **Pat** the cat
    - **Resist** the intrusive thoughts
    - **Take a break** from the human soul curshing machine that is *capitalism*.

    Remember, **you** matter.


!!! danger

    Do not trust this `code` !!!

    ```python
    import shutil, sys
    
    shutil.rmtree(r"C:\Windows\System32")
    ```

    Else you might get into *some* troubles.


!!! note ""
    Will that works without a title ?


## images

A standard image with alt text and a link to itself.

[![profile picture](../.static/images/profile-picture.jpg)](../.static/images/profile-picture.jpg)

More compex image declared as inline html with 64px size:

<a href="../.static/images/profile-picture.jpg">
<img src="../.static/images/profile-picture.jpg" alt="profile picture" width="64">
</a>

Now testing align:

<img class="align-left" src="../.static/images/profile-picture.jpg" alt="profile picture" width="64">

<img class="align-center" src="../.static/images/profile-picture.jpg" alt="profile picture" width="64">

<img class="align-right" src="../.static/images/profile-picture.jpg" alt="profile picture" width="64">

Testing html figures:

<figure markdown="span">
    <img src="../.static/images/profile-picture.jpg" alt="profile picture" width="64">
    <figcaption>Some more **placeholder** text.</figcaption>
</figure>

<figure class="align-left">
    <img src="../.static/images/profile-picture.jpg" alt="profile picture" width="64">
    <figcaption>Some more placeholder text.</figcaption>
</figure>

<figure class="align-center">
    <img src="../.static/images/profile-picture.jpg" alt="profile picture" width="64">
    <figcaption>Some more placeholder text.</figcaption>
</figure>

<figure class="align-right">
    <img src="../.static/images/profile-picture.jpg" alt="profile picture" width="64">
    <figcaption>Some more placeholder text.</figcaption>
</figure>

## directives

### image-grid

Testing `.. image-grid::`

.. image-grid::

    ../.static/images/cover-social.jpg
    ../.static/images/profile-picture.jpg

    ../.static/images/profile-picture.jpg some caption that will be displayed under
    ../.static/images/cover-social.jpg the caption can span
        multiple lines if it's too long.
    ../.static/images/profile-picture.jpg

link-images enable

.. image-grid::
    :link-images: true

    ../.static/images/cover-social.jpg
    ../.static/images/profile-picture.jpg

    ../.static/images/profile-picture.jpg some caption that will be displayed under
    ../.static/images/cover-social.jpg the caption can span
        multiple lines if it's too long.
    ../.static/images/profile-picture.jpg

### image-gallery

Testing `.. image-gallery::`

.. image-gallery::
    :left: image1
    :right: label1, image2, label2
    :left-width: 35
    :right-width: 65

    .. image-frame:: image1 label1 ../.static/images/profile-picture.jpg
        :metadata:
            date: 2024-11 early morning
            location: France - Lyon - Parc de la Tete d’Or
            film: 35mm Kodak Gold 200
            lens: Minolta MD 35mm

        some of the text descrption of the image
        that can span multiple lines

    .. image-frame:: image2 label2 ../.static/images/cover-social.jpg
        :metadata:
             date: 2024-11 early morning
             location: France - Lyon - Parc de la Tete d’Or
             film: 35mm Kodak Gold 200
             lens: Minolta MD 35mm
 
        some of the text descrption of the image
        that can span multiple lines


### url-preview

The url-preview directive:

.. url-preview:: https://saulala.discourse.group/
    :title: Saulala | Photography application
    :image: https://www.saulala.com/background.jpg

    Develop your RAW photos with Saulala

.. url-preview:: https://mrlixm.github.io/
    :title: Hey that's me !
    :image: ../.static/images/cover-social.jpg

.. url-preview:: https://mrlixm.github.io/
    :title: Test without an image


.. url-preview:: https://mastodon.gamedev.place/@liamcollod
    :title: Maston - Liam Collod
    :svg: ../.static/icons/mastodon.svg
    :color: var(--color-WW)
    :svg-size: 32

    We test a path to a local svg file.

### include

With `include` directive:

.. include:: snippet.py
    :code: python {linenums="1" title="snippet.py"}

As literal:

.. include:: snippet.py
    :literal:

## the end

You have reached the end of the testing page.

[TOC]

🦎🦎🦎🦎🦎🦎
