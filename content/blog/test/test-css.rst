Testing the CSS for this blog
#############################

:summary: I'm a summary for this article, trying to be as long as possible
    just for testing purposes.

:status: draft
:date-created: 2021-11-24 23:13
:date:  2021-11-24 23:13

:category: tutorial
:tags: mari, color-science, OCIO, ACES
:author: Liam Collod

.. role:: text-green
    :class: m-text m-primary

index
regius torquis cito convertams resistentia est. gemnas sunt spatiis de peritus assimilatio.
cum aonides peregrinatione, omnes nuclear vexatum iacerees examinare clemens, teres calcariaes.
nunquam convertam lacta.

.. block-info:: Demissios trabem!

    https://substance3d.adobe.com/documentation/spdoc/color-management-223053233.html

.. contents::

regius torquis cito convertams resistentia est. gemnas sunt spatiis de peritus assimilatio.

.. block-info:: Demissios trabem!

   a falsis, urbs brevis deus.

Heading H2
----------

regius torquis cito convertams resistentia est. gemnas sunt spatiis de peritus assimilatio.
cum aonides peregrinatione, omnes nuclear vexatum iacerees examinare clemens, teres calcariaes.

Heading H3
==========

regius torquis cito convertams resistentia est. gemnas sunt spatiis de peritus assimilatio.
cum aonides peregrinatione, omnes nuclear vexatum iacerees examinare clemens, teres calcariaes.

Heading H4
__________

regius torquis cito convertams resistentia est. gemnas sunt spatiis de peritus assimilatio.
cum aonides peregrinatione, omnes nuclear vexatum iacerees examinare clemens, teres calcariaes.

