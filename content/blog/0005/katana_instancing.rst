Instancing in Katana
####################

:summary: How OpScript can be used for instancing with flexible setup.

:status: draft
:date: 2021-10-23 14:58

:category: tutorial
:tags: katana, instancing, lua, software


Katana, as its usual, doesn't offers "ready to go" solution for instancing.
This initial complexity can be overcome by the fact that we can create an
instancing solution that exactly suits our needs. But we have to first
understand how it works.

Adtionnaly I will explain how I tried to create a flexible solution for
instancing called ``kui``.

And lastly you will find a paragraph specific to `Redshift`_ where I had some
troubles guessing what it needed to work.

.. contents::

.. block-warning:: Disclaimer

    My explanations reflects the experience I had with this subject and may
    not be totally accurate in other production contexts. Be sure to contact me
    if you spot big mistakes /  things to improve.



Intro
-----

An instance is not a magical object. It is just
a location with a defined list of attributes understood by your render-engine.
You can as such create an instance with a simple
``LocationCreate + AttributeSet`` (if you have time to loose) but we will be
using OpScripts to do so.

Here is a quick diagram that could resume how an instance is built :

.. image:: {static}/images/blog/0005/intro.png
    :alt: instancing principle
    :scale: 10%

The basic principle is that an ``instance`` links at least to one
``instance source`` (a scene-graph location).
The instance will create a "copy" of this instance source. You can then set
transformations overrides that will allow the instance having a different
position, rotation, etc, than the source.
Aditional attributes can also be set and used for shading to make the
instance even more different than the source.


Instancing Methods
------------------

Instancing comes in different flavor, that, similarly to all things, have
specific ups and down. You render-engine may also supply alternative ways to
produce instances so be sure to check its documentation on the topic.

Here is what the Katana documentation say about this:
`Q100518: Instancing Overview
<https://support.foundry.com/hc/en-us/articles/360006999219>`_


Leaf-level
==========

*(Never used this one)*

`The Katana documentation <https://support.foundry
.com/hc/en-us/articles/360006999259>`_ is pretty explicit.

.. container:: m-row

    .. container:: m-col-s-6

        .. block-danger:: cons

            Major drawback is that you can't have a location with children
            locations (to verify),
            and well it seems every render-engine has a way to decide which
            location is the first one to instance 🙂.

    .. container:: m-col-s-6

        .. block-success:: pros

            You just have to set a single attribute.

            You can easily apply modification on a single instance.
            *(ex: a Transform3D)*



*Would love to know in what case this one can be more pertinent than the other methods.*

Hierarchical
============

Each instance = one scene-graph location.

.. container:: m-row

    .. container:: m-col-s-6

        .. block-danger:: cons

            Too much instances (>~100 000) will lead you to performances
            issues. (pre-render)

    .. container:: m-col-s-6

        .. block-success:: pros

            You can easily apply modification on a single instance.
            *(ex: a Transform3D)*

Array
=====

One single scene-graph location where each instance correspond to an index
on each attribute.

.. container:: m-row

    .. container:: m-col-s-6

        .. block-danger:: cons

            Complicated to get per-instance override.

    .. container:: m-col-s-6

        .. block-success:: pros

            Better performances.


.. transition:: ~

And there is probably some aditional pro/cons inheritent to your render-engine
so again, check the documentation, and test stuff.
(For example , when I started to explore instancing, Redshift was not supporting
locations with children when using the ``array`` method.)

Instancing in Practice
----------------------

To start, there is a nice small example on the `official Katana documentation
<https://learn.foundry.com/katana/Content/ug/instancing/rendering_instances.html>`_
. It explains how to create instance using mostly Katana nodes and one small
OpScript to avoid stacking numerous ``AttributeSet`` nodes.
This approach is pretty basic : we manually set how much instances we want to
create and we need to manually move them. The setup also
take times to build and is not very scalable.

A more widely used solution depends on ``point-clouds`` : a type of location
composed of visual abstract "points" in the 3d space that can hold an
arbitrary number of attributes based on the point index.

You use each individual point's attribute to create an instance. For example,
each point can specify what kind of instance source it is representing, ...
Furthermore it's "abstract" aspect make it very convenient for transfering data
between DCCs.

