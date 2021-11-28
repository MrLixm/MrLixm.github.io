Color-management in Substance Painter with OCIO
###############################################

:summary: The long-awaited OCIO feature is here, let's see how it works.

:status: draft
:date-created: 2021-11-24 23:33
:date: 2021-11-24 23:33

:category: tutorial
:tags: substance-painter, color-science, OCIO, ACES
:author: Liam Collod

.. role:: text-danger
    :class: m-text m-danger

.. role:: text-green
    :class: m-text m-primary


It's there ! After so much time, Substance-Painter finally saw it-self getting
a shiny new color-management system with OCIO support. We're going to dive
deeper inside and see how it works.

The article is divided in two parts.
You got first a theoratical part that will try to explain how
color-management works. This can help you debug issues and just not tweak
settings like a blind machine. This part is not mandatory thought. You can
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

    This part is aimed at beginners, but this is a too vast topic for this
    article. I recommend to read
    `Chris Brejon article's section about colorspaces
    <https://chrisbrejon.com/cg-cinematography/chapter-1-color-management
    #rgb-colorspace-and-its-components>`_ first, to be sure you understand
    some of the technical vocabulary employed.

We can break the workflow in 4 sections : ``Input``, ``Workspace``, ``Display``
and ``Output``

.. container:: l-c-color l-mrg-l l-flex-c l-flex-center

    .. raw:: html
        :file: diagramA.svg


You transfer ``data`` between each of this section. Data that must be
potentialy decoded and then encoded, depending of what the section require.
In Substance Painter this ``data`` is most of the time pixels, encoded
using the RGB color model.

All of this data-transfers allow me to introduce the first core rule:
:text-green:`you always need to know where you start to know where you are
going`.
As an example, in the above diagram, to convert the ``Input`` data to the
``Workspace`` data, we need to know how the ``Input`` data is encoded (in our
case, which colorspace).

Data types: Color and Scalar
============================

"Where you start" means first, what type of data are you manipulating ?

There is only two types : ``color`` and ``scalar``.

It is important to know which one your data belongs to because the scalar
one doesn't require your data to be color-managed and as such skip a
complex part.

Scalar
______

Scalar data has no means to be displayed directly, the data store numbers
that can be used to drive other type of data. We are only interested by the
original value of these numbers and as such this kind of data **must never
be altered by color-transformations.**

To get to more concrete examples scalar data include but is not limited to:
roughness, normals, masks, displacement, vectors, ...

.. note-warning::

    This is not because the data , when displayed, is not grayscale , that it
    is color data. For example normal maps, even if colored, ARE scalar data.

Color
_____

Everything that is not scalar. Values stored are intented to be displayed
directly. These values are always encoded in some colorspace and require to be
decoded properly.

This include but is not limited to : diffuse/albedo/base-color, subsurface
color, specular color, refraction color, every image displayed on the web, ...

In Substance
____________

In Substance you will find this separations depending of the channel you
are working on. `The full list of color-managed channels is available here.
<https://substance3d.adobe.com/documentation/spdoc/color-management
-223053233.html#section5>`_

As Substance is aware if the channel need to be color-managed, some operations
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

Data that need to be processed, this can be anything but in our case it is
pixel data, like an image texture, a brush stroke, a procedural noise, ...

If it is scalar, we don't need to decode it. We must specify that we doesn't
want color-transformations by specifying for example the colorspace="raw".

If it is color this mean that **the data has been mandatory encoded in a given
colorspace**. You can hope that this encoding is specified somewhere, like in
the name, in the metadata, ... But as color-management is a big mess still in
2021 most of the time we will assume that it's in sRGB colorspace with
a transfer-function depending of the file format used.

In sp the Input section can be found on the image slot of each layer.
.. TODO link section

Workspace
_________

Everything you create, modify go through it. We define how it is configured
so we can always know "where to go" when transforming an Input.
In sp this is the "Working color space". In OCIO term it correspond the
``scene_linear`` role (also the ``reference`` one).

Even thought sp doesn't support OCIO role, it actually read the
``scene_linear`` one to use it as the Working Colorspace.

Display
_______

Once the data as been processed through the Workspace you might want to
preview it. To do so, everybody will be using some kind of hardware display,
usually a computer monitor. This might sounds dumb but it is a critical step.
So here we need to convert the Workspace data to Display data, and there is a
lot to do here.

