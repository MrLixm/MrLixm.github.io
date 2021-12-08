Color-management in Substance Painter with OCIO
###############################################

:summary: The long-awaited OCIO feature is here, now we gotta find how it works.

:status: published
:date-created: 2021-11-24 23:33
:date: 2021-12-08 19:03
:cover: {static}/images/blog/0008/cover.jpg

:category: tutorial
:tags: substance-painter, color-science, OCIO, ACES
:author: Liam Collod

.. role:: text-danger
    :class: m-text m-danger

.. role:: text-green
    :class: m-text m-primary


It's there ! After so much time, Substance-Painter finally saw itself getting
a shiny new color-management system with OCIO support. We're going to dive
deeper inside and see how it works.

The article is divided into two parts.
You got first a theoretical part that will try to explain how
color-management works. This can help you debug issues and just not tweak
settings like a blind machine. This part is not mandatory though. You can
skip straight to the `Substance Setup & Workflow`_ section if desired.

.. note-info::

    OCIO was introduced in `Substance-Painter version 7.4 <https://substance3d.adobe.com/documentation/spdoc/version-7-4-223053247.html>`_

    This is the version used through this article and some features might
    have changed since.

.. block-info:: Official Documentation

    https://substance3d.adobe.com/documentation/spdoc/color-management-223053233.html

.. contents::

Color-managed Workflow
----------------------

.. note-info::

    This part is aimed at beginners, but introduce a too vast topic for this
    article. I recommend reading
    `Chris Brejon article's section about colorspaces
    <https://chrisbrejon.com/cg-cinematography/chapter-1-color-management
    #rgb-colorspace-and-its-components>`_ first, to be sure you understand
    some of the technical vocabularies employed.

We can break the workflow into 4 sections : ``Input``, ``Workspace``,
``Display`` and ``Output``

.. container:: l-c-color l-mrg-l l-flex-c l-flex-center

    .. raw:: html
        :file: diagramA.svg


You transfer ``data`` between each of these section. Data that must be
potentially decoded and then encoded, depending on what the section required.
In Substance Painter this ``data`` is most of the time pixels, encoded
using the RGB color model.

All of these data-transfers allow me to introduce the most important rule:
:text-green:`you always need to know where you start to know where you are
going`.
As an example, in the above diagram, to convert the ``Input`` data to the
``Workspace`` data, we need to know how the ``Input`` data is encoded (in our
case, which colorspace).

Data types: Color and Scalar
============================

"Where you start" means first, what type of data are you manipulating ?

There are only two types : ``color`` and ``scalar``.

It is important to know which one your data belongs to because the scalar
one doesn't require your data to be color-managed and as such skip a
complex part.

Scalar
______

Scalar data has no means to be displayed directly, the data store numbers
that can be used to drive other types of data. We are only interested in the
original value of these numbers and as such this kind of data **must never
be altered by color-transformations.**

To get to more concrete examples scalar data include but is not limited to:
roughness, normals, masks, displacement, vectors, ...

.. note-warning::

    This is not because the data, when displayed, is not grayscale, that it
    is color data. For example normal maps, even if colored, ARE scalar data.

Color
_____

Everything that is not scalar. Values stored are intended to be displayed
directly. These values are always encoded in some colorspace and require to be
decoded properly.

This include but is not limited to : diffuse/albedo/base-color, subsurface
color, specular color, refraction color, every image displayed on the web, ...

In Substance
____________

In Substance you will find this separation depending on the channel you
are working on. `The full list of color-managed channels is available here.
<https://substance3d.adobe.com/documentation/spdoc/color-management
-223053233.html#section5>`_

As Substance is aware if the channel needs to be color-managed, some operations
will be adjusted/skipped. An application of this is the ``view transform``
that will be disabled when viewing a scalar channel.

This notion will be also applied by yourself when needed to specify the
colorspace encoding of a resource (images, alphas, materials, ...).
If you import a roughness texture, as it is scalar data you will have to
specify the "colorspace" as "raw", so no special decoding is applied.

Workflow Sections
=================

.. container:: l-c-color l-mrg-l l-flex-c l-flex-center

    .. raw:: html
        :file: diagramA.svg

Input
_____

Data that need to be processed, can be anything but in our case it is
pixel data, like an image texture, a brushstroke, a procedural noise, ...

If it is scalar, we don't need to decode it. We must specify that we don't
want color-transformations by specifying for example the colorspace="raw".

If it is color this means that **the data has been mandatorily encoded in a given
colorspace**. You can hope that this encoding is specified somewhere, like in
the name, in the metadata, ... But as color-management is a big mess still in
2021 most of the time we will assume that it's in sRGB colorspace with
a transfer-function depending on the file format used.

In sp the Input section can be found on the image slot of each layer.
See `Input Setup in Sp`_ ..

Workspace
_________

Everything you create, modify go through it. We define how it is configured
so we can always know "where to go" when transforming an Input.
In sp this is the "Working color space". In OCIO term it corresponds the
``scene_linear`` role (also the ``reference`` one).

Even though sp doesn't support OCIO role, it read the
``scene_linear`` one to use it as the Working Colorspace.

Display
_______

Once the data has been processed through the Workspace you might want to
preview it. To do so, everybody will be using some kind of hardware display,
usually a computer monitor. This might sound dumb but it is a critical step.
So here we need to convert the Workspace data to Display data, and there is a
lot to do here.

