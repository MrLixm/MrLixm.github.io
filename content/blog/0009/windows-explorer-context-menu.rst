Creating custom context menu for Windows file explorer.
#######################################################

:summary: Making tx, rescaling image, displaying alembic content all as fast as
          a right click can be.
:thumbnail: {static}/images/blog/0009/

:status: draft
:date-created: 2023-01-29 21:15
:date: 2023-01-29 21:15

:category: tutorial
:tags: productivity
:author: Liam Collod

I had always been a fan of contextual menu in interfaces. They are a very fast
way to run various processes on a selected item. And at the same time you
don't have to remember which action you can run on the item, or how the
action was named. You right click and everything doable is
available a few pixels away from your cursor.

And I had come to the point where, while browsing my files in the
file-explorer, I found that I needed to run a specific tool on a file. And
then 10 min later again, and the next week again ... Each time I had to open
the tool (so depends how easy it is to find its executable), copy the path of
the file, and give it to the tool. Huh ... too long I wish I could automate
that.

A bit of reasearch, and of course you can. You probably noticed that some
applications you install doesn't refrain themselves for adding actions to the
context menu, so why not you ?

.. contents::

Why ?
-----

You might have clicked on this article because you already knew this sounds
like something you wanted to do at some point. But for the others why would
you even need to add new actions to the context menu ?

To get an example that will be familiar for the 3d artists out there let's take
the case of ``makeTx``. If you are using Arnold you know what I'm going to
talk about. For every texture you use in your scene, Arnold will usually
generate a version of it in its own format called ``tx``. This process is
usually done automatically when you click render but there is multiple reasons
it can goes wrong, or might not just be the behavior you want. The
solution to fix it is to manually generate the tx files. To achieve that you
can use the ``makeTx.exe`` tool that is found alongside the Arnold installation.

The particularity with that tool being that it is a `Command Line
Interface <https://en.wikipedia.org/wiki/Command-line_interface>`_, which will
allow us to have something like this :

.. TODO put a GIF of the result

Command Line Interfaces programs
--------------------------------

A Command Line Interface program is made to be interacted with from the command
line, and not from a graphical interface like most programs. If you are not familiar
with :abbr:`CLI <Command Line Interface>`, they are going to look very unpleasant
to use compared to a :abbr:`GUI <Graphical User Interface>`. But their power
will be found in the flexibility they offer, especially for automatizing tasks.
It's like you were ordering the program to perform an action by describing it in
a sentence.

This is will be useful in our case, because this means that by passing the
"right sentence" to makeTx, he could generate a tx from the file that has been
selected from the right-click !