We can see the Workspace as an "open-domain", where data can
be stored in some fancy colorspaces, reach some very high values, ... (it
can also be closed with data being already closer to the Display domain).
We can then see the Display as a "closed-domain", it except a kind of
particulary encoded signal and has limits clearly defined. Knowing the
source (Workspace) we can define the transformations required to convert it
to the target (Display). This involve at his core, colorspace primaries
conversion (if Workspace colorspace is different from the Display ones),
transfer-function encoding/re-encoding (to convert a linear Workspace to
a Display requiring the sRGB transfer-function), and at a more advanced stage,
a dynamic-range conversion (still if required). This last step is usually
called "tonemapping" where we try to make the open-domain that is the Workspace
fit into the Display closed-domain.

Damn that's a complicated one, but anyways, what you have to keep in mind is
we are encoding data for a delimited domain defined by the display you are
using.

In sp the Display section is handled by the ``view-transform`` dropdown, that
you can find at the top-right of your viewport.
.. TODO link section

Output
______

But isn't the Display the Output ? Yes, it can be, if you are at the end of the
chain. But here in sp, the end of the chain is our exported texture files. The
Display only allow us to a preview at how they could look.

So here, we will encode the Workspace data, has it is required for the next
pipeline step. Encoding will depend of what you need in the next step and what
container (image format) you choosed.

In sp the Output section happens during the textures export process.
.. TODO link section

Example
_______

To illustrate the theory here is a diagram representing a section of a
potential VFX-pipeline. I hope this will not confused more than this topic
already is.

.. figure:: {static}/images/blog/0008/diagramB.jpg
    :target: {static}/images/blog/0008/diagramB.jpg
    :alt: Color-managed pipeline example diagram

    Example of a color-managed pipeline with various colorspace configuration
    used for each section.

-
    I voluntary choosed different colorspace across departements and sections to
    accentuate potential transformations.

-
    It has been choosed to work with ACES for the color-management.

-
    Let's assume all the users working on this pipeline have access to the
    same display which is a DCI-P3 calibrated monitor.

.. block-danger:: Substance Painter

    If we look at the Substance Painter departement, we can see that our workspace
    is ``linear - sRGB``. The artist decided to not bother working with ``ACEScg``
    colorspace but instead is using ``sRGB`` primaries.
    This mean that for the Display, the chain of color-transformation is the
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

            And all of this transformation are magically handled by the OCIO
            config, the artist only specify what display is he using by
            modifying the view-transform colorspace.

    We finally export the textures in the same Workspace colorspace.

.. block-primary:: Maya

    | Now we are in Maya. We need to apply the textures on the asset and the
     end-goal is to create a render of it. The Workspace is now ``ACEScg`` .
     This mean we need to convert our texture which are in sRGB to this
     colorspace. The Display is the same, only the source colorspace
     change, which is now ACEScg.
    | Let's skip quickly to the last departement.

.. block-warning:: Nuke

    Nuke keep the same Workspace as Maya, as our Input render is already in ACEScg
    we don't need conversion. As this is the end of the pipeline we have few
    more possibilites here for the Output. Here we want to also be able to see the
    composited render on a sRGB Display. As such this mean the Output need to be
    encoded for an sRGB Display, we cannot use the Output encoded for a DCI-P3
    Display.

Substance Setup & Workflow
--------------------------

.. image:: {static}/images/blog/0008/sp-project-legacy.png
    :target: {static}/images/blog/0008/sp-project-legacy.png
    :alt: New project window with color-management tab

Color-management is not application-dependant but project-dependant.
As such, you will not find any options in the applications settings but in
the project one.

New Project
===========

The first occurence of these new option can be fin on the ``New project``
window. You will find a ``Color Management`` sub-menu at the bottom.

.. image:: {static}/images/blog/0008/sp-project-cm-options.png
    :target: {static}/images/blog/0008/sp-project-cm-options.png
    :alt: New project window with color-management tab

.. note-info::

    You can change all the color-management settings at any moment in
    the project settings. Keep in mind that big changes could break your
    project thought.