We can see the Workspace as an "open-domain", where data can
be stored in some fancy colorspaces, reach some very high values, ... (it
can also be closed with data being already closer to the Display domain).
We can then see the Display as a "closed-domain", it except a kind of
particularly encoded signal and has limits clearly defined. Knowing the
source (Workspace) we can define the transformations required to convert it
to the target (Display). This involved at his core, colorspace primaries
conversion (if Workspace colorspace is different from the Display ones),
transfer-function encoding/re-encoding (to convert a linear Workspace to
a Display requiring the sRGB transfer-function), and at a more advanced stage,
a dynamic-range conversion (still if required). This last step is usually
called "tonemapping" where we try to make the open-domain that is the Workspace
fit into the Display closed-domain.

Damn that's a complicated one, but anyway, what you have to keep in mind is
we are encoding data for a delimited domain defined by the display you are
using.

In sp the Display section is handled by the ``view-transform`` dropdown, that
you can find at the top-right of your viewport.
See `Display Setup in Sp`_ .

Output
______

But isn't the Display the Output ? Yes, it can be, if you are at the end of the
chain. But here in sp, the end of the chain is our exported texture files. The
Display only allow us to have a preview of how they could look.

So here, we will encode the Workspace data, has it is required for the next
pipeline step. Encoding will depend on what you need in the next step and what
container (image format) you chose.

In sp the Output section happens during the textures export process.
See `Output Setup in Sp`_ .

Example
_______

To illustrate the theory here is a diagram representing a section of a
potential VFX-pipeline. I hope this will not confuse you more than this topic
already is.

.. figure:: {static}/images/blog/0008/diagramB.jpg
    :target: {static}/images/blog/0008/diagramB.jpg
    :alt: Color-managed pipeline example diagram

    Example of a color-managed pipeline with various colorspace configuration
    used for each section.

-
    I voluntary chose different colorspace across departments and sections to
    accentuate potential transformations.

-
    It has been chose to work with ACES for the color-management.

-
    Let's assume all the users working on this pipeline have access to the
    same display which is a DCI-P3 calibrated monitor.

.. block-danger:: Substance Painter

    If we look at the Substance Painter department, we can see that our workspace
    is ``linear - sRGB``. The artist decided to not bother working with ``ACEScg``
    colorspace but instead is using ``sRGB`` primaries.
    This means that for the Display, the chain of color-transformation is the
    following :

    ::

        linear - sRGB > linear - ACES 2065-1 + ACES RRT > 2.6 gamma - DCI-P3


    .. container:: m-row

        .. container:: m-container-inflate m-col-l-4 m-left-l

            .. figure:: {static}/images/blog/0008/sp-odt-p3.png
                :target: {static}/images/blog/0008/sp-odt-p3.png
                :alt: sp view-transform set to ACES - P3-D60

                Located at the top-right of the viewport

        .. container:: m-col-l-8

            And all of these transformation are magically handled by the OCIO
            config, the artist only specify what display is he using by
            modifying the view-transform colorspace.

    We finally export the textures in the same Workspace colorspace.

.. block-primary:: Maya

    | Now we are in Maya. We need to apply the textures on the asset and the
     end goal is to create a render out of it.
     The Workspace is now ``ACEScg`` .
     This mean we need to convert our texture which are in sRGB to this
     colorspace. The Display is the same, only the source colorspace
     change, which is now ACEScg.
    | Let's skip quickly to the last department.

.. block-warning:: Nuke

    Nuke keep the same Workspace as Maya, as our Input render is already in ACEScg
    we don't need conversion. As this is the end of the pipeline we have a few
    more possibilities here for the Output. Here we want to also be able to
    see the composited render on an sRGB Display. As such this mean the
    Output needs to be encoded for an sRGB Display, we cannot use the Output
    encoded for a DCI-P3 Display.

----

You made it yay ! Color-science is a complex topic, so don't worry if you
don't get everything the first time. You will find additional resources to
continue your exploration at the end of this article.

Now, let's put into practice the theory ...


Substance Setup & Workflow
--------------------------

.. image:: {static}/images/blog/0008/sp-project-legacy.png
    :target: {static}/images/blog/0008/sp-project-legacy.png
    :alt: New project window with color-management tab

Color-management is not application-dependent but project-dependant.
As such, you will not find any options in the applications settings but in
project ones.

New Project
===========

The first occurrence of these new options can be found on the ``New project``
window. You will find a ``Color Management`` sub-menu at the bottom.

.. image:: {static}/images/blog/0008/sp-project-cm-options.png
    :target: {static}/images/blog/0008/sp-project-cm-options.png
    :alt: New project window with color-management tab

.. note-info::

    You can change all the color-management settings at any moment in
    the project settings. Keep in mind that big changes could break your
    project though.

You will be offered between two modes ``Legacy`` and ``OpenColorIO``.
``Legacy`` corresponds to the pre-release way sp was working with. We will
skip this mode as it is not useful anymore.

.. note-info::

    Even if you don't need to use any specific OCIO config, substance offer a
    default one for the sRGB workflow which made **the OCIO mode recommended
    to use.**

OCIO config
===========