If you ever tried to double click on a .exe just to see a window open and
close immediatly, it's probably because it was a CLI. By double clicking on it
you executed it, it execute the task it was made for (in our case nothing
because you didn't gave it any argument), and then close once finish.

To first see what's going when you don't give it arguments, let's open the
command line. On Windows, this can be achive using ``Win`` + ``R`` then typing
``cmd`` and enter. You can also just search for ``Command Prompt`` in the
Windows search bar.

.. image:: {static}/images/blog/0009/command-prompt-blank.png
    :target: {static}/images/blog/0009/command-prompt-blank.png
    :scale: 80%
    :alt: A blank command prompt.

Then to execute our program you need to pass the path to its executable.
Easiest way is just to drag and drop the executable from the file explorer
to the command prompt. You can also just copy and paste its path.

.. note-info::

    On Windows, make sure paths are always wrapped in double quotes like
    ``"C:/Program Files/xyz/bin/myapp.exe"``

Then press enter to start executing it.

.. image:: {static}/images/blog/0009/command-prompt-maketx.png
    :target: {static}/images/blog/0009/command-prompt-maketx.png
    :scale: 80%
    :alt: Command prompt after executing makeTx.exe

Without any argument, most CLI will just display their documentation. Which
we will anyway need to open at leat one time to make sure we know what
arguments the tool expects.

.. note-info::

    Most CLI will display their documentation if you just pass the
    ``--help`` argument.


maketx
======

.. url-preview:: https://openimageio.readthedocs.io/en/latest/maketx.html#maketx
    :title: OpenImageIO - makeTx
    :svg: {static}/images/blog/0009/oiio-icon.svg
    :svg-size: 50

    Official makeTx documentation. Arnold version is slightly different.


Alright, how does makeTx works ? You can see on the line ``Usage : maketx
[options] file...`` that it expect the path of the file to be provided last,
and before some options.

The options are listed just under, and there is a lot of them. Usually
options/arguments are documented but here we will have to rely on their name.
But don't worry, no need for playing the guess game of which options does
what we want. How ? Well you know Arnold already auto-convert the tx files
for you, so it knows which options to use. And thanksfully, the whole command
used to generate the tx file is actually embeded in the tx's metadata !

But how do I retrieve the tx's metadata ? Well, by using an other CLI that
we are going to see a bit later, I can retrieve it :

.. code:: text

     Software: "OpenImageIO-Arnold 2.4.0dev : maketx G:/whatever/sources/FREDDY_Shoes/texturing/publish/textures-4k.v04\FREDDY_Shoes_Diffuse_Color_1001.exr --opaque-detect --constant-color-detect --monochrome-detect --fixnan box3 --oiio --attrib tiff:half 1 -v -u --unpremult --oiio --format exr"

Seems there is a lot of options used ! One important thing to keep in mind is
that **those options vary depending on what kind of texture you are converting
and how the "texture node" in the source DCC is configured.** The most notable option
being ``--colorconvert`` used to convert the input file to another colorspace.

.. note-warning::

    You must be aware that the ``maketx.exe`` from the Arnold installation has
    been slightly modified from the "official" maketx of OpenImageIO. It append
    default argument to the command, no matter if you already gave them.

    Those default argument are always :

    .. code:: shell

        --opaque-detect --constant-color-detect --monochrome-detect --fixnan box3 --oiio --attrib tiff:half 1

    And as such doesn't need to be provided again when calling maketx manually.

Anyway we have what we need, the whole command required to convert a file to tx.
We can now have a look at how to create the context menu !

.. note-default::

    You might have notice that in the above command the filepath is specified
    before the options, sometimes order matters, but here seems makeTx don't care !

Editing the registry: Basics
----------------------------

Unfortunately, not really a simple and easy way to add actions to the context menu
(there is thanks to some apps on othe interfaces that does the same thing I'm
going to explain), we will have to edit the `registry <https://en.wikipedia.org/wiki/Windows_Registry>`_.

If you ever have to use it, you know it's not easy to find what you are looking for.
Or you are probably aware that editing the wrong stuff can easily break
parts of your system.

To mitigate those issues we will be using ``.reg`` files, instead of browsing
the registry Editor. Main logic stay the same, the reg file will just create
new registry keys and set their values. The advantages are :

1.
    They allow for a reproducible process. That means that if your reformat your system,
    you don't have to remember which key you created. Just execute the reg file again.
2.
    You can create a copy of the initial reg file that does the inverse, meaning
    removing the keys instead of adding them.

.. note-warning::

    Keep in mind that editing the registry can still be dangerous, so it is
    recommended to save a backup of it before any change.

Creating the .reg file
======================

.. block-info:: Documentation

    https://en.wikipedia.org/wiki/Windows_Registry#.REG_files

As a first step, create a blank new file like a ``.txt`` and just replace the
extension with ``.reg`` (you might need to display file extension in the View
menu of the file explorer if not set already).

Then right click and open the file with any text/code editor (make sure to not
click on it else you will be executing it !).

Just so you get an idea of the finished product, here is what we will be
producing :

.. include:: maketx.reg
    :code: ini

.. note-info::

    You can add comment lines by starting them with a semi-colon ``;``

On the first line, we have to put this text :

.. code:: ini

    Windows Registry Editor Version 5.00

The next importanty step will be to determine the root location of the key to use.
This location will determine on which type of file explorer entities the action
in the context menu will appear.

Here are the few options availables :

.. class:: l-table l-overflow

    ====================== =================================================================
    Files                  ``HKEY_CURRENT_USER\Software\Classes\{EXTENSION}\shell\``
    Directories            ``HKEY_CURRENT_USER\Software\Classes\Directory\shell``
    Directories Background ``HKEY_CURRENT_USER\Software\Classes\Directory\Background\shell``
    Drive                  ``HKEY_CURRENT_USER\Software\Classes\Drive\shell``
    ====================== =================================================================

.. note-default::

    If you would like to make the context-menu action available to ALL users of
    the system you could replace ``HKEY_CURRENT_USER\Software`` with
    ``HKEY_CLASSES_ROOT``.

As makeTx expect a single file, we will be using the first key location. We
still need to determine on which file extension the action should appear. Unless
you want to specifically choose which file format can be converted to tx we will
consider by laziness that all file formats might be, and as such replace
``{EXTENSION}`` with ``*``.

Great, we have now the root path for each key. Now time to create the first key.
We just need a name for it (*special-character-free*). No need to think to hard,
we will be using just ``makeTx``.

Let's put that into the reg file :

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]