You will be offered between two modes ``Legacy`` and ``OpenColorIO``.
``Legacy`` corresponds to the pre-release way sp was working with. We will
skip this mode as it not usefull anymore.

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
is a color-management solution developed originaly by Sony Picture Imageworks
aiming at enforcing color-management consistency between DCCs.
I recommend `having a read at the documentation <https://opencolorio
.readthedocs.io/en/latest/concepts/overview/overview.html>`_ .

OCIO itself only define standards of utilisation and give you the tools to work
but the core of the system is the **OCIO config** (a ``.ocio`` file).
This is where all the color-transforms and options are defined.
For example ACES is a color-management system on his own but ship a version
through OCIO.

Main advantage is that OCIO is supported by most software (even if the
implementation wildy differs between each 😬 ) so you could get the same look
through all of your DCCs (in theory).

.. transition:: ~

For our convenience sp already ship with 3 OCIO configs :

- Substance
- ACES 1.0.3
- ACES 1.2

You can find them in the sp installation folder like this one :

::

    C:\Program Files\Allegorithmic\Adobe Substance 3D Painter\resources\ocio

Honestly I don't know why did they included two ACES version, only the last
one was needed, but it is awesome to have a default "Substance" config.

| Lot of flexibility here. First option being to use the shipped configs.
 On my opinion only the ``Substance`` config is interesting here.
| The 2 ACES one are the "default" dev configs with the hundred of
 colorspaces you will never need. It is better to use a lightweight ACES
 config like `the one from CAVE academy <https://caveacademy
 .com/product/cave-cg-animation-aces-ocio-config/>`_. (see `ACES Setup`_
 section)

The ``Substance`` config will be a good fit if you are using the tradional
sRGB linear workflow and do not wish to use an OCIO config in every DCC.
You will still have enough control to have a proper color-managed workflow.

Let's now see how you could load a custom OCIO config.

.. transition:: ~

Custom config
_____________

.. image:: {static}/images/blog/0008/sp-project-ocio-custom.png
    :target: {static}/images/blog/0008/sp-project-ocio-custom.png
    :alt: New project window with OCIO option set with a custom config.

The first option is to use the ``Custom`` option and the manually look for
the path to the ``config.ocio`` file on your disk.


.. block-warning:: Only a reference to the config path is saved in the project.

    When submiting a OCIO config through the ``Custom`` option, **the config is always
    loaded live from the disk**. This mean if you share a substance project with
    someone that doesn't have the OCIO config at the same exact path you will
    see this message pop up :

    .. image:: {static}/images/blog/0008/sp-project-ocio-custom-error.png
        :target: {static}/images/blog/0008/sp-project-ocio-custom-error.png
        :alt: Error window when the custom config can't be found.

See the bottom section `Substance parameters for OCIO configs`_ to continue
the setup.

Environment variable
____________________

The above might be enough for indivual artist but being in a pipeline
environement will require other way to set OCIO automaticaly.

.. note-info::

    If the OCIO environment variable is present and has a valid configuration
    file it will take over to override and disable the UI settings.

On Windows you have 2 way to set environment variable :

Global Settings
"""""""""""""""

.. image:: {static}/images/blog/0008/ocio-env-global.png
    :target: {static}/images/blog/0008/ocio-env-global.png
    :alt: Windows creating the OCIO environment variable.

You create a new variable named OCIO with the path to the config.
This variable will be used by ALL software that can read it. (unless
overriden).

This is not a recommended solution as you polute your environment variable + if
you decide to switch the config for an other one all your previous project
will be broken.

Set localy at startup
"""""""""""""""""""""

You defined the environment variable in a start-up script.
This is the cleanest way to do it but means you can't use the Windows shortcut
to start your software :

We use a ``.bat`` to configure and launch the software. Here is a basic ``.bat``
that will set the OCIO variable and then launch sp.

.. code:: shell

    set "OCIO=C:\aces_1.1\config.ocio"

    "C:\Program Files\Allegorithmic\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe"

.. note-default::

    To create a ``.bat`` just create a new ``.txt`` file, paste the above code,
    modify it with the path to your config, save it, and then just replace
    the ``.txt`` with ``.bat`` in the file's name.

| This mean that to launch Substance you will have to always use this .bat.
 No "double-clicking" on file to open them either.
| You can have a look on internet at `how to pin a .bat to the taskbar
 <https://superuser.com/questions/656611/how-to-pin-a-batch-file-to-the
 -taskbar-quicklaunch/656649>`_ .