A convenient way to create scene graph locations based on a source object like
a point-cloud, is to use the `OpScript
<https://learn.foundry.com/katana/Content/ug/working_with_attributes
/opscript_nodes.html>`_ feature. It is an entry door to use scripting while
staying in the Katana nodegraph system. Usage of OpScript require to learn
the `lua language <https://en.wikipedia.org/wiki/Lua_(programming_language)>`_
. But don't worry, if you don't want to get your hands dirty you will be able
to use a premade script/node shared in the `Katana Uber Instancing`_ section.

To create scene graph location we need to know how it must be structured.
For this what's better than having a look at the documentation :
`AttributesConventions/Instancing <https://learn.foundry.com/katana/4
.5/dev-guide/AttributeConventions/Instancing.html>`_. You notice that we
find the 3 instancing methods described again.

Let's now start building the scene.

Scene-Preparation
=================

For you to follow the tutorial, I will be providing you some assets. Actually
only a point-cloud, as to keep it simple, instances sources will be
primitives.

.. url-preview:: https://mega.nz/folder/uooQzJJR#5aguo_c3gLXPrkEnN62ZBg
    :title: Sources Files Download
    :svg: {static}/images/global/social/mega.svg

    15KB folder on mega.nz



OpScript-Preparation
====================

We are going to manipulate a lot of inputs and data and at some point we
will need to see what X variable equal to, what the result of X operation, etc
to just be able to know where we need to go scripting-wise. Usually this is
done by using the ``print()`` function. But this is very basic and can led to
various limitations.

To have a more robust way of debugging OpScript I made myself a small
logging module in lua. Kind of similar to what Python logging module does.
It add a bunch of line to your script but will allow more flexibility in the
way data will be displayed to you.

On top of a freshly created ``.lua`` file let's paste the content of this
file :

    https://raw.githubusercontent.com/MrLixm/Foundry_Katana/main/src/utility/lua_logger/lllogger.lua

We will then be able to use the logger methods to output message to the
console. *(This just wrap the ``print()`` function which in Katana, output the
result in the console that should be opened alongside your Katana)*

.. code:: lua

    logger:debug("any object")
    logger:info("any object")
    logger:warning("any object")
    logger:error("any object")

.. note-info::

    Alternatively, to avoid having to paste so much code you can use it as a
    lua module. See the `README.md <https://github.com/MrLixm/Foundry_Katana
    /tree/main/src/utility/lua_logger>`_ for instructions.

All this steps **are not mandatory**. They just help for faster debugging.


Katana Uber Instancing
----------------------

As we just saw, instancing can require in some cases quite some work before
having a result. That's why I tried to produce a solution that would be very
flexible with a vrey straightforward setup.

The goal here will be to create an 'uber' instancing node (just a group node
actually) where, using the same parameters, you could conveniently switch
between different instancing methods and have a lot flexibility on inputs.
(Leaf-level will be excluded as I'm not familiar with it.)


R&D
===

Let's first think at what could be the ``source`` of the instances data. A most
common case would be to use a point-cloud. We could also see an even more
flexible solution by allowing to use any location, like a locator.

The next step will be to extract the ``source`` attributes and convert them to
individual instances attributes. That's where we will meet a new issue :

| We know the destination of these attributes : scale, rotation, index, color,
 ..., we know that at least one of them will be present.
 But what is very variable is how they are named, what are the one that we
 actually need, etc. The first way to fix this issue is to define pipeline
 conventions, where X type of attribute should have X name, and so teh X name
 is hardcoded into your script. But production needs change often, and we can
 agree that having a script with as minimal hardcoded conventions as possible
 is better.
| The second solution is to have a way to specify to the script the name of
 the attributes present on the ``source`` and how to behave with them.
 We could do this using user arguments on the OpScript but I feel we can
 have an even more logicial solution that would be to have these infos on the
 ``source`` itself.

So the ``source`` would have a bunch of attributes which have a fixed naming
convention (we can't escape it) that will gave the script the info require
to process the ``source``. It will be more clear when applied to the script.



OpScript-Getting What We Need
=============================




Redshift
--------

The production where I had to look for instancing was using Redshift,
and unfortunately it seems that, at that time, the instancing features where
"minimally" implemented and some stuff was missing/broken.
Fortunately, Redshift developer's Juanjo was very responsive and very quickly, fixed
all the issues I found. Discussion can be found `in this thread
<https://redshift.maxon.net/topic/33461/more-documentation-for-instancing-in-katana?_=1634997159560>`_.