.. image:: {static}/images/blog/0008/sp-project-OCIO-01.png
    :target: {static}/images/blog/0008/sp-project-OCIO-01.png
    :alt: New project window with OCIO options

But wait, wait ... what is OCIO ? Why should I use it ?

`OCIO <https://opencolorio.readthedocs.io>`_
is a color-management solution developed originally by Sony Picture Imageworks
aiming at enforcing color-management consistency between DCCs.
I recommend `having a read at the documentation <https://opencolorio
.readthedocs.io/en/latest/concepts/overview/overview.html>`_ .

OCIO itself only define standards of utilisation and give you the tools to work
but the core of the system is the **OCIO config** (a ``.ocio`` file).
This is where all the color-transforms and options are defined.
For example, ACES is a color-management system on his own but ship a version
through OCIO.

The main advantage is that OCIO is supported by most software (even if the
implementation wildly differs between each 😬 ) so you could get the same look
through all of your DCCs (in theory).

.. transition:: ~

For our convenience sp already ships with 3 OCIO configs :

- Substance
- ACES 1.0.3
- ACES 1.2

You can find them in the sp installation folder like this one :

::

    C:\Program Files\Allegorithmic\Adobe Substance 3D Painter\resources\ocio

Honestly, I don't know why did they include two ACES versions, only the last
one was needed, but it is awesome to have a default "Substance" config.

| Lot of flexibility here. First option is to use the shipped configs.
 In my opinion only the ``Substance`` config is interesting here.
| The 2 ACES ones are the "default" dev configs with the hundred of
 colorspaces you will never need. It is better to use a lightweight ACES
 config like `the one from CAVE academy <https://caveacademy
 .com/product/cave-cg-animation-aces-ocio-config/>`_. (see `ACES Workflow`_
 section)

The ``Substance`` config will be a good fit if you are using the traditional
sRGB linear workflow and do not wish to use an OCIO config in every DCC.
You will still have enough control to have a proper color-managed workflow.

Let's now see how you could load a custom OCIO config.

Custom config
_____________

.. image:: {static}/images/blog/0008/sp-project-ocio-custom.png
    :target: {static}/images/blog/0008/sp-project-ocio-custom.png
    :alt: New project window with OCIO option set with a custom config.

The first option is to use the ``Custom`` option and manually look for
the path to the ``config.ocio`` file on your disk.


.. block-warning:: Only a reference to the config path is saved in the project.

    When submitting a OCIO config through the ``Custom`` option, **the
    config is always loaded live from the disk**.
    This means if you share a substance project with
    someone that doesn't have the OCIO config at the exact same path, you will
    see this message pop up :

    .. image:: {static}/images/blog/0008/sp-project-ocio-custom-error.png
        :target: {static}/images/blog/0008/sp-project-ocio-custom-error.png
        :alt: Error window when the custom config can't be found.

See the bottom section `Substance parameters for OCIO configs`_ to continue
the setup.

Environment variable
____________________

The above might be enough for individual artists but being in a pipeline
environment requires other ways to set OCIO automatically.

.. note-info::

    If the OCIO environment variable is present and has a valid configuration
    file it will take over to override and disable the UI settings.

On Windows you have 2 ways to set environment variables :

Global Settings
"""""""""""""""

.. image:: {static}/images/blog/0008/ocio-env-global.png
    :target: {static}/images/blog/0008/ocio-env-global.png
    :alt: Windows creating the OCIO environment variable.

You create a new variable named OCIO with the path to the config.
This variable will be used by ALL software that can read it. (unless
overridden).

This is not a recommended solution as you pollute your environment variable
+ if you decide to switch the config for another one all your previous project
will be broken.

Set locally at startup
""""""""""""""""""""""

You defined the environment variable in a start-up script.
This is the cleanest way to do it but means you can't use the Windows shortcut
to start your software :

We use a ``.bat`` to configure and launch the software. Here is a basic ``.bat``
that will set the OCIO variable and then launch sp.

.. code:: shell

    set "OCIO=C:\aces_1.1\config.ocio"

    start "" "C:\Program Files\Allegorithmic\Adobe Substance 3D Painter\Adobe
    Substance 3D Painter.exe"

.. note-default::

    To create a ``.bat`` just create a new ``.txt`` file, paste the above code,
    modify it with the path to your config, save it, and then just replace
    the ``.txt`` with ``.bat`` in the file's name.

| This means that to launch Substance you will have to always use this .bat.
 No "double-clicking" on file to open them either.
| You can have a look on internet at `how to pin a .bat to the taskbar
 <https://superuser.com/questions/656611/how-to-pin-a-batch-file-to-the
 -taskbar-quicklaunch/656649>`_ .

But this guarantees a very robust software configuration per project.

Substance parameters for OCIO configs
_____________________________________

.. figure:: {static}/images/blog/0008/sp-project-ocio-options.png
    :target: {static}/images/blog/0008/sp-project-ocio-options.png
    :alt: Options for OCIO mode in sp..

    OCIO with Substance config properly configured.


It corresponds to all the sections below the color-management mode. It allows
to configure how inputs react with the OCIO config, i.e which colorspace is
being assigned by default.

