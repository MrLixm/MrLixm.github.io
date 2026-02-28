# Winchester 1873

:image: render.jpg
:date-created: 2019-02-20T21:11
:description: Winchester 1873 full aspect cg shot for a school assignment.
:software: Maya,Arnold,Mari,Blender,EEVEE,After-Effects,Nuke,Megascans

<div id="post-description" markdown="1">
Winchester 1873 cg model, reponsible for all aspects.

School project I'm making since November 2018.

- modeling: Maya, subd and quad-only
- texturing: Mari, metalness workflow with textures from megascans, Substance Source, and other textures packs.
- rendering: Blender EEVEE for the animations, Arnold for static shots.
- post-processing: AfterEffect (EEVEE renders), Nuke (arnold shots)

I used Blender's EEVEE due to the short time I had. I wanted to make a quick animation to showcase the texturing work, but I only had one weekend.
Hence, me ending up picking EEVEE which speedup render times but also the lookdev process.

Some of my first renders with the ACES workflow.

Huge thanks to the Wizix discord community for the feedback.
</div>

<section id="post-main">
<figure>
    <img src="render.jpg" alt="A staged shot of the historicly famous Winchester gun. There's 2 model placed on a wooden floor, amongst some bullet casing.">
    <figcaption>key-art (Arnold + Nuke)(this is actually an improved version I did 2 years later)</figcaption>
</figure>
<figure>
  <video muted loop autoplay controls>
    <source src="anim.mp4" type="video/mp4">
  </video>
  <figcaption>Animation (EEVEE)</figcaption>
</figure>
<figure>
  <video muted loop autoplay controls>
    <source src="anim.close.mp4" type="video/mp4">
  </video>
  <figcaption>Animation (EEVEE)</figcaption>
</figure>
<figure>
    <img src="render.close.jpg" alt="A close up of the gun barrel where we can notice all the details on the wood like scracthes and smudges.">
    <figcaption>Close-up render (Arnold + Nuke)</figcaption>
</figure>
<figure>
    <img src="breakdown.textures.jpg" alt="A screenshot of the Mari interface with the image-manager and 2 screenshots of the model edge-wear mask and a rust mask.">
    <figcaption>Some of the textures and mask used in Mari.</figcaption>
</figure>
<figure>
    <img src="viewport.mari.1.jpg" alt="A screenshot of the winchester model fully shaded in the Mari viewport.">
    <figcaption>The model in the Mari viewport with full shading.</figcaption>
</figure>
<figure>
    <img src="viewport.mari.2.jpg" alt="A screenshot of the winchester model fully shaded in the Mari viewport.">
    <figcaption>The model in the Mari viewport with full shading.</figcaption>
</figure>
<figure>
    <img src="wireframe.jpg" alt="A screenshot of the Maya viewport of the model with the wireframe visible.">
    <figcaption>The model wireframe in Maya.</figcaption>
</figure>
<figure>
    <img src="viewport.eevee.jpg" alt="A screenshot of the Blender viewport with all the light and camera visibles.">
    <figcaption>The animated scene EEVEE viewport (~25fps with a GTX1080).</figcaption>
</figure>
<figure>
    <img src="comparison.aces.gif" alt="A comparison between 2 render of the model, one using the traditional sRGB workflow that looks harsher, and the other teh ACES workflow where highlights looks softer.">
    <figcaption>ACES / sRGB comparison where clipped/overexposed values are visible on the sRGB version.</figcaption>
</figure>
<figure>
    <img src="test.jpg" alt="A different variant of the key-art render that was warmer and less polished.">
    <figcaption>EEVEE composition test for the key render.</figcaption>
</figure>
</section>