You notice that I added a new key location ``shell`` after our root key. It's
needed by Windows. Now we can configure our key. We can start by configuring
which text will appear in the context-menu for this key :

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"

I could have put any sentence between the 2 double quotes, but I decided to
stay simple.

Then you might want to add a icon next to your action. It can be achieved like :

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"

But you have to keep in mind :

- You have to put an absolute path
- You have to escape backward slashes like ``\\``
- You have to use an ``.ico`` file. There is plenty of online converter for it.
- If for whatever reason thet path doesn't exists/is not valid, you will get a default "sheet" icon.

And finally the most important option, what is executed when clicking on the action !
We have to create a new key ``command`` and then configure it.
For the configuration we will pass a string as you would execute the program
from the command prompt.

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\command]
    @="D:\\resources\\maketx.exe"

If you remember what we tested previously, this will only display the documentation
of makeTx, cause we doesn't provide any argument. But let's move step by step
and test what we already have.


Executing the .reg file
=======================

Save your reg file from your text/code editor and double click on it. Windows
will gift you 3 dialogs to accept, but that will be all you have to do !

As a safety let's manually check in the registry if it was registered. Open the
``Registry Editor`` (you can use windows search). In the window that opens,
find the "current path" field, right under the menu bar. Inside paste
the path of the key we created and press enter.
The editor should directly browse to the key.

.. image:: {static}/images/blog/0009/registry-editor-maketx.png
    :target: {static}/images/blog/0009/registry-editor-maketx.png
    :alt: Screenshot of the Registry Editor int he state described above.

If you would want to delete what we did, you could just delete the ``makeTx``
key (but we will see an alternative later).

Aright in theory it should work, what about practice ? Well pick any file
in the file explorer (because remember we put it under ``*`` which work for
all file extensions) and right click on it. You should now see the ``makeTx``
action near the top !

Let's test it, click on it :

.. image:: {static}/images/blog/0009/rmb-makeTx-demo-1.gif
    :target: {static}/images/blog/0009/rmb-makeTx-demo-1.gif
    :alt: gif of right clicking on a file and clicking on the makeTx action

Well ... it just open and close. Not very useful ... But this is normal, remember
what I explained in the `Command Line Interfaces programs`_, the program execute
its task and then close. If we want to keep its result displayed we have to
open it from the command line. And that's a task for the next section !

Editing the registry: Advanced
------------------------------

The previous section allowed us to add a simple new action to the context menu,
that just execute the application we gave it. But we are still missing plenty
of use-cases, like how to keep the interface open in the case of a CLI, or even
more importantly, how do we pass the path of the file we right-clicked on, to
the command to execute ?

Calling the command prompt
==========================

Let's adress the issue we stopped the previous section at. As our tool is a CLI,
it close once finished. But we want to keep its result visible. Manually the solution
was to execute it from an existing command prompt window. And we will do exactly
the same for our context-menu action.

Get back to out .reg file and the last line where we define our command to execute.

To open the command prompt we simply need to prefix our command with
``cmd /k``, so we have:

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\command]
    @="cmd /k \"D:\\resources\\maketx.exe\""

By safety we also wrapped our path between esapced double quotes, to make sure
the command prompt doesn't complain.

Save the reg file and execute it again. Find a file again, and execute the
action in the context-menu as previously.

We now have a command prompt window that open and execute the makeTx.exe. But
the window stays open because it was not opened by makeTx but by us. Nice.

Retrieving the file selected in the command
===========================================

Probably the most interesting option for our context-menu. We selected a file
by right-clicking, this mean we want to execute a program on it, by passing the
path of this file to the program.

For now our makeTx action only open the documentation of the program cause it
doesn't receive any argument. By bassing the path of the file it should now
start the conversion.

To retrieve it simple we will be using the ``%1`` variable (it simply retrieve
the first argument passed to the command line) :

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\command]
    @="cmd /k \"\"D:\\resources\\maketx.exe\" \"%1\"\""