Usually, in other software, this section is configured using the `OCIO roles
<https://opencolorio.readthedocs.io/en/latest/guides/authoring/overview
.html#roles>`_ defined in the OCIO configuration.
:text-danger:`But currently sp doesn't support OCIO roles.` Instead, it is
using the ``working colorspace`` as a default colorspace everywhere, which mean
:text-danger:`you have to manually setup this section` to get a correct result
with the auto settings.

If you look at the above image, this is how it is supposed to look when picking
the Substance config. By default 8 and 16 bit images are supposed to be
considered as ``sRGB``, **same goes for substance materials**.

Make sure these options are properly configured with the intended colorspaces
for each format if you want all the ``auto`` options to work properly. Most of 
them (except Export ones) can be changed in context.

Visit the `ACES Workflow`_ section to find how this should be considered if you
are using the ACES config.

New Project : Conclusion
========================

Alright, to recap' everything for a new project you need :

1. Change the color-management mode to OCIO
2. Choose the OCIO config (already chosen if env variable set)
3. Edit the OCIO options to have the correct default colorspaces working.

And of course, setting the other parameters related to your texturing.

Now you are good to start the texturing workflow. The workflow will be
divided into the same sections explained in the theoretical part of this
article (see `Color-managed Workflow`_).

Workspace Setup in Sp
=====================

The Workspace, in software is actually an "abstract" section. It just
represents the colorspace used as a reference, target or source for every color
transformation. It is defined in the OCIO config and cannot be changed outside
of it.

.. note-info::

    In the OCIO config it corresponds to the ``scene_linear`` role.

.. figure:: {static}/images/blog/0008/sp-project-ocio-workspace.png
    :target: {static}/images/blog/0008/sp-project-ocio-workspace.png
    :alt: The Working Colorspace displayed in the Color-management tab.

    Visible in the Project's Color-management section (Using the ACES 1.2 OCIO
    config here)

It is just good to know what is the colorspace being used here.

Display Setup in Sp
===================

.. image:: {static}/images/blog/0008/sp-odt-default.png
    :target: {static}/images/blog/0008/sp-odt-default.png
    :alt: View-transform screenshot.

A good first step before working is to make sure the Display part is
properly configured so you don't start texturing while viewing the wrong
colors. This Display part can be configured using what we usually called a
`view-transform` menu. In sp, you can find it at the top-right of your
viewport.

What you have to remember is that :text-green:`you need to choose the option
that corresponds to your display.` If your display is calibrated to the
Display P3 colorspace (Apple displays), choose the Display P3 option.

But what if I don't know what my display is calibrated to ?

    A safe choice would be to assume you are using an sRGB-like display.

.. _the rec709 transfer-function issue:

I see some people using Rec.709 instead of sRGB, why ?

    sRGB and Rec.709 share the same primaries, so you can use both without
    seeing color-shift due to different primaries. What does change is the
    transfer function being used. But fasten your seat-belt, here comes the
    mess : Rec.709 only defined an :abbr:`OETF <opto-electrical transfer function>`
    which is intended for camera signal encoding, not data display encoding !
    For display encoding with the Rec.709 colorspace, one should use the
    `BT.1886 <https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1886-0-201103-I!!PDF-E.pdf>`_
    standard which can be resumed as a simple 2.4
    :abbr:`power-function <= gamma>`.

    So how to know which one of these two is being used ? Simple, if when
    compared to sRGB, the image looks darker, it's the OETF, if it's looking
    less contrasty, it's BT.1886.

    If you do the test, the Substance config use the OETF (which should not
    be used), while the ACES config uses BT.1886.

You didn't answer my question !? I'm just more confused now !

    As written previously, you need to choose the option that corresponds to
    your display, so if your display is not calibrated to Rec.709+BT.1886
    don't use it. But some people like the look of it, being less contrasty,
    that's why it's being chosen. But the display should not be a creative
    choice. If you like a less contrasty look, you should apply it in the Look
    (see under).

    Just to add more confusion, the BT.1886 difference with sRGB can
    actually be used as a viewing environment compensation. So it can actually
    justify why using Rec709+BT.1886 instead of sRGB.

Anyways, I'm going too far from the subject, and someone already
wrote about this topic, I let you read this mind-blowing article from
Chris Brejon `OCIO, Display Transforms and Misconceptions <https://chrisbrejon
.com/articles/ocio-display-transforms-and-misconceptions/>`_.

Displaying Color and Scalar data
________________________________

Sp will handle it for you automatically, depending on the channel you
are previewing.

`The full list of color-managed channels is available here.
<https://substance3d.adobe.com/documentation/spdoc/color-management
-223053233.html#section5>`_

For example, selecting the Roughness channel for preview will disable the
view-transform :

.. image:: {static}/images/blog/0008/sp-odt-off.png
    :target: {static}/images/blog/0008/sp-odt-off.png
    :alt: View-transform screenshot, when scalar data is selected.

If you are using a custom ``User`` channel, you will have to manually
specify if the channel is color-managed though. (By default they are not)


Input Setup in Sp
=================

Texturing is all about mixing already existing images, with some carefully
crafted paint stroke, and funky procedural resources. All of these, if they
are color-data, have been created and saved with a specific colorspace.
We will need to know and then specify this colorspace to sp so the OCIO
processor can know if it needs conversion to the Workspace colorspace.

Shelf Resources
_______________

