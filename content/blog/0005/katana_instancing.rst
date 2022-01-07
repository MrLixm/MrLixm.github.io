Instancing in Katana
####################

:summary: Let's see how to produce a flexible solution for instancing.

:status: draft
:date: 2021-10-23 14:58

:category: tutorial
:tags: katana, instancing, lua, software


Katana doesn't offers "ready to go" solution for instancing (as for most things)
, if you add the fact that you render-engine might need a different
configuration, having a working solution can become hard depending of your industry knowledge.

I will explain my solution to have a flexible enough instancing system,
in hopes that this will save you some time.

You will also find a paragraph specific to `Redshift`_ where I had some troubles guessing what it needed.

.. contents::
    :class: m-block m-default

.. block-warning:: Disclaimer

    My explanations reflects the experience I had with this subject and may not be
    totally accurate. Be sure to contact me if you spot big mistakes.



Intro
-----

As a first step, please read the Katana documentation on this subject:
`Q100518: Instancing Overview <https://support.foundry.com/hc/en-us/articles/360006999219>`_

An instance is not a magical object. It is just
a location with a defined list of attributes understanded by your render-engine.
You can as such create an instance with a simple ``LocationCreate + AttributeSet``
(if you have time to loose) but we will be using OpScripts to do so.

Here is a quick diagram that could resume how an instance can be created :

.. image:: {static}/images/blog/0005/diagram.png
    :alt: instancing principle

The basic principle is that an instance links at least to an ``instance source`` (a location).
The instance will create a "copy" of this instance source. You can then set
transformations overrides that will allow the instance having a different
position, rotation, etc, than the source.
Aditional attributes can also be set and used for shading to make the
instance even more different than the source.


..
    - ``instance`` : object being the result of an instancing operation
    - ``instance source``: object source that will be "copied" to an instance.




Instancing Methods
------------------

Instancing comes in different flavor, that, similarly to all things, have
specific ups and down. You render-engine may also supply alternative ways to
have instances so be sure to check its documentation on the topic.

Leaf-level
==========

*(Never used this one)*

`The Katana documentation <https://support.foundry
.com/hc/en-us/articles/360006999259>`_ is pretty clear on it.

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

Application
-----------

The goal here will be to create a 'uber' instancing node (just a group node
actually) where, using the same parameters, you could conveniently switch
between different instancing methods and have a lot flexibility on inputs.
(Leaf-level will be excluded as I'm not familiar with it.)

To easily create scene-graphs location we are going to use `OpScript
<https://learn.foundry.com/katana/Content/ug/working_with_attributes
/opscript_nodes.html>`_ .
I'm not going to explain in details what it is, just enough so you can follow.

OpScript-Preparation
====================

We are going to manipulate a lot of inputs and data and at some point we
will need to see what X variable equal to, what the result of X operation, etc
to just be able to know where we need to go scripting-wise. Usually this is
done by using the ``print()`` function. But this is very basic and can led to
various issues.

To have a more robust way of debugging OpScript I made myself a small
logging module in lua. Kind of similar to what Python logging module does.
It add a bunch of line to your script but will allow more flexibility in the
way data will be displayed to you.

On top of a freshly created ``.lua`` file let's paste this :

.. raw:: html

    <script src="https://emgithub.com/embed.js?target=https%3A%2F%2Fgithub.com%2FMrLixm%2FFoundry_Katana%2Fblob%2Fmain%2Fsrc%2Futility%2Flua_logger%2Flllogger.lua&style=atom-one-dark&showLineNumbers=on&showFileMeta=on&showCopy=on&fetchFromJsDelivr=on"></script>

We will then be able to use the logger methods to output message to the
console. *(This just wrap the ``print()`` function which in Katana output the
result in the console that should be opened alongside your Katana)*

.. code:: lua

    logger:debug("any object")
    logger:info("any object")
    logger:warning("any object")
    logger:error("any object")

So all of this code **is not mandatory**. It can just help debugging.



Redshift
--------

The production where I had to look for instancing was using Redshift,
and unfortunately it seems that, at that time, the instancing features where
"minimally" implemented and some stuff was missing/broken.
Fortunately, Redshift developer's Juanjo was very responsive and very quickly, fixed
all the issues I found. Discussion can be found `in this thread
<https://redshift.maxon.net/topic/33461/more-documentation-for-instancing-in-katana?_=1634997159560>`_.