Again we wrap it between escaped double-quotes by safety BUT we also now `escape
the whole command <https://ss64.com/nt/syntax-esc.html>`_ using double-quotes
else we will get a `very funky behavior <https://stackoverflow.com/a/15262019/13806195>`_.

Repeat the usual steps to tests, and you should now see the file right-clicked
properly converted to tx (if you selected an image format selected by makeTx
of course).

Passing more arguments
======================

You remember at the beginning that I extracted the full command used by makeTx
on an existing .tx file ? There was a lot of additional arguments used. As I am
personnaly using maketx from the Arnold installtion I will remove all the
argument that maketx will already add for me anyway.

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\command]
    @="cmd /k \"\"D:\\resources\\maketx.exe\" \"%1\" -v -u --unpremult --format exr\""

No need to espace anything this time but make sure they are part of the
"global string" passed to ``cmd``.

Test again, you should mainly see much more info being displayed as used the
``-v`` option for "verbose".

And at that state we have a totally working command, but don't leave yet, we
still have a few improvements to make !


Creating a "uninstall" reg file
===============================

For now we have a single file that allow us to create the keys in the registry.
But what if we want the inverse, meaning removing them ? All program can be
installed and uninstalled, so it should be the same for our context-menu action.

As mentioned before you could manually dig into the registry to delete the key,
but if we took the time to create a reg file, it's not to end up browsing the
registry manually to revert it.

The solution is to create a new reg file that delete the keys instead of adding
them. To start just copy/paste the existing reg file we have been creating.

Also open it in your text/code editor. And now very simple edit, in front of
each key path, after the first bracket, add a minus character :

.. code:: ini

    Windows Registry Editor Version 5.00

    [-HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"

    [-HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\command]
    @="cmd /k \"\"D:\\resources\\maketx.exe\" \"%1\" -v -u --unpremult --format exr\""

That's about it. It's enough to tell window to remove the keys instead of creating them.
You could simplify the file by removing the line setting values but I will leave
them so I can remember exactly what I'm removing.

Now that you have 2 files (good idea to keep them side by side), you will need
to remember that if you add a new key / edit an existing one in the "create" reg
file, you also need to propagate the changes in the "uninstall" reg file.

And we end up with a pretty robust workflow, "install" your custom context-menu
in one double-click and "uninstall" it the same way ! Without having to remember
which key you added or manually browsing the registry editor.


Using environment variables for robustness
==========================================

In all the previous examples we have been using an absolute path to
``maketx.exe``. Let's imagine your directly picked the maketx located in your
Maya Arnold installation, or whatever other DCC. What happens if you uninstall
that version ? Well your command will break. You will have to edit the reg file
with the new maketx path and edit it again ...

    But wait ! I could just copy maketx.exe to one of my personal resources
    directory so I'm sure it will not be deleted when uninstalling Arnold !

And you'd be right, maketx is a standalone program that doesn't need anything
else to work so you could just copy it anywhere else. But what happens when
you want to upgrade your maketx version ? Or you move it. Well you
have to go find and update the reg file to execute it again. Not the
most annoying task, but we can do better.

Introducing `environment variables <https://en.wikipedia.org/wiki/Environment_variable>`_.
A system wide way to set and query values. I will not make a full tutorial
on them so we will skip to the essential. Feel free to browse the internet to learn
more about them.

0. In the Window search bar type "environment" and select "Edit Environment variable"
1. Select Edit
2. Create a new variable at user level
3. Fill the values, we will be naming it ``MAKETX``. Don't forget to escape
   the path of maketx with quotes if it has special characters like in my case.
4. "Ok" for all dialogs.

.. image:: {static}/images/blog/0009/env-var-maketx.png
    :target: {static}/images/blog/0009/env-var-maketx.png
    :alt: step by step to set environment variable

.. note-warning::

    Be carefull when choosing a name for your envionement variable. It's possible
    that a program will expect this variable name and use it. In our case
    ``MAKETX`` has a high chance of being expected by a program, but at the same
    time it would probably also expect the path to the maketx executable. So
    in a way it should not break anything.

And now to get the environment variable value in our command we need to use
the `batch <https://en.wikibooks.org/wiki/Windows_Batch_Scripting>`_ syntax
``%ENVVARNAME%`` :

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\command]
    @="cmd /k %%MAKETX%% \"%1\" -v -u --unpremult --oiio --format exr\""

Again we have to escape our variable declaration so it's the command prompt
we open that resolve the variable. For escaping it we just need to double the
percent character.