In Sp this manipulation takes place, weirdly, on the images slots of each
layer. You will not find any option to specify the colorspace in the shelf.

.. image:: {static}/images/blog/0008/sp-in-bobross.png
    :target: {static}/images/blog/0008/sp-in-bobross.png
    :alt: Screenshots of the Input colorspace option for layers.

By default, it is set to ``auto``, which will use the settings specified in the
project color-management settings explained above.
(`Substance parameters for OCIO configs`_).

I recommend always modifying this option to the proper colorspace to be sure
the resource is properly color-managed.

Another option is to have the source colorspace specified in the file name.
That's in my opinion a bit messy because the colorspace has to be the exact
name used in the config. If 2 configs used a different name, your image will
only work for one. If I take for example a colorspace name used in the ACES
config this could give: ``bricks_wall_albedo_Utility - Linear - sRGB.exr``.

The color-picker
________________

.. container:: l-flex-r l-flex-start l-gap-1

    .. image:: {static}/images/blog/0008/sp-colorpicker.png
        :target: {static}/images/blog/0008/sp-colorpicker.png
        :alt: Screenshots of the color picker.

    .. container:: l-flex-shrink-2

        As used as feared by artists. It never react how the artist wants
        and looks to be made out of dark magic (at least in Mari 🙃 ).
        Did the sp implementation bring any good news ? Let's see.

        Abbreviations used:

        -
            ``tcd`` : top colorspace dropdown
        -
            ``eds`` : editable sliders, where you can manually enter your color
            components.

        First really good feature is the little info icon, giving explicit
        info on how the widget works. But the given info brings some bad
        news; if we have a look at the info message next to the ``tcd`` :

            This is the display color space used for displaying the on-screen
            image. The editable color values are specified within the project's
            working color space.

        What this means is that in the values sliders under, the value entered
        are always in the colorspace defined by the project's working
        color space. So you could change the ``tcd`` but
        this won't modify the value entered.

        **The ``tcd`` only modify how the color is displayed in the
        interface.** (you can see this displayed value under the ``eds``)

        .. note-info::

            As such it is recommended to set the ``tcd`` to the same colorspace
            being used in the view-transform.

.. _picker:

What about the actual picker ?

    Same thing, the value that is being picked is expressed in the working
    colorspace. It is not affected by the ``tcd``.

    First the color-picker pick the value at display *(the value will be
    different if you enable or disable the view-transform )*

    Then the color-picker ALWAYS apply an extra color-transformation step :
    It applies the inverse transform defined in the colorspace used in
    the ``color-picking`` OCIO role.

To make things clearer, what best than an image ?

.. figure:: {static}/images/blog/0008/diagramC.jpg
    :target: {static}/images/blog/0008/diagramC.jpg
    :alt: Color-picking process as a diagram.

    Using the Substance config

.. figure:: {static}/images/blog/0008/diagramC-ACES.jpg
    :target: {static}/images/blog/0008/diagramC-ACES.jpg
    :alt: Color-picking process as a diagram.

    Using the ACES 1.2 config (the end-result could be even more broken if
    we were using another view_transform)

.. note-warning::

    You need to also take into consideration the color-picker precision issues.
    Applying an invert color-transformations can lead in some cases to
    imprecisions but it seems the color-picker already has some precision
    issues by itself.

This means the colorpicker is unfortunately again, broken. But there is a
solution to compensate for this issue.

.. block-primary:: In the case you want to reverse the color-picker
    color-transformation :

    -
        Set the ``tcd`` to the same colorspace used by the ``color_picking``
        role. (by default it should be the first view-transform but check
        the config)

    -
        Pick your value.

    -
        Look at the values in the ``Display colorspace`` widget, and copy
        them in the ``eds``.

    *(most common case would be to pick data in a scalar channel)*

Environment
___________

There is no direct option to modify the environment image colorspace.

Your options are :

-
    Modify the default ``Linear`` colorspace in the project settings. The
    environments maps will use it.

-
    Include the source colorspace in the name of the HDRI. It has to be the
    **exact same name** as defined in the config. Example :
    ``myhdri_ACES - ACEScg.exr``. (you can find an example in `ACES -
    Environment`_)

The pre-integrated HDRIs are encoded with a ``linear - sRGB`` colorspace.


Output Setup in Sp
===================

The Export Textures window didn't got much new. We doesn't have any options
to apply a color-transformation at export time in the Window. The only options
are the one available into the project settings.

.. image:: {static}/images/blog/0008/sp-project-export.png
    :target: {static}/images/blog/0008/sp-project-export.png
    :alt: Sp project settings export options.

Basically, integer format should be sRGB display encoded. Floating point format
should use the same working colorspace.

What's new though is the ``$colorspace`` token in the Output Templates tab.

.. image:: {static}/images/blog/0008/sp-export-template.png
    :target: {static}/images/blog/0008/sp-export-template.png
    :alt: Sp Export window, Output template tab.

Which is simply replaced by the colorspace defined in the project settings.
(You can have a preview of the file name in the ``LIST OF EXPORT`` tab).

I'm personaly not fan of this option as this might introduce special characters
in the file's name, depending on how the colorspace is named. It is, I think,
a better option to have the texture name without the colorspace, but exported
in a directory with the colorspace name.

