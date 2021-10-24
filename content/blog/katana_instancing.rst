Instancing in Katana
####################

:date: 2021-10-23 14:58
:category: software
:summary: Let's see how to produce a flexible solution for instancing.
:status: draft

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

.. image:: {static}/images/blog/katana_instancing/diagram.png
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

Instancing comes in different flavor, with ups and down for each one. And your
render-engine may even have some aditional/modified ones.

Leaf-level
==========

(Never used this one)

The Katana documentation is pretty clear so I'm not going to re-explain anything.

.. container:: m-row

    .. container:: m-col-s-6

        .. block-danger:: cons

            Major drawbacks is that you can't have a location with children locations (to verify),
            and well it seems every render-engine has a way to decide which location is the first one to instance 🙂.

    .. container:: m-col-s-6

        .. block-success:: pros

            You just have to set a single attribute.

            You can easily apply modification on a single instance (ex: a transform3D)


*Would love to know in what case this one can be more pertinent than the other methods.*

Hierarchical
============

Each instance = one location.

.. container:: m-row

    .. container:: m-col-s-6

        .. block-danger:: cons

            With too much instances (>~100 000) you will start to see performance issues

    .. container:: m-col-s-6

        .. block-success:: pros

            You can easily apply modification on a single instance (ex: a transform3D)

Array
=====

One single location where each instance correspond to an index on each attribute.

.. container:: m-row

    .. container:: m-col-s-6

        .. block-danger:: cons

            Complicated to get per-instance override.

    .. container:: m-col-s-6

        .. block-success:: pros

            Better performances.


.. transition:: .

And there is probably some aditional pro/cons inheritent to your render-engine
so check the documentation and test stuff.

(For example , when I started to explore instancing, Redshift was not supporting
locations with children when using the ``hierarchical`` method.)

Application
-----------

The goal will be to create a node (a group) where, using the same parameters,
you could conveniently switch between different instancing methods.
I am going to forget about Leaf-level as I'm not familiar with it.


Redshift
--------

The production where I had to look for instancing was using Redshift,
and unfortunately it seems that, at that time, the instancing features where
"minimally" implemented and some stuff was missing/broken.
Fortunately, Redshift developer's Juanjo was very responsive and very quickly, fixed
all the issues I found as discussed `in this thread <https://redshift.maxon.net/topic/33461/more-documentation-for-instancing-in-katana?_=1634997159560>`_.