Same routine, save and test. Everyhting should just work like before.

Now you should never have to get back to your reg file to edit it.

.. TODO rename "actions" to menu ?

Creating sub-menus
==================

One feature that you might want to use, would be to have nested menus. For
example the default "Open With" menu offer multiple options once hovered.

With our example it would be nice to have multiple maketx options, one for
Arnold, one for Renderman, one with a colorspace conversion, ...

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"
    "subCommands"=""

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\shell\txconvert]
    "MUIVerb"="convert to .tx"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\shell\txconvert\command]
    @="cmd /k %%MAKETX%% \"%1\" -v -u --unpremult --oiio --format exr\""

What happened ? Well first you can see our root key got a new value set with
``"subCommands"=""``. We then added a new sub-key. For that we took the root
key path and added ``shell\`` + a new custom name for that key. That new key
can use the same options as the root key and I used ``MUIVerb`` again to set
the text displayed in the interface.

As I don't want to create a new nested sub-menu from it I can copy/paste
the key path and ``\command`` as before to specify what command it will execute.

Here is the whole example I mentioned before :

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx]
    "MUIVerb"="makeTx"
    "icon"="F:\\blog\\demo-icon.ico"
    "subCommands"=""

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\shell\txconvert]
    "MUIVerb"="convert to .tx"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\shell\txconvert\command]
    @="cmd /k %%MAKETX%% \"%1\" -v -u --unpremult --format exr\""

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\shell\txconvertprman]
    "MUIVerb"="convert to Renderman .tx"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\shell\txconvertprman\command]
    @="cmd /k %%MAKETX%% \"%1\" --prman -v -u --unpremult --format exr\""

    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\shell\txconvertsrgb]
    "MUIVerb"="convert to .tx - sRGB source"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\makeTx\shell\txconvertsrgb\command]
    @="cmd /k %%MAKETX%% \"%1\" --colorconvert sRGB linear -v -u --unpremult --format exr\""

.. note-warning::

    If you got your maketx executable from Arnold installation the second key
    with the ``--prman`` option will not work as Arnold always send ``--oiio``
    which conflict with ``--prman`` :(

.. image:: {static}/images/blog/0009/rmb-makeTx-demo-submenus.gif
    :target: {static}/images/blog/0009/rmb-makeTx-demo-submenus.gif
    :alt: example of right clicking on a file with the above setup

.. note-info::

    Menus are sorted alphabetically by key name. In the above example even
    if I first create ``txconvertsrgb``, it will still be displayed after
    ``txconvertprman``. A workaround for this would be to se a number prefix
    like ``001txconvertsrgb``, but this also mean you have to edit all your
    key when you want to insert a new one between existing ones.


Auto-generating the .reg files
==============================

For the more technical person that will be reading this article. I already
simplified all the steps above by creating a python CLI.

.. url-preview:: https://github.com/MrLixm/Reg-file-creator
    :title: GitHub - Reg-file-creator
    :image: https://opengraph.githubassets.com/b156f27a74c59c1a80f31050d52fa66fba750b1d3cf63253bc338b5050f53517/MrLixm/Reg-file-creator

    Python package to create context-menu entries in windows via .reg file.

It doesn't simplify that much the process, but it allow you to write a more
convenient json file to convert it to the 2 reg files.

Cool use cases ideas for context-menus
--------------------------------------

Because makeTx is not the only program that is cool to have available has a right
click, here is a few ideas that could really boost your workflow !

OIIO Tool
=========

I will start by the most useful of all (for a 3D artist at least). `oiiotool
<https://openimageio.readthedocs.io/en/latest/oiiotool.html#>`_ is the CLI
version of the OpenImageIO library and was designed to perform image-processing.

Just have a look at the documentation and the `multiple examples it includes
<https://openimageio.readthedocs.io/en/latest/oiiotool.html#oiiotool-tutorial-recipes>`_
to get an idea of how powerful it is.

As it could handle probably hundred of actions you want to perform from a
context menu, I will just show a few very useful of them.

.. block-default:: How to download it

    oiiotool is part of the `OpenImageIO code library <https://github.com/OpenImageIO/oiio>`_
    , and as such is not officially downloadable. You have to compile the
    library yourself to get it.

    Fortunately it's not the only solution :

    -
      | It is shipped with the Arnold installation !
      | You can find it in ``C:\Program Files\Autodesk\Arnold\maya{VERSION}\bin``
      | It's a totally standalone builded application so you can copy it anywhere

    -
      | `Someone shared pre-compiled version of OIIO <https://www.lfd.uci.edu/~gohlke/pythonlibs/#openimageio>`_
        Make sure to download the ``x64.zip`` version.
      | note1: the versions are a bit old but better than nothing
      | note2: the .exe need some of the ``.dll`` next to it to work


.. note-warning::

    The following examples assume you put the path to ``oiiotool.exe`` in an
    environment variable ``OIIOTOOL`` as shown previously.

Retrieving image statistic and metadata
_______________________________________

Especially useful for OpenEXR files. To check what is inside.

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool]
    "MUIVerb"="OIIO Tool"
    "icon"="F:\\softwares\\os\\config\\contextmenus\\oiiotool\\oiiotool.ico"
    "subCommands"=""

    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiioinfo]
    "MUIVerb"="Display Info"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiioinfo\command]
    @="cmd /k %%OIIOTOOL%% --info -v \"%1\""