Heading H5
""""""""""

regius torquis cito convertams resistentia est. gemnas sunt spatiis de peritus assimilatio.
cum aonides peregrinatione, omnes nuclear vexatum iacerees examinare clemens, teres calcariaes.

Formatting
----------

*Sunt rationees experientia grandis, gratis vigiles.*

**Sunt rationees experientia grandis, gratis vigiles.**

``Sunt rationees experientia grandis, gratis vigiles.``

:abbr:`*Sunt rationees <experientia grandis, gratis vigiles.>*`

https://mrlixm.github.io/

`Link to my super website hehe <https://mrlixm.github.io/>`_

| This is teh first Line.
| This is teh second line.
 THis is still the second line.

1.
    First Line

2.
    Second one

3.
    Third one

-
    We do it again

-
    Second line

-
    Third line

Components
-----------

Notes
=====

cum humani generis cadunt, omnes brabeutaes carpseris camerarius, salvus mortemes.
agripetas ortum.

.. note-default::

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.

    - audax, altus nomens tandem reperire de varius, primus caesium.

.. note-info::

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.

    - audax, altus nomens tandem reperire de varius, primus caesium.

.. note-warning::

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.

    - audax, altus nomens tandem reperire de varius, primus caesium.

.. note-danger::

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.

    - audax, altus nomens tandem reperire de varius, primus caesium.

.. note-success::

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.

    - audax, altus nomens tandem reperire de varius, primus caesium.

Blocks
======

.. block-default:: Demissios trabem!

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.
    audax, altus nomens tandem reperire de varius, primus caesium.

.. block-info:: Demissios trabem!

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.
    audax, altus nomens tandem reperire de varius, primus caesium.

.. block-warning:: Demissios trabem!

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.
    audax, altus nomens tandem reperire de varius, primus caesium.

.. block-danger:: Demissios trabem!

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.
    audax, altus nomens tandem reperire de varius, primus caesium.

.. block-success:: Demissios trabem!

    cur itineris tramitem ire? neuter, teres finiss grauiter amor de magnum,
    primus nomen.
    audax, altus nomens tandem reperire de varius, primus caesium.

Misc ?
======

cum hippotoxota mori, omnes burguses perdere salvus, pius accolaes.
sunt genetrixes reperire rusticus, clemens bullaes. resistere unus ducunt ad grandis luba.
fluctuis observare.

    the aspect has sainthood, but not everyone understands it.
    be mediocre for whoever exists, because each has been studied with intuition.
    be secret.

superbus, pius exsuls absolute anhelare de noster, emeritis guttus.
resistere vix ducunt ad barbatus byssus. castus fermium unus locuss abactus est.
sensorems favere.

    cum hippotoxota mori, omnes burguses perdere salvus, pius accolaes.
    sunt genetrixes reperire rusticus, clemens bullaes. resistere unus ducunt ad grandis luba.
    fluctuis observare.

    -
        mighty, black hornpipes unlawfully mark a salty, dead landlubber.
        the parrot ransacks with yellow fever, vandalize the fortress before it sings.

    -
        salty, old jacks oppressively haul a fine, jolly shark.
        the wind hoists with halitosis, endure the bahamas before it rises.

    -
        weird, stormy krakens fast ransack a coal-black, salty parrot.
        the plunder pulls with punishment, endure the bikini atoll until it dies.

    cum detrius favere, omnes galluses magicae grandis, castus lunaes.

Code-blocks
===========


.. code:: shell

    set "OCIO=C:\aces_1.1\config.ocio"

    start "" "C:\Program Files\Allegorithmic\Adobe Substance 3D Painter\Adobe
    Substance 3D Painter.exe"

.. code:: python

    def publish(commit_name: str):

        infofile = InfoFile()

        args = [
            r"C:\Program Files\Git\bin\sh.exe",
            "_git-publish-noprompt.sh",
            f"{commit_name}",
            f"{infofile.version}"
        ]

        # update the info.json before any commits (not good if error happen)
        infofile.write_last_published()
        infofile.increment_version()

        process = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        print(f"[publish][_git-publish-noprompt.sh] stdout:\n    {process.stdout.decode('utf-8')}")

        if process.stderr:
            raise RuntimeError(
                f"Error while executing <_git-publish-noprompt.sh>:\n{process.stderr.decode('utf-8')}"
            )

        return

    if __name__ == '__main__':
        run()

Produced wih the include directive

.. include:: tests_include.lua
    :code: lua


Fake-test-section
-----------------

Ubi est alter accola?
=====================

.. image:: {static}/images/blog/0008/sp-odt-default.png
    :target: {static}/images/blog/0008/sp-odt-default.png
    :alt: Lubas messis.

Acipensers favere in regius avenio! Cum byssus resistere, omnes cottaes magicae grandis, raptus apolloniateses.
cum itineris tramitem accelerare, **omnes tabeses captis** fortis, brevis
boreases.
Mori ``solite`` ducunt ad talis lacta. Rusticus epos callide tractares solitudo est.
Sunt hippotoxotaes captis clemens, placidus uriaes. Talis gallus mechanice contactuss diatria est.
gluten.

The dark cockroach begrudgingly hails the mate.  :text-green:`malfunction
pedantically like a distant ferengi. the teleporter is proudly twisted.`
The ship-wide captain wildly attacks the particle.
Tragedy at the cosmos that is when carnivorous spacecrafts fly.

Liberis messis! Cum gabalium congregabo, omnes bromiumes captis peritus, alter liberies?

    A falsis, verpa salvus decor. Alter, regius compaters semper dignus de altus, audax finis.

.. _axona, solitudo bromium:

Cum coordinatae potus, omnes fugaes manifestum placidus, alter adgiumes?

    Cur ignigena nocere? Castus, placidus fortiss superbe imperium de regius, secundus amicitia.
    Barbatus, salvus armariums recte amor de gratis, fatalis valebat.
    Cum historia tolerare, omnes eleateses examinare altus, domesticus nutrixes.
    Sunt axonaes quaestio germanus, superbus plasmatores.
    :abbr:`Apolloniates <caesium, et agripeta.>`
    salvus era recte tractares omnia est. secundus impositio interdum visums sectam est.
    Teres, alter mortems aegre attrahendam de altus, fortis vortex.
    `BT.1886 <https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1886-0-201103-I!!PDF-E.pdf>`_
    superbus, domesticus zetas inciviliter imitari de fortis, varius gluten.
    nunquam magicae luna.
    Pol, domesticus elevatus! Planeta de albus tata, attrahendam turpis! Medicina de rusticus palus, gratia uria!
    Homos peregrinatione in dexter lutetia! *Dexter, regius seculas
    sapienter experientia de noster, nobilis cursus.*
    Est raptus tus, cesaris.

    Hercle, fortis lotus!, albus orgia! Cum lanista volare, omnes verpaes
    transferre flavum, nobilis lubaes.
    Barbatus, placidus lubas solite convertam de magnum, raptus bubo.

Ubi est mirabilis finis? Peritus, grandis zirbuss sed mire quaestio de bassus, audax historia!

    Velox accolas ducunt ad clabulare. Gratis candidatus foris dignuss gemna est.
    Salvus, barbatus rumors superbe fallere de primus, bi-color habena.
    Cum boreas peregrinatione, omnes orgiaes perdere camerarius, brevis eposes.
    Caesiums trabem, tanquam barbatus valebat.
    Credere ``inciviliter`` ducunt ad alter rumor. Vortex de altus elevatus,
    quaestio mens!
    Ecce, demissio! Menss potus in ``albus`` asopus! Festus, barbatus nuclear
    vexatum iaceres hic quaestio de clemens, camerarius medicina.
    demolitiones velum.

Cum rector prarere, omnes tumultumquees manifestum talis, bi-color gemnaes.
Ignigenas unda in neuter chremisa! Mineralis de grandis devatio, examinare glos!
Secundus, teres onuss hic talem de camerarius, gratis lacta.
ostravia.

.. note-info::

    cur itineris tramitem ire? ``neuter``, teres finiss grauiter amor de magnum,
    primus nomen.
    ``audax``, ``altus`` nomens tandem reperire de varius, primus caesium.

Cum rector prarere, omnes tumultumquees manifestum talis, bi-color gemnaes.
Ignigenas unda **in neuter chremisa!** Mineralis de grandis devatio, examinare
glos!
Secundus, teres onuss hic talem de ``camerarius``, gratis lacta.
ostravia.

.. image:: {static}/images/blog/0005/intro.png
    :alt: instancing principle

.. block-warning:: Demissios trabem!

    cum mons velum, omnes accentores acquirere ferox, castus ignigenaes,

    - camerarius, varius tuss absolute promissio de dexter, alter domus,
    - emeritis, rusticus vortexs aliquando acquirere de pius, peritus luna,

Cum hibrida mori, omnes victrixes acquirere germanus, ferox rationees.
Cum fiscina unda, omnes luraes magicae brevis, teres torquises.
Cum lactea observare, omnes galluses fallere gratis, bassus zirbuses.
eleates.

.. raw:: html

    <script src="https://emgithub.com/embed.js?target=https%3A%2F%2Fgithub.com%2FMrLixm%2FFoundry_Katana%2Fblob%2Fmain%2Fsrc%2Fnodegraph%2FCreateGSV%2FCreateGSV.py&style=atom-one-dark&showBorder=on&showLineNumbers=on&showFileMeta=on&showCopy=on&fetchFromJsDelivr=on"></script>

The above should be an embed GitHub file using emgithub. It should have the
dark atom-one-dark theme.

Custom Directives
-----------------

url-preview
===========

Some text above

.. url-preview:: https:\\google.com
    :title: Lazy Brown grey fox !

    test for **content** that should be a description

Some text in between
Cum hibrida mori, omnes victrixes acquirere germanus, ferox rationees.
Cum fiscina unda, omnes luraes magicae brevis, teres torquises.

.. url-preview:: https:\\google.com
    :title: Lazy Brown grey fox !
    :image: {static}/images/blog/0002/cover.png

    test for **content** that should be a description

And some text under
Cum hibrida mori, omnes victrixes acquirere germanus, ferox rationees.
Cum fiscina unda, omnes luraes magicae brevis, teres torquises.


.. url-preview:: https://mega.nz/folder/uooQzJJR#5aguo_c3gLXPrkEnN62ZBg
    :title: Sources Files Download
    :svg: {static}/images/global/icons/mega.svg
    :color: rgb(254, 71, 65)

Dexter, altus orexiss rare imitari de grandis, secundus plasmator.
Cum exsul favere, omnes aususes convertam grandis, albus fortises.

.. url-preview:: https://discord.gg/jk6u3eB
    :title: Digital Imaging | Discord Server
    :svg: {static}/images/global/icons/discord.svg
    :svg-size: 60

    A Discord server centered around digital imaging - from CGI to digital
    cinematography and photography and more.

Dexter, altus orexiss rare imitari de grandis, secundus plasmator.
Cum exsul favere, omnes aususes convertam grandis, albus fortises.
