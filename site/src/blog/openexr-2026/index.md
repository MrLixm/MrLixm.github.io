# Reviewing OpenEXR in 2026

:description: Where we have a look at the core image format of the vfx industry and benchmark its compression algorithm.
:image: TODO
:date-created: 2025-12-28T18:37
:category: experimentations
:tags: vfx, image-processing
:authors: Liam Collod
:stylesheets: +openexr-2026.css

[TOC]

!!! caution "reader expectations"

    This article tries to stay accessible to a majority of computer-toucher. Some
    concepts mentioned are technically complex but are not necessary to understand
    for fully understanding this post. I expect the main audience to be vfx artists
    that are already aware of the file format, but people totally outside this field
    could also hopefully enjoy the explanations.

    You are at least familiar with the basics on how digital images are structured 
    (2D pixels layout, RGB model).


If you put your nose into the file structure of any visual effect project, you
would very quickly find some `.exr` files. Yet, I think outside of this industry field
not a lot of people are aware of its existence.
This could make sense, being an image file format, it's obvious people mastering the 
craft of (animated) pictures have developed technologies going in this direction.
But pretty much everyone of any field work with images at some point, so what's the deal ?

Its clearly not features, [OpenEXR](https://openexr.com) is full of them:

- can store an arbitrary amount of "color" channels
- can store an arbitrary amount of metadata fields
- you like pictures ? what if you could store pictures within pictures ? that's called
  "multi-part" and mip-mapping which is supported.
- you can define the area that is supposed to be viewed, different from the area of pixel that is stored  (data vs display window).
- supports for [stereoscopic](https://en.wikipedia.org/wiki/Stereoscopy) workflows
- pixel data can be stored as "tiles" or "scanlines" allowing to optimize the read/write
  depending on the context.
- it provide 10 different compression algorithms to optimize file sizes
- it's a high bitdepth format offering either 16-bit float or 32-bit float encodings

It's neither its access to it, OpenEXR is one of the oldest open-source software
of the vfx-industry (2003), currently maintained by the [ASWF](https://www.aswf.io/), and 
provides API through C++,C and Python[^1]

Well a part of the answer is in the last bullet point: it's a format to store 
high dynamic range imagery in a floating point encoding. What this mean ? Well if we are
pedantic we aren't really storing images with OpenEXR, but rather an intermediate state 
of them. Expanding on this topic is a rabbit-hole in itself that I cannot handle for now
so the really short explanation is that we are not storing image that are ready to be 
displayed yet.

So viewing a `.exr` file is actually quite confusing, you never just blast the pixel value to 
the display, there must always be some form of interpration to perform, which depends on
the initial context the pixel data was generated from.

[//]: # (TODO Example with 3 picture:)
[//]: # (  1. this is an EXR whose pixel are directly sent to the monitor)
[//]: # (  2. this an EXR whose pixel have been converted to the correct colorspace &#40;sRGB standard)
[//]: # (  3. this an EXR whose pixel have been converted as it was authored)

> But why are we even't bothering with this intermediate state ? Can't we just get the 
final image in a very high quality format ? 

There's 2 reason I can think of:

- our field relies a lot on trying to reproduce the physical world, and we need to 
  manipulate physical quantities instead of more finite "display-bound" quantities.
- any image ready to be displayed means it's optimized and bound to a specific display,
  we want to deffer this step as much as possible.

Some people likes to call OpenEXR as the "raw" format of 3D (in parallel to photography),
and as you may know a raw photographic file is no more an image than an Excel sheet is. 
It's merely an intermediate file that store the raw energy recording of the camera's sensor.

So that's why OpenEXR is so niche, and you will probably never see it supported by
a web-browser or mentioned as an alternative to jpg or png. It serves a different purpose.

Yet this format is an incredible piece of technology which packs so much feature, which
by reviewing them I hope will make you appreciate all their subtelties.

## some more background

I don't want this post to become a wikipedia-like resume so we are going to skip over
most of it, but I do recommend to have a look at the origin story which was published
in 3 parts over on the ASWF website (in short interviews form): 
[part1](https://www.aswf.io/news/aswf-deep-dive-openexr-origin-story-part-1/),
[part2](https://www.aswf.io/news/aswf-deep-dive-openexr-origin-story-part-2/),
[part3](https://www.aswf.io/news/aswf-deep-dive-openexr-origin-story-part-3/).

Another interesting part of context is that OpenEXR is mainly used programmatically
through [OpenImageIO](https://openimageio.readthedocs.io), which is another standard
vfx library. In part because it has much more robust python bindings than OpenEXR,
but also because it provides an abstract interface for reading and writing a lot of 
other file formats. You can check the [example at the end of this post](#a-short-code-example).


## which bitdepth to choose ?

Probably the simplest choice, OpenEXR support 3 of them [^5], but we can really only
use two: 

- 16bits float (half)
- 32bits float (float)
- 32bits integer (uint32)

The integer bitdepth has been implemented to support [deep](#deep) images [^9]
and is never exposed in any application interface. So the choice is mostly between
the 2 floating points formats.

!!! hint "some bitdepth basics"

    If you are not familiar with bitdepth or "color depth" for images, it's a parameter
    which drive the "amount" of color you can store in an image. The amount being driven
    by the number of bits used to represent a value. Alongside the number of bits
    which are mostly a power of 2 (8,16,32), there is two ways of expressing the value:

    -   with _integers_ (3,4,5,...).
    -   with _floats_ (0.25,0.2536,1.23,156.3, ...). 

    For OpenEXR only floats interest us, and making a float is [a clever system](https://en.wikipedia.org/wiki/IEEE_754)
    which rely on splitting the original value in 3 components. Here is a handy 
    cheatsheet but *you don't need to understand it* at all for this post:

    <div class="diagram">
    <a href="diagram-bitdepth-encoding-dark.svg">
    .. include:: diagram-bitdepth-encoding-dark.svg
    </a>
    </div>

    You can use <https://float.exposed> to get a live breakdown for any float value.

    If you really want to properly explore the bitdepth topic I cannot recommend enough 
    [this (paid) zine by Julia Evans](https://store.wizardzines.com/products/how-integers-and-floats-work)
    or this [great post about floats by Bartosz Ciechanowski](https://ciechanow.ski/exposing-floating-point/).


The choice between float and half-float is the same as answering the question "how much
data to I need to store". And if we even have to make the choice it's because 32bit cost
us quite some space on disk, while 16bit will take less space + read and write faster.

However as much simple the question is, I find it rather hard to provide clear guidelines
and indication to when the difference of bitdepth matters. If the difference between
integers and floats is pretty clear, the nuance between 2 flavors of floats is harder
to put in context.

The most obvious limitation is the maximum value which for the half-float format caps 
to 65504.0. And if you think you have no image that can reach such range, it's 
possible to find such high values in sunny HDRIs [^6] or even depth buffer (zdepth) 
of very large scenes. Yet we can agree this is pretty rare.

But the more subtle limitation is precision, where half have less "gap" between each
possible value than float.

!!! admonition ""

    <div class="diagram">
    <a href="diagram-bitdepth-values-dark.svg">
    .. include:: diagram-bitdepth-values-dark.svg
    </a>
    </div>

    In the above diagram, we can see that half-float allow to express 15360 steps between
    the 0 and 1 range. While the 32bit float bitdepth allow ~ 1 billions steps. If we
    compare 16bits float to its integer counterpart we can see that we have 4 times less 
    possible values if our data is between the 0-1 range.


The last consideration to have for making the choice requires to know how was the data 
generated ? Because you need as much precision on disk only if the data stored in 
memory need as much.

[//]: # (TODO storing log in EXR)


## compression algorithms

OpenEXR comes with a shit-ton of compression algorithm, 10 of them, with 2 new algorithm
that got added in September 2025. Offerring choice is fantastic, but it's very easy to
lost the user with too much. Why is there even so much choice ?

File compression is a trade-off between size of the file on disk, time took to 
read and write, and loss of data. In short, you cannot get light files, short time to 
read/write and no loss of data (more on [Wikipedia - Data Compression](https://en.wikipedia.org/wiki/Data_compression)).
And balancing those 3 parameters is one reason we have so many choices.

Among those 10 contenders we can split them in 2 categories: lossless and lossy.
Where lossless means it possible to compress and uncompress with retrieving the exact
same data that were initially compressed. While lossy is the opposite and means *some*
of the original data will be lost, but it's acceptable because it does not have
an important visual impact.

<div class="diagram">
<a href="diagram-compression-dark.svg">
.. include:: diagram-compression-dark.svg
</a>
</div>

For the contenders I am just going to list their names, and let you refer to [the
OpenEXR documentation](https://openexr.com/en/latest/TechnicalIntroduction.html#data-compression) 
if you want the algorithm behaviour description:

- `rle` (lossless)
- `zips` (lossless) (can specify a compression amount)
- `zip` (lossless) (can specify a compression amount)
- `piz` (lossless)
- `htj2k256` (lossless)
- `htj2k32` (lossless)
- `pxr24` (lossy)
- `b44` (lossy)
- `b44a` (lossy)
- `dwaa` (lossy) (can specify a compression amount)
- `dwab` (lossy) (can specify a compression amount)

As for which one to choose now, we will get hints by summoning the dark art of 
statistics.

### compression benchmarks

Nerd time :emoji:(cat-nerd), let's warm up the computer and crunch the numbers.

Those benchmarks were realised in the following configuration:

- we rely on the [exrmetrics tool](https://openexr.com/en/latest/bin/exrmetrics.html) provided with the OpenEXR library version 3.4.4; compiled by myself.
- each compression is tested in an individual call to exrmetrics (even if the tool can test them all at once).
- each operation is run 3 times (`--passes 3`) and we use the median result
- the machine used runs on Windows 10 and was left inactive during the runs
- all ratios are caculated relative to the results with no compression

The whole generation and plotting workflow is wrapped in python script that you can
find at <https://github.com/MrLixm/benchmark-openexr>.


## storing multiple layers.

One of the most convenient feature of OpenEXR is allowing you to store as much pixel
data as needed. You are not limited to R,G,B and a potential Alpha channel. Thus, you
can reduce how much individual files you have to manage by packing it all in one.

The main usage for vfx is storing AOVs, which are alternative representation of your scene.
Those representations are usually provided by the 3d render-engine and allow to fine
tweak the image in 2d space without having to wait for expensive 3d calculations.
You can see AOVs like "layers" of the final combined image.

[//]: # (TODO add AOVs image example)

So now imagine you have 3 layers of pixel data you want to store, for a total of 8 channels:

1. final image (R,G,B,A), 
2. depth buffer (one grayscale channel) 
3. normals buffer (3 channels for x,y,z)

How can you achieve this with OpenEXR ?

### multi-file

You store each layer in a separate OpenEXR file, for a total of 3 files. 

```yaml
myimage_main.exr:
  channels: R,G,B,A
myimage_depth.exr:
  channels: Z
myimage_normals.exr:
  channels: X,Y,Z
```

### multi-channel

You add as much channel as you need, so let the file have 8 channels. To properly
separate the channels you named them using the same prefix for each layer
(conventions use the dot as separator [^3]).

```yaml
myimage.exr:
  # each channel name is separated by a comma
  channels: R,G,B,A,depth.Z,normals.X,normals.Y,normals.Z
```

That way when the software reads the channels, it can just group together
the channels that starts with the same prefix, thus "reconstructing" the layer. 

*(this method is sometime also called multi-layer)*

### multi-part

You split the data by logical groups using the "part" feature. A *part* in OpenEXR
is literally an image in an image, and you can have as much as you need (shallow). If we
represent our previous example with this logic:

```yaml
myimage.exr:
  part1:
   channels: R,G,B,A
  part2:
    channels: depth.Z
  part3:
    channels: normals.X,normal.Y,normal.Z
```

Each part can also have as many channels as it needs. In the above example we also kept
the prefix convention in channels names, but we could just have renamed the part
with the layer name, and kept channels names one letter long.

### multi-file, multi-channel or multi-part ?

As you can see we have a lot of flexibility. However there is actually only one solution
that really matters for our use-case. 

*Multi-file* is fine, but you have to manage as much
files as you have layers. And it's totally possible we reach the hundred of AOVs by image
on some productions ! Quite complicated to import and manage so much files in our "reading software".

*Multi-channel* has one massive drawback which is performances. When reading the file,
the software MUST read all the channels, to then be able to group them by layer using their names.
Imagine you have 100 AOVs with at least 3 channels for each ...

*Multi-part* is the actual solution. By splitting your layers in parts, you allow the 
reader to only read one part at a time when needed. 

!!! hint ""reader""

    In this context the software that reads the OpenEXR file, relying on the OpenEXR API.

!!! note

    There is a possibility the reader implementation just choose to always read all the 
    parts at once thus providing no gain. What is sure is that with a 
    multi-channel file, it has no choice
    to always read all the channel to reconstruct the layers.

Lastly, one important part of context is that multi-part was only introduced later in OpenEXR
lifetime (v2.0 in 2013 [^2]). Meaning that before v2.0, multi-channel and multi-file were
the only method possible. But nowadays, it is safe to assume that every software 
supporting OpenEXR uses an API version that is more recent than the v2.0.

Hopefully this make it clear as why multi-part is the best solutions in most cases. 
I *most-cases* because multi-file can still be preferred. Some software doesn't allow
you to write a multi-part file AND allow each part to specify a different bitdepth or
compression algorithm, or it simply does not support multi-part or even multi-channel 
at all (hello Photoshop :emoji:(cat-weeee)).

### mip-mapping

One use-case for wanting to store multiple images inside one image is [mipmapping](https://en.wikipedia.org/wiki/Mipmap).
That's really a need specific to 3D where for optimization reasons, we recursively store
images smaller than the previous one.

With OpenEXR, you could store each mipmap in an individual part, where the first part
is the orginal image in full resolution, and each subsequent part is smaller.

But it's also possible to store multiple mipmap for each individual part (only if the data 
is stored in a tiled layout [^4]) !

[//]: # (TODO make example of file with multiple levels and a "fuck ai" text)

However, as an artist it's probably something you will never have to do, being a rather
automated process handled by the render-engine. See [Maketx - Arnold User Guide](https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_user_guide_ac_textures_ac_textures_maketx_html)
for example.

## tiles and scanlines layouts

Those 2 attributes describe how the pixel data is stored in the file. They specify
how the original area is split in "chunk" of pixels before being stored:

-   `scanlines`: the area is split in rows of 1 pixel height
    -   this is the default layout for all images
-   `tiles`: the area is split in smaller areas of an arbitrary size
    -   this is the only layout compatible with [mipmapping](#mip-mapping) [^8].

<div class="diagram">
<a href="diagram-layout-dark.svg">
.. include:: diagram-layout-dark.svg
</a>
</div>

The purpose of those chunks is optimizing the reading step. Depending on the context
you might not want to read all the image pixels at once, but only some portions to 
speed up the process.

<figure>
    <video controls width="100%">
      <source src="./nuke-scanlines-demo.mp4" type="video/mp4" />
    </video>
    <figcaption>
    Here is an example with Nuke which works best with scanlines layout. For the first read
    we force it to read all the image, and Nuke take about 2s to read this 8K image from top
    to bottom. For the second read we let Nuke optimize the read, which become nearly
    instant. If we pause the viewport and zoom we can indeed see that only some scanlines
    of the source image are loaded.
    </figcaption>
</figure>

!!! tip "choice as an artist"

    The choice mostly depends on which software will read your exr. Scanline
    is a safe default. It doesn't even matter for 3d render-engine because they
    rely on the own inetrmediate texture format (eg, .tx, .tex) which already
    encode the original in the proper optimized layout.


## unusual formats

OpenEXR versatility made it a pretty good candidate for supporting new ways of
storing image-related data. So along the year of its existence it implemented
2 new formats that covered very specific needs of vfx productions. 

### cryptomatte

Imagine you have a 3d scene with hundreds of objects, everything get baked into 2d
during the process of rendering, and you now have a 2d image of your scene from a 
specific camera angle. Yet it's usually not the end of the craft-cycle for the image, 
and there is still additional artistic modification steps performed after. But obviously
those steps happens in 2D space: merging and mixing other medias, 
color-correcting elements, adding flavor and globally polishing the image to make it 
pretty until we can consider it "[final](https://www.reddit.com/r/funny/comments/33idlc/every_designer_in_the_world/)".

What if in this 2D space you need to perform specific adjustement to a very specific 
object of the scene that is rendered ? This mean you need a mask of the object, 
basically an image with pixel values of 1 where is the object, and 0 where it's not.

<figure markdown="span">
    <img src="diagram-cryptomatte-colorcorrect.png" alt="a diagram showcasing a 3d scene render being edited using a mask">
    <figcaption>Example where we change the [scene](https://download.blender.org/archive/gallery/blender-splash-screens/blender-2-81/) stand's wood color to green.</figcaption>
</figure>


[//]: # (TODO add image of mask of an object of the scene)

How do you create that mask ? And to go even further how could you make sure to have a
mask for every object in the scene ? There are methods that would involve rendering a 
second image where 3d objects are shaded with a constant uniform color that you could
extract in 2d, but this is legacy and the actual solution that have become standard in 
those past 20 years is *cryptomatte*.

.. url-preview:: https://raw.githubusercontent.com/Psyop/Cryptomatte/master/specification/IDmattes_poster.pdf
    :title: Fully automatic ID mattes with support for motion blur and transparency
    :image: https://github.com/Psyop/Cryptomatte/blob/master/docs/nukeScreenshot.jpg?raw=true

    SIGGRAPH 2015 poster

Cryptomatte is a mapping of your scene object collection to each pixel of the rendered 
image. Which allow operation such as "create a mask for every object whose name starts 
with a `Background` prefix". 

<figure>
    <video controls width="100%">
      <source src="./nuke-cryptomatte-demo.mp4" type="video/mp4" />
    </video>
    <figcaption>
    Example of creating masks using cryptomatte in Nuke.
    We can individually pick objects on screen, or type expressions to select
    multiple object at once.
    </figcaption>
</figure>

We can usually find 3 types of cryptomatte:

- "object": each scene mesh have a unique id.
- "asset": meshes are grouped using a common parent which receive a unique id (less common).
- "material": objects with the same material have the same id.

But it's basically up to the 3d render-engine to decide how to split/group objects in 
the scene, cryptomatte is just [a standard](https://github.com/Psyop/Cryptomatte/blob/master/specification/cryptomatte_specification.pdf)
that say how to encode and decode those information.

And speaking of encoding, if cryptomatte files are standard OpenEXR files that could 
be read by any OpenEXR reader, you would still need a specific plugin implementation
to meaningfully read the data (we use a special node in the previous Nuke example).
Because traditional image-processing operations relies on the number value in each 
pixel, here pixel values doesn't make sense until you map them with their corresponding 
"text".

Here's how cryptomatte are encoded in an OpenEXR file:

[//]: # (TODO add diagram)
<figure markdown="span">
    <img src="" alt="A diagram showcasing the hierarchy of data in an OpenEXR file">
    <figcaption>
    Cryptomatte works with a rank system where each rank is a different "depth" of
    transparency. Each rank need 2 channel of data, meaning we use the 4 standard RGBA
    channels to encode 2 ranks for optimization of space.
    Then we rely on the OpenEXR [multi-channel](#multi-channel) feature to store as much
    ranks as we need (default is 6)[^12].
    </figcaption>
</figure>


!!! Note "💡"

    This is why previewing the cryptomatte channels from an exr looks weird. The values
    of the pixel have very wild ranges and the different RGBA channels have no
    relation between each others.

It could really have been its own independent file format, but because we could qualify
it as an AOV (a different representation of the same scene and frame), it was 
probably more convenient to store it in the same file format as the other AOVs. Thus
also making it easier for software to implement it support, without having to add a new
external dependency to their stack [^10].

A few note ot be aware of:

- Make sure cryptomatte channels are encoded with 32bits [^11]
- Make sure cryptomatte channels are not color-managed when written/read
- It's possible to sometime find the cryptomatte saved in its own exr file.
- Cryptomatte support transparency but not refraction (glass-like materials)

[//]: # (TODO: how to debug cryptomatte)


### deep

TBD

## manipulating .exr files

Until now, we have seen a lot of theory, assumed to be applied in your 
DCC of choice. But what could actually be those DCCs ?

### reading .exr files

As of 2026, it's not that rare anymore to find a software which can read a basic exr file
(suprisingly Apple system have native support for it since the beginning [^7]). 
However finding a software that can read the full spectrum of OpenEXR configurations AND
allow you to post-process it to get back the original image intended for display is harder.

I cannot list all the image-viewers with OpenEXR support, but I have gathered a small 
list of the free ones I have strongly heard about, or at least tried a few times:

| name                                                            | support quality | description                                                                                                                             | issues                               |
|-----------------------------------------------------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| [DJV](https://grizzlypeak3d.github.io/DJV/)                     | +high (OCIO)    | a long-standing vfx artist favorite to read EXRs                                                                                        |                                      |
| [mrv2](https://github.com/ggarra13/mrv2)                        | +high (OCIO)    | a recently developed, vfx specific image-viewer                                                                                         |                                      |
| [OpenRV](https://github.com/AcademySoftwareFoundation/OpenRV)   | +high (OCIO)    | a pillar of the vfx industry; robustness in its clunkyness                                                                              | require compilation                  |
| [xSTUDIO](https://github.com/AcademySoftwareFoundation/xstudio) | +high (OCIO)    | a recently and studio developed vfx-focused image viewer                                                                                | require compilation                  |
| [CineSync](https://www.cinesync.online/)                        | -high (OCIO)    | a commercial and professional media viewer with a free plan                                                                             | closed-source; no multi-part support |
| [hdrview](https://github.com/wkjarosz/hdrview)                  | high            | a research-oriented image viewer with high-dynamic range support; even have [web-browser support](https://wkjarosz.github.io/hdrview/). |                                      |
| [tev](https://github.com/Tom94/tev)                             | high            | an image viewer with high-dynamic range support                                                                                         |                                      |
| [Oculante](https://github.com/woelper/oculante)                 | basic (RGBA)    | a small cross-platform image-viewer                                                                                                     |                                      |
| [PureRef](https://www.pureref.com/)                             | basic (RGBA)    | a image whiteboard popular with artists                                                                                                 |                                      |

And special mention to [Nuke](https://www.foundry.com/products/nuke-family), which is a
whole paid compositing software, but it has a free non-commercial version and provides 
a very good OpenEXR support.

### programmatic conversion with OIIO

If you ever had an .exr file, but wish you had another file format. Or the opposite !

We are going to use the [OpenImageIO](https://openimageio.readthedocs.io) library which
have first-class support for OpenEXR, and nowadays is pretty straightforward to install.

The first option will be to use their command line tool `oiiotool`. The tool is provided
with the python wheels so if you are not really into c++ library compilation, we can 
rely on the python ecosystem to get it. On my side I'll be using [uv](https://docs.astral.sh/uv/)
to retrieve it without having to even bother installing python:

```bash
uv pip install OpenImageIO --target /any/directory
```

And then the `oiiotool` executable is in `/any/directory/OpenImageIO/bin`. 

`oiiotool` already have an [extensive documentation](https://openimageio.readthedocs.io/en/v3.1.8.0/oiiotool.html)
but let's check a few example.

#### convert from exr

The most basic oiiotool command to convert from one format to another:

```bash
# oiiotool {input path} -o {output path}
oiiotool "image.exr" -o "image.jpg"
```

!!! hint "compression"

    You can control the jpeg compression by setting attributes before writing:

    ```bash
    # have a high-quality jpeg with not a lot of compression:
    oiiotool "image.exr" --compression "jpeg:90" --attrib "jpeg:subsampling" "4:4:4" -o "image.jpg"
    ```


However, this command doesn't perform any color-management and our not-display-ready
image will be directly dumped into a format that is assumed to be display-ready. 
Fortunately we can fix it, but as always this require us to know what kind of data
we put in the exr and how it's supposed to be displayed.

In my case it's a linear-sRGB exr and if I want a display-ready sRGB image I will just
need to apply the transfer function:

```bash
# oiiotool {input path} --colorconvert {src colorspace} {dst colorspace} -o {output path}
oiiotool "image.exr" --colorconvert lin_srgb srgb_display -o "image.jpg"

# in the above we are using oiiotool default OCIO config, you can check the available
# colorspace with
oiiotool --colorconfiginfo
```

Have a look at the [oiiotool documentation](https://openimageio.readthedocs.io/en/v3.1.8.0/oiiotool.html#oiiotool-commands-for-color-management)
to check the other options for color-management.

Next use-case, what if we wanted a particular layer of our exr to be saved to the jpg ?
By default, only the RGB channels are saved (jpg have no alpha).

If our exr is multi-part, you need to know the name/index of the part to keep:

```bash
# get the number of subimages
# you can add -v to have the subimage names
oiiotool --info -a "image.exr"

# take subimage 2 and write it to the jpg
oiiotool "image.exr" --subimage 2 --colorconvert lin_srgb srgb_display -o "image.jpg"
```

If our exr is multi-channel, you need to know the name of the channels to keep:

```bash
# get the channel names
oiiotool --info -v "image.exr"

# extract specific channels to the jpg
oiiotool "image.exr" --ch "R=diffuse.red,G=diffuse.green,B=diffuse.blue" --colorconvert lin_srgb srgb_display -o "image.jpg"
# ⚠️ make sure the channel names are correct because there will be no warning if they are incorrect !
```

And if you are wondering how to get each part written as a separate file, [the oiiotool
documentation](https://openimageio.readthedocs.io/en/v3.1.8.0/oiiotool.html#split-a-multi-image-file-into-separate-files)
already have an example you can check.


#### convert to exr

And for the other way around, pretty much the same logic and problematics:

```bash
# oiiotool {input path} -o {output path}
oiiotool "image.jpg" -o "image.exr"
# if we check the default exr configuration:
oiiotool --info -v "image.exr"
# ... 3 channel, half openexr
#     channel list: R, G, B
#     compression: "zip"
#     ...
```

The above is incorrect because again there is no proper colorspace conversion. We need
to at least linearise the jpeg input before storing it in the exr.

```bash
# oiiotool {input path} --colorconvert {src colorspace} {dst colorspace} -o {output path}
oiiotool "image.jpg" --colorconvert srgb_display lin_srgb -o "image.jpg"
```

And how we can fine-tune our exr configuration:

```bash
# we want a tiled float exr, with dwaa compression
# ! this a kind of "mix-it-all example" which is not optimized
oiiotool "image.jpg" --compression "dwaa:30" -d float --tile 16 16 --colorconvert srgb_display lin_srgb -o "image.jpg"
```

### with Blender !

TBD


## closing words

This post took much time before coming to life, and I am relieved it is now. 
It started from the initial idea that it woudl be cool to benchmark and compare various
file formats used in vfx. Idea wich I had since deep-diving the first time in OpenEXR,
back in 2020. It's only in 2024 that I started to do some first benchmarks around OpenEXR,
but relied on `oiiotool` for writing and tried to benchmark Nuke for reading.
Without a commercial license, the project just ended-up in the bin of unfinished project.
But around the same time I gave it up, OpenEXR devs released `exrmetrics` and it's only
during those 2025 Christmas holiday I finally had time to have a play with it. Crazy how 
"productive" people become if you gave them free time instead of work time ?

*[AOVs]: Arbitrary Output Variables
*[API]: Abstract Programming Interface
*[DCC]: Digital Content Creation (software)

[^1]: The provided Python API has limitations and you would rather use the Python bindings
    of other libraries like [OpenImageIO](https://openimageio.readthedocs.io/).
[^2]: <https://openexr.com/en/latest/news.html#april-9-2013-openexr-v2-0-released>
[^3]: <https://openexr.com/en/latest/TechnicalIntroduction.html#channel-names>
[^4]: <https://openexr.com/en/latest/ReadingAndWritingImageFiles.html#scan-line-based-and-tiled-openexr-files>
[^5]: <https://openexr.com/en/latest/TechnicalIntroduction.html#image-channels-and-sampling-rates>
[^6]: page 69 (5.8.3 Maximum Range) <https://blog.selfshadow.com/publications/s2016-shading-course/unity/s2016_pbs_unity_hdri_notes.pdf>
[^7]: last Florian's quote <https://www.aswf.io/news/aswf-deep-dive-openexr-origin-story-part-1/>
[^8]: https://openexr.com/en/latest/TechnicalIntroduction.html#scan-lines
[^9]: https://openexr.com/en/latest/DeepIDsSpecification.html#deep-id-basics
[^10]: this section is personal speculations
[^11]: https://openexr.com/en/latest/DeepIDsSpecification.html#cryptomatte-comparison
[^12]: page 2 (Channel contents) https://github.com/Psyop/Cryptomatte/blob/master/specification/cryptomatte_specification.pdf