Rescaling textures
__________________

It is most common that you exported textures in with big dimensions like
4096x4096 and that you need to resize them as you don't need that much pixels.

Again with oiiotool, as fast as right click can be !

This time setuping this context-menu will be more complicated. If we were to
reuse the workflow we used previously we woudl set something like this :

.. code:: ini

    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale2048]
    "MUIVerb"="rescale 2048"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale2048\command]
    @="cmd /k %%OIIOTOOL%% -v \"%1\" --resize 2048x0 -o \"%~n1-2048%~x1\""

The issues is in the last argument of the command where we need to pass the path
of the new file OIIO need to write. If we were to overwrite the existing file,
easy you can just give ``\"%1\"``. But here we want to create a new file.
The batch language has a special syntax to make path manipulation on variables.
Unfortunately the syntax doesn't work when called from ``cmd /k``.

.. block-info:: path manipulation in batch

    https://en.wikibooks.org/wiki/Windows_Batch_Scripting#Percent_tilde

    Let's dissect ``%~n1-2048%~x1`` we are using here :

    - ``%~n1`` : the file name without path and extension of the first argument (1)
    - ``-2048`` : the suffix we add to the filename.
    - ``%~x1``: File name extension including the period of the first argument (1)

We need a workaround to be able to use the full batch syntax. This workaround
could also be used if you need to execute more complex commands. So here we will
be using a ``.bat`` file to define our command, and the registry command will
just start the bat file.

Create a new ``.bat`` file (create a .txt and just rename the extension). Open
it with any text/code editor and inside paste the following :

.. code:: batch

    @echo off

    %OIIOTOOL% -v "%1" --resize %2x0 -o "%~n1-%2%~x1"

You notice we replace ``2048`` with ``%2`` which imply we will be using the
2nd argument passed to the .bat to determine the size to rescale. With this we
can use one .bat to rescale to any size !

Save the .bat somewhere then let's get back to our .reg file :

.. code:: ini

    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale2048]
    "MUIVerb"="rescale 2048"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale2048\command]
    @="cmd /k \"F:\\blog\\path\\to\\oiiotool-rescale.bat\" %1 2048"

Don't forget to also escape the backward slaches in the path. You notice that
we just forward the path of the file selected as first argument of the bat, and
the second argument is indeed the size to use.

You can the just copy the above setup as much time as needed to have multiple
size options :

.. code:: ini

    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale4096]
    "MUIVerb"="rescale 4096"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale4096\command]
    @="cmd /k \"F:\\blog\\path\\to\\oiiotool-rescale.bat\" %1 4096"

    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale2048]
    "MUIVerb"="rescale 2048"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale2048\command]
    @="cmd /k \"F:\\blog\\path\\to\\oiiotool-rescale.bat\" %1 2048"

    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale1024]
    "MUIVerb"="rescale 1024"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiiorescale1024\command]
    @="cmd /k \"F:\\blog\\path\\to\\oiiotool-rescale.bat\" %1 1024"

    ...

.. note-info::

    As you know, using cmd will open a new command prompt every time, that you
    need to manually close. This can be annoying when processing dozens
    of textures. Actually nothing prevent you to directly start the .bat
    without the ``cmd /k``. You will just not be able to know if the the rescaling
    failed.

Converting images to .ico
_________________________