But this guarantee a very robust software configuration per project.

Substance parameters for OCIO configs
_____________________________________

.. figure:: {static}/images/blog/0008/sp-project-ocio-options.png
    :target: {static}/images/blog/0008/sp-project-ocio-options.png
    :alt: Options for OCIO mode in sp..

    OCIO with Substance config properly configured.


This correspond to all the section bellow the color-management mode. It allow
to configure how inputs reacts with the OCIO config, i.e which colorspace is
being assigned by default.

Usually in other software this section is configured using the `OCIO roles
<https://opencolorio.readthedocs.io/en/latest/guides/authoring/overview
.html#roles>`_ defined in the OCIO configuration.
:text-danger:`But currently sp doesn't support OCIO roles.` Instead it is
using the ``working colorspace`` as a default colorspace everywhere, which mean
:text-danger:`you have to manually setup this section` to get correct result
with the auto settings.

If you look at the above image, this is how it supposed to look when picking
the Substance config. By default 8 and 16 bit images are supposed to be
considered as ``sRGB``, same goes for substance materials.

Make sure these options are properly configured with the intended colorspaces
for each format if you want all the ``auto`` options to work properly.

Visit the `ACES setup`_ section to find how this should be considered if you
are using the ACES config.

New Project : Conclusion
========================

Alright, to recap' everything for a new project you need :

1. Change the color-management mode to OCIO
2. Choose the OCIO config (already choosen if env variable set)
3. Edit the OCIO options to have the correct default colorspaces working.

And of course setting the other parameters related to your texturing.

Now you we are good to start the texturing workflow. The workflow will be
divided in the same sections explained in the theoratical part of this
article (see `Color-managed Workflow`_).

The Workspace in Sp
===================

The Workspace, in software is actually an "abstract" section. It just represent
the colorspace used as a reference, target or source for every color
transformations. It is defined in the OCIO config and cannot be changed outside
of it.

.. note-info::

    In the OCIO config it correspond to the ``scene_linear`` role.

.. figure:: {static}/images/blog/0008/sp-project-ocio-workspace.png
    :target: {static}/images/blog/0008/sp-project-ocio-workspace.png
    :alt: The Working Colorspace displayed in the Color-management tab.

    Visible in the Project's Color-management section (Using the ACES 1.2 OCIO
    config here)

It is just good to know what is the colorspace being used here.

The Display in Sp
=================

.. image:: {static}/images/blog/0008/sp-odt-default.png
    :target: {static}/images/blog/0008/sp-odt-default.png
    :alt: View-transform screenshot.

A good first step before working is to make sure the Display part is
properly configured so you don't start texturing while viewing wrong colors.
This Display part can be configured using what we usually called a
`view-transform` menu. In sp, you can find it at the top-right of your
viewport.

What you have to remember is that :text-green:`you need to choose the option
that correspond to your display.` If your display is calibrated to the
Display P3 colorspace (Apple displays), choose the Display P3 option.

But what if I don't know what my display is calibrated to ?

    A safe choice would the be to assume you are using a sRGB-like display.

.. _the rec709 transfer-function issue:

I see some people using Rec.709 instead of sRGB, why ?

    sRGB and Rec.709 share the same primaries, so you can use both without
    seeing color-shift due to different primaries. What change is the
    transfer function being used. But fasten your seat-bealt, here come the
    mess : Rec.709 only defined an :abbr:`OETF <opto-electrical transfer function>`
    which is intended for camera signal encoding, not data display encoding !
    For display encoding with the Rec.709 colorspace, one should use the
    `BT.1886 <https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1886-0-201103-I!!PDF-E.pdf>`_
    standard which can be resumed as a simple 2.4
    :abbr:`power-function <= gamma>`.

    So how to know which one of this two is being used ? Simple, if when
    compared to sRGB, the image looks darker, it's the OETF, if it's looks less
    contrasty, it's BT.1886.

    If you do the test, the Substance config use the OETF (which should not
    be used), while the ACES config use BT.1886.

You didn't answered to my question !? I'm just more confused now !

    As written previously, you need to choose the option that correspond to
    your display, so if your display is not calibrated to Rec.709+BT.1886
    don't use it. But some people like the look of it, being less contrasty,
    that's why its being choosed. But the display should not be a creative
    choice. If you like a less contrasty look, you should apply it in the Look
    (see under).

    Just to add more of confusion, the BT.1886 difference with sRGB can
    actually be used as a viewing environment compensation. So it can actually
    justify why using Rec709+BT.1886 instead of sRGB.