For scalar channels, sp will not apply any color-transformation
and consider them using the colorspace ``raw`` (no matter the config).
Interstingly, this colorspace ``raw`` doesn't get written into the
``$colorspace`` token as it should.

ACES Workflow
-------------

I'm not going to get into the what and the why, only the how. Let's keep the
rest for a next (potential) article ?

ACES - Config setup
===================

You could use the one shipped with Substance but I wouldn't recommend so.
They are the ones with the hundred colorspaces that will just slow you down
when you need to choose one.

Instead, it would be smarter to use a config with only what you need like
`the one from CAVE academy`_.

Then you will need to configure the default colorspaces. Using the Cave config
(which have the same nomenclature as the official ACES ones) here is what I
recommend :

.. image:: {static}/images/blog/0008/sp-aces-project.png
    :target: {static}/images/blog/0008/sp-aces-project.png
    :alt: Substance project window with ACES setuped properly.

Import settings are the usual stuff, most of the 8bit texture, if not all
are sRGB display encoded files so ``Utility - sRGB - Texture`` correspond.
Floating point images like EXRs should always be linear so the alternative
version ``Utility - Linear - sRGB`` is the right choice. Remember these options
are just applied by default (with the ``auto`` colorspace) but can be
changed anytime.

I choose ``Utility - sRGB - Texture`` for ``Substance materials`` because
it seems the output is always sRGB display encoded as the screenshot under
show. (colorspace options can be modified on the material anyway).

.. figure:: {static}/images/blog/0008/sp-mat-colorspace.png
    :target: {static}/images/blog/0008/sp-mat-colorspace.png
    :alt: Substance viewport screenshot with different default for materials.

    Model by `Emmanuel-Xuân Dubois <https://www.artstation.com/ashimara>`_

Now for the output my choice is not the only option. To me, you shouldn't
export ACEScg 8bit files, that why I re-encode them back to sRGB by using
``Utility - sRGB - Texture``. The right option is to export EXRs (floating
point images) in the same working colorspace: ACEScg. And don't worry for
scalar channel they will be handled automatically at export. These options
are the only ones that can't be modified per-case though; this is the only
place you can change them.

ACES - What to do when working
==============================

I'm only going to give detailed explanations when something is specific to
ACES. Meanwhile the explanations given in `Substance Setup & Workflow`_ still
apply so make sure you properly understood this section.

ACES - Display
______________

Not much new, use the view-transform that correspond to the display you are
using. (In my case ``ACES - sRGB``, that behind the scene, uses ``Output -
sRGB``)


ACES - Inputs
_____________

For every external resource you import, you need to assign the correct
input colorspace if the automatic one doesn't correspond. The usual rules
for the ACES workflow apply.

.. image:: {static}/images/blog/0008/diagram-aces-idt.jpg
    :target: {static}/images/blog/0008/diagram-aces-idt.jpg
    :alt: ACES IDT Cheatsheet.


ACES - Environment
""""""""""""""""""

There is unfortunately no direct options to change environment's colorspace.
But they follow default colorspace rules. And as they are floating point image
they use the pre-defined ``Utility - Linear - sRGB`` colorspace. As such, as
long as they are sRGB - linear encoded, they will be properly displayed.

But what if I want to import an already converted ACEScg HDRI ?

    There is a way to have it working. You can specify the colorspace in the
    file name. The colorspace has to be **the exact same name** as the one
    defined in the config. An example would be: ``myhdri_ACES - ACEScg.exr``.

    Left one is sRGB encoded, middle and right ACEScg encoded. Right one
    doesn't get properly converted and looks shifted.

    .. figure:: {static}/images/blog/0008/sp-aces-hdri-comparison.png
        :target: {static}/images/blog/0008/sp-aces-hdri-comparison.png
        :alt: Sp viewport screenshot with hdri comparison.

        Model and texturing by `Emmanuel-Xuân Dubois`_


ACES - Colorpicker
__________________

The colorpicker by default and in my case use the same colorspace as the
first view_transform. This means the color I see in the picker is the same in
the viewport. As mentioned in `The color-picker`_ section the sliders values
are expressed in the working-colorspace, in our case ACEScg.

Consider the following example :

.. figure:: {static}/images/blog/0008/sp-aces-colorpicker.png
    :target: {static}/images/blog/0008/sp-aces-colorpicker.png
    :alt: Substance colorpicker with ACES workflow.

    Model by `Emmanuel-Xuân Dubois`_

I have an ACEScg value of (1,0,0) which is damn too saturated
and no object except laser are that saturated.

.. note-warning::

    This mean you have to be careful
    when picking values, and always keep a look at the scene-refered ACEScg
    values.

