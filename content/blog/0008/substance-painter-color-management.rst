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

The article is divided in two parts. You got the theory first and then the
"how to do it" at the end. Is is strongly recommend to read the theory part but
you could just read the "how-to" part to get the quickest answers.

.. note-info::

    OCIO was introduced in `Substance-Painter version 7.4 <https://substance3d.adobe.com/documentation/spdoc/version-7-4-223053247.html>`_

    This is the version used through this article and some features might
    have changed since.

.. block-info:: Official Documentation

    https://substance3d.adobe.com/documentation/spdoc/color-management-223053233.html

.. contents::

New Project
-----------

.. image:: {static}/images/blog/0008/sp-project-legacy.png
    :target: {static}/images/blog/0008/sp-project-legacy.png
    :alt: New project window with color-management tab

Color-management is not application-dependant but project-dependant.
As such, you will not find any options in the applications settings but in
the project one.

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

OCIO options
------------

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

Picking an OCIO config
======================

| Lot of flexibility here. First option being to use the shipped configs.
 On my opinion only the ``Substance`` config is interesting here.
| The 2 ACES one are the "default" dev configs with the hundred of
 colorspaces you will never need. It is better to use a lightweight ACES
 config like `the one from CAVE academy <https://caveacademy
 .com/product/cave-cg-animation-aces-ocio-config/>`_.

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

See the bottom section `Default parameters for OCIO configs`_ to continue
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

Default parameters for OCIO configs
===================================

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

Vist the `ACES setup`_ section to find how this should be considered if you
are using the ACES config.

Conclusion
==========

Alright, to recap' everything for a new project you need :

1. Change the color-management mode to OCIO
2. Choose the OCIO config (already choosen if env variable set)
3. Edit the OCIO options to have the correct default colorspaces working.

And of course setting the other paramaters realted to your texturing.
Now you we are good to start the texturing workflow.


Color-managed Workflow
----------------------

| Now that the project is properly configured, we will see how to keep your
 workflow properly color-managed.
| This require a bit of theory first :

We can break the workflow in 4 sections : ``Input``, ``Workspace``, ``Display``
and ``Output``

.. container:: l-c-color l-mrg-l l-flex-center-c

    .. raw:: html
        :file: diagramA.svg


You transfer ``data`` between each of this section. Data that must be
potentialy decoded and then encoded, depending of what the section require.
In Substance Painter this ``data`` is most of the time pixels, encoded
with the RGB system.

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

This is important what type the data you are manipulating
belongs to, because it will allow, in a case, to skip all the mess that
color-transformations can be.

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

.. container:: l-c-color l-mrg-l l-flex-center-c

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
a transfer-function depending of the file format used. But we will get back
to it later. .. TODO link section

Workspace
_________

It is an intermedariy section where we know exactly what it will output so
we can know how to convert all its inputs properly. In our context this is
the "Working color space". In OCIO term it correspond to the


ACES setup
----------

.. TODO