Anyways, I'm going too far from the subject, and someone already
wrote about this topic, I let you read this mind-blowing article from
Chris Brejon `OCIO, Display Transforms and Misconceptions <https://chrisbrejon
.com/articles/ocio-display-transforms-and-misconceptions/>`_.






OCIO Implementation Issues
--------------------------

.. note-default::

    The goal here is not to denigrate the dev team's works but rather to offer
    explanations and solutions at what could be better.

Display Issues
==============

This explanations were made possible thanks to the Chris Brejon's article
`OCIO, Display Transforms and Misconceptions`_.

Display components mismatch
___________________________

OCIO divide the Display section in 3 components :

-
    ``Display`` : the physical hardware you are using (monitor, TV, phone, ...).

-
    ``View`` : a way to encode the data for a specific viewing purpose.

-
    ``Look`` : a creative layer of modification on the data. ex: a grade.

Why does I explain you this ? Because these components are often mismatched
or forgot. Unfortunately Substance make no exception here.

.. image:: {static}/images/blog/0008/sp-odt-default.png
    :target: {static}/images/blog/0008/sp-odt-default.png
    :alt: View-transform screenshot.

If you look at the view-transform screenshot above, you can see that each
option has the the ``Default`` prefix.
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

And if we want to use a new OCIO v2 feature :

.. code:: yaml

    shared_views:
      - !<View> {name: False Color, colorspace: False Color}
      - !<View> {name: Raw, colorspace: Raw}

    displays:
      sRGB:
        - !<View> {name: Display, colorspace: sRGB}
        - !<View> {name: ACES, colorspace: ACES sRGB}
      DisplayP3:
        - !<View> {name: Display, colorspace: Display P3}
      Rec709:
        - !<View> {name: Display, colorspace: Rec709}
      Rec2020:
        - !<View> {name: Display, colorspace: Rec2020}

But again unfortunately, even if the above example is valid, it doesn't work
on sp and we can't select the ``Raw`` and ``False Color`` views. (even thought
sp use OCIO v2)

Partial Look support
____________________

If go back to the above explanations where I mention OCIO Display is build with
3 components, we see that I didn't mention the last one yet: Looks.

Looks is a color-tansformation performed in any colorspace aimed at
modifying the data in a creative way. This would allow for example the
artist to have a first look at how it's render could looks like after the
:abbr:`di <Digital Intermediate = grading process>` pass.

Usually Looks are defined similar to colorspaces, as a list, but you can also
make a Look available in a display view:

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

In the best case we shoould have a dropdown menu that would allow us to combine
the current ``view-transform`` with any Look defined. A good example of this
is Blender :

.. figure:: {static}/images/blog/0008/blender-cm.png
    :target: {static}/images/blog/0008/blender-cm.png
    :alt: Screenshot of Blender color-management menu.

    Notice how it respects the 3 components of an OCIO display.

Unfortunately, sp didn't implemented this feature yet. So we can only rely
on merging the look in a display view for now.

A good way to test this is using the `Filmic <https://github
.com/sobotka/filmic-blender>`_ OCIO config by Troy Sobotka.
The filmic encoding is correctly available in a ``View`` but require an
extra step to be correctly displayed. By default it is a flat log
representation, and require to choose a Look with the desired contrast amount.

To have it working in sp, it is requires to merge the Look in a new ``View``.

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



Issues Recap
============

This list aim at helping the potential Substance dev team members reading this
adressing the issues.

-
    Substance config use the wrong Rec.709 display encoding.
    (see `the rec709 transfer-function issue`_)

-
    Substance config miss simple P3 colorspaces while it offer a Rec2020 one
    (who would use it ??)

-
    Substance config ``displays`` key is not properly build.
    (see `substance-config-displays-fixed`_ )

-
    OCIO v2 feature ``shared_views`` is not supported.

-
    OCIO roles are not supported, as such default configuration for
    project is wrong and can confuse artists.

-
    The view-transform dropdown is too small in width. When selecting long
    ``display`` names, they got cropped. (see `sp-odt-name-cropped`_)



ACES setup
----------

.. TODO