You saw that we needed to create ``.ico`` file to give pretty icon to our
context-menus, and it's annoying to go on some random website to convert your
images. Let's automatize it too !

As previously, in 2 part with a .bat :

.. code:: batch

    @echo off
    %OIIOTOOL% -v -i "%1" --resize 256x0 --dup --resize 128x0 --dup --resize 64x0 --dup --resize 48x0 --dup --resize 32x0 --dup --resize 24x0 --dup --resize 16x0 --siappendall -o "%~n1.ico"

.. code:: ini

    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiioicon]
    "MUIVerb"="convert to .ico"
    [HKEY_CURRENT_USER\Software\Classes\*\shell\OIIO_Tool\shell\oiioicon\command]
    @="cmd /k \"F:\\blog\\path\\to\\oiiotool-ico-convert.bat\" %1"

The only tricky part was to know the ico format store multiple versions of
the same image at different scales, but again OIIO make that pretty easy !

ABCInfo
=======

Next one : retrieving informations about an Alembic file without even opening
it in a DCC. We will be using a CLI called ``abcinfo.exe``. *This CLI can only
be found in Houdini installation* :

.. code:: text

    C:\Program Files\Side Effects Software\Houdini {VERSION}\bin\abcinfo.exe"

The tool is not standalone, meaning you can't just copy it somewhere. I
recommend to as always set an environement variable to it that you can easily
update when you update your Houdini version.

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\.abc\shell\abcinfo]
    "MUIVerb"="abcinfo"
    "icon"="C:\\Program Files\\Side Effects Software\\Houdini 18.5.499\\bin\\abcinfo.exe"
    "subCommands"=""

    [HKEY_CURRENT_USER\Software\Classes\.abc\shell\abcinfo\shell\001abcinfo]
    "MUIVerb"="abcinfo"
    [HKEY_CURRENT_USER\Software\Classes\.abc\shell\abcinfo\shell\001abcinfo\command]
    @="cmd /k %%ABCINFO%% \"%1\""

    [HKEY_CURRENT_USER\Software\Classes\.abc\shell\abcinfo\shell\002abcinfo_verbose]
    "MUIVerb"="abcinfo verbose"
    [HKEY_CURRENT_USER\Software\Classes\.abc\shell\abcinfo\shell\002abcinfo_verbose\command]
    @="cmd /k %%ABCINFO%% -v \"%1\""

This time no need to put it in ``Classes\*``, we only need it for ``.abc``. I
created 2 commands, one which give most of the time the info I need, another one
that really give the maximum of info about the file.

You can also notice that for the icon we gave a path to a .exe ! Windows will
use the icon packed in the .exe (if there is one).


Starting different version of the same DCC
==========================================

Maybe you are working on multiple projects at the same time, requiring different
software versions to be used. And you really would like to just double-click on
your file to launch it. Well with what we learned you coudl at leat create a
context-menu to open the selected file in the given DCC version.

Here is an example with Maya :

.. code:: ini

    Windows Registry Editor Version 5.00

    [HKEY_CURRENT_USER\Software\Classes\.ma\shell\mayaopen]
    "MUIVerb"="abcinfo"
    "icon"="C:\\Program Files\\Autodesk\\Maya2023\\bin\\maya.exe"
    "subCommands"=""

    [HKEY_CURRENT_USER\Software\Classes\.ma\shell\mayaopen\shell\maya2023]
    "MUIVerb"="Open in Maya 2023"
    [HKEY_CURRENT_USER\Software\Classes\.ma\shell\mayaopen\shell\maya2023\command]
    @="C:\\Program Files\\Autodesk\\Maya2023\\bin\\maya.exe -file \"%1\""

    [HKEY_CURRENT_USER\Software\Classes\.ma\shell\mayaopen\shell\maya2020]
    "MUIVerb"="Open in Maya 2020"
    [HKEY_CURRENT_USER\Software\Classes\.ma\shell\mayaopen\shell\maya2020\command]
    @="C:\\Program Files\\Autodesk\\Maya2020\\bin\\maya.exe -file \"%1\""

..

    Wait I see you are giving argument to Maya, this mean it's a CLI ?!

Yes it is ! For every .exe try to call ``myDCC.exe --help`` and see what are the
available options.

Nothing prevent you to instead of calling the .exe, you call a .bat that call
the .exe but set a bunch of environement variable before, ... There is plenty
of cool workflow optimization you could perform with customized context menus !