What if I want to apply a color we gave me as hexadecimal ?

    Consider my brand's green picked from https://coolors.co .

    .. figure:: {static}/images/blog/0008/sp-aces-colorpicker-hex.png
        :target: {static}/images/blog/0008/sp-aces-colorpicker-hex.png
        :alt: Substance colorpicker with ACES workflow.

        Model by `Emmanuel-Xuân Dubois`_

    Well ... the less brain-damaging solution would be to just eyeball the
    color.

    The first issue here is that the color is probably sRGB display
    encoded and need to first be linearized, then converted to ACEScg.

    .. image:: {static}/images/blog/0008/sp-aces-colorpicker-conversion.png
        :target: {static}/images/blog/0008/sp-aces-colorpicker-conversion.png
        :alt: Nuke screenshot to convert sRGB hex value to ACEScg

    The above should give you an idea of how to achieve this with Nuke.
    The ACEScg values can be found at the bottom right of the image.
    But as you can see the viewer color (with the ACES ODT applied) is still
    different from the preview on coolors website !

    Keep this in mind: :text-green:`you will never be able to match the look
    of the sRGB workflow with the ACES workflow.` (unless cheating).

    I'm not going to dive into further explanations as there is `enough threads
    on this subject <https://community.acescentral.com/t/preserving-logos-and-graphics-in-aces/2861>`_
    on ACES central and Chris `is already explaining it here
    <https://chrisbrejon.com/cg-cinematography/chapter-1-5-academy-color
    -encoding-system-aces/#inverted-odt-workflow>`_.

ACES - Output
_____________

Do yourself a favour here and only care about EXR. `You don't need anything
else <https://www.elsksa.me/scientia/cgi-offline-rendering/file-format
-debunk>`_ and this is the file format recommended by the Academy for ACES
data encoding.

If you choose EXR, you have nothing to care about. Color channel will be
exported in ``ACEScg`` while scalar channel will bypass any
color-transform encoding. Simple as that.

.. figure:::: {static}/images/blog/0008/sp-aces-export.png
    :target: {static}/images/blog/0008/sp-aces-export.png
    :alt: Substance Export window screenshot.

    You can check the LIST OF EXPORTS tab to see how it's going to be exported.

Reminder that you can choose to remove the ``$colorspace`` token in your
export template map name to avoid unwanted special characters in your file
name. (and instead export the textures in a folder named ACEScg)


OCIO Implementation Issues
--------------------------

.. note-default::

    The goal here is not to denigrate the dev team's works but rather to offer
    explanations and solutions to what could be better.

Display Issues
==============

These explanations were made possible thanks to the Chris Brejon's article
`OCIO, Display Transforms and Misconceptions`_.

Display components mismatch
___________________________

OCIO divide the Display section into 3 components :

-
    ``Display`` : the physical hardware you are using (monitor, TV, phone, ...).

-
    ``View`` : a way to encode the data for a specific viewing purpose.

-
    ``Look`` : a creative layer of modification on the data. ex: a grade.

Why do I explain you this ? Because these components are often mismatched
or forgotten. Unfortunately, Substance makes no exception here.

.. image:: {static}/images/blog/0008/sp-odt-default.png
    :target: {static}/images/blog/0008/sp-odt-default.png
    :alt: View-transform screenshot.

If you look at the view-transform screenshot above, you can see that each
option has the ``Default`` prefix.
If we have a look at the ``config.ocio`` file from the Substance config,
we can see why :

.. figure:: {static}/images/blog/0008/config-substance-displays.png
    :target: {static}/images/blog/0008/config-substance-displays.png
    :alt: Screenshot of the displays part of the Substance Ocio config.

What should be a ``display`` or a separate ``view`` is actually all merged
into a single ``view`` component !

.. _substance-config-displays-fixed:

Here is how it should look :

.. code:: yaml

    displays:
      sRGB:
        - !<View> {name: Display, colorspace: sRGB}
        - !<View> {name: ACES, colorspace: ACES sRGB}
        - !<View> {name: False Color, colorspace: False Color}
        - !<View> {name: Raw, colorspace: Raw}
      Display P3:
        - !<View> {name: Display, colorspace: Display P3}
        - !<View> {name: False Color, colorspace: False Color}
        - !<View> {name: Raw, colorspace: Raw}
      Rec709 :
        - !<View> {name: Display, colorspace: Rec709}
        - !<View> {name: False Color, colorspace: False Color}
        - !<View> {name: Raw, colorspace: Raw}
      Rec2020 :
        - !<View> {name: Display, colorspace: Rec2020}
        - !<View> {name: False Color, colorspace: False Color}
        - !<View> {name: Raw, colorspace: Raw}

Here is the result of the above in Substance Painter :

.. image:: {static}/images/blog/0008/config-substance-fixed-sp.png
    :target: {static}/images/blog/0008/config-substance-fixed-sp.png
    :alt: Screenshot of the displays part of the Substance Ocio config.

Using OCIO v2 there are other ways to improve how the config is built.
Heads up to `Improving the Substance OCIO config`_ to see how.

But even with this fix, it's not very friendly to have a long list of merged
(display + view) while you would only need one Display most of the time. **The
best solution here would be to have 2 dropdowns** :
One to choose the Display, and one to choose the corresponding available View.
We should even get a third one for looks as we are going to see in the next
section :

Partial Look support
____________________

In above explanations where I mention OCIO Display is build with
3 components, we now see that I didn't mention the last one yet: Looks.

Looks is a color-tansformation performed in any colorspace aimed at
modifying the data in a creative way. This would allow for example the
artist to have a first look at how its renders could looks like after the
:abbr:`di <Digital Intermediate = grading process>` pass.

Usually, Looks are defined similar to colorspaces, as a list, but you can also
make a Look available in a display's view:

.. code:: yaml

    displays:
        sRGB:
            - !<View> {name: Display, colorspace: sRGB-Display}
            - !<View> {name: Display Grade A, colorspace: sRGB-Display, looks: gradeA}

    looks:
    - !<Look>
      name: gradeA
      process_space: rclg16
      transform: !<FileTransform> {src: look_A.cc, interpolation: linear}

In the best case, we should have a dropdown menu that would allow us to combine
the current ``view-transform`` with any Look defined. A good example of this
is Blender :

.. figure:: {static}/images/blog/0008/blender-cm.png
    :target: {static}/images/blog/0008/blender-cm.png
    :alt: Screenshot of Blender color-management menu.

    Notice how it respects the 3 components of an OCIO display.

Unfortunately, sp didn't implement this feature yet. So we can only rely
on merging the look in a display view for now.

A good way to test this is using the `Filmic <https://github
.com/sobotka/filmic-blender>`_ OCIO config by Troy Sobotka.
The filmic encoding is correctly available in a ``View`` but require an
extra step to be correctly displayed. By default it is a flat log
representation, and require choosing a Look with the desired contrast amount.

To have it working in sp, it is required to merge the Look in a new ``View``.

.. code:: yaml

    displays:
        sRGB:
            - !<View> {name: sRGB OETF, colorspace: sRGB OETF}
            ...
            - !<View> {name: Filmic Very High Contrast, colorspace: Filmic Log Encoding, look: +Very High Contrast}
            ...

.. _sp-odt-name-cropped:

Which in sp, if we kept all the contrast amount, give us a very long list of
cropped name 😬 But at least it's working.

.. image:: {static}/images/blog/0008/sp-odt-filmic.png
    :target: {static}/images/blog/0008/sp-odt-filmic.png
    :alt: Screenshot of sp view-transform with filmic view.


Improving the Substance OCIO config
===================================

The Substance OCIO config is an OCIO v1 configuration. I don't know
what is the reason they decided to not use the v2 for their config because
it could really helped having a cleaner and better config (even if the artist
wouldn't see that much of a difference).

By curiosity I tried to put my hand on OCIO v2 and create a config that could
be a substitution of the Substance config. Documentation was pretty straight
forward and I manage to build a nice config using python. You can find the
result here :

https://github.com/MrLixm/OCIO.Liam

I called it ``Versatile``. It only misses the ``false color`` view from the
Substance config. Have a look at the
`config.ocio <https://github.com/MrLixm/OCIO.Liam/blob/main/versatile/config/config.ocio>`_
file to see the new features.


Issues Recap
============

| This list aim at helping the potential Substance dev team members reading
 this, addressing the issues.
| *Keep in mind that this is my personal opinion, i'm not a color-scientist
 nor a profesional developer.*

-
    | Substance config uses the wrong Rec.709 display encoding.
    | (see `the rec709 transfer-function issue`_)

-
    Substance config miss simple P3 colorspaces while it offers a Rec2020 one
    (who would use it ??)

-
    | Substance config ``displays`` key is not properly built.
    | (see `substance-config-displays-fixed`_ )

-
    The Substance config could overall, benefits from using OCIO v2 features.

-
    | OCIO roles are not supported, as such default configuration for
     projects is wrong and can confuse artists.
    | (see `Substance parameters for OCIO configs`_)

-
    | The view-transform dropdown is too small in width. When selecting long
     ``display`` names, they got cropped.
    | (see `sp-odt-name-cropped`_)

-
    | The view-transform dropdown could be split into 2 dropdowns. One for
     Displays and one for Views.
    | (see `substance-config-displays-fixed`_ )

-
    Colorspace on resources (images, ...) should be performable from the shelf
    and not from a layer's slot. A resource doesn't have its original
    colorspace changing depending on where it's used !

-
    | There is no direct option to change the environment image colorspace.
     Having the above suggestion implemented would solve this one too.
    | (see `Environment`_ )

-
    Color-picker : modifying the top colorspace should affect the editable
    values. Where the top colorspace represents the colorspace used to enter
    values so they can be converted to the working colorspace behind the scene.

-
    With the above, add a way to see what values are being used in the
    workspace.

-
    | Color-picker: the picker should not use the ``color_picking`` role as an
     invert transform. It should be the colorspace used by the
     ``view-transform``. (and no transform should be applied when the
     view-transform is disabled)
    | (see `picker`_ section)

-
    No options to set a specific colorspace for textures at export time.

Conclusion
----------

Damn that was a long one. Congrats if you stick to the end, I hope you
now have an idea of how you could use OCIO in SubstancePainter. If not,
don't hesitate to `contact </pages/contact>`_ me to suggest how this
article could be improved. (you can also join the discord, click on the purple
button at the bottom of this page)

If you like this post and wish to support me you could buy some of my
scripts on `my Gumroad <https://app.gumroad.com/pyco>`_.

I see you in the next one that would probably be on the same topic but on
Mari. 👋

Resources
---------

.. block-default:: The Hitchhiker's Guide to Digital Colour

    https://hg2dc.com/

.. block-default:: Chris Brejon

    https://chrisbrejon.com/cg-cinematography/chapter-1-color-management

.. block-default:: ACES Central

    https://community.acescentral.com/

.. block-default:: Cinematic Color

    https://cinematiccolor.org/

.. block-default:: A Color-Science Discord server

    https://discord.gg/jk6u3eB