Instancing in Katana
####################

:summary: How OpScript can be used to create a flexible solution for
    instancing.
:thumbnail: {static}/images/blog/0005/cover.jpg

:status: published
:date: 2022-03-30 20:58
:date-created: 2021-10-23 14:58

:category: tutorial
:tags: katana, instancing, lua, software
:author: Liam Collod

Katana, as usual, doesn't offer a "ready to go" solution for instancing.
This initial :abbr:`complexity test abbr>` can be overcome by the fact that we can create an
instancing solution that exactly suits our needs. And that is what we
are going to address in this post.
Additionally, I will explain how I tried to create a flexible solution for
instancing called ``KUI`` so you don't have to !

.. contents::

.. note::

   this is a note

hercle, ignigena camerarius!. bassus, bi-color mensas patienter tractare de neuter, nobilis byssus.

Intro
-----

As Katana's motto states : *It’s all just a bunch of Attributes.* And it
applies to instances too. They are just a bunch of locations with a defined
list of attributes understood by your render-engine.

Instancing Methods
------------------

Instancing comes in different flavors, that, similarly to all things, have
specific ups and downs. Your render-engine may also supply alternative ways to
produce instances so be sure to check its documentation on the topic.