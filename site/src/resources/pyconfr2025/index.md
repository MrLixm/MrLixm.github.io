# PyConFR 2025

:description: Ma participation à la Python Convention FR 2025 (in french).
:date-created: 2025-10-30T14:47
:image: pycon-logo.svg
:authors: Liam Collod
:category: learning
:tags: programming, python, web-dev
:language: fr

Du 30 octobe au 2 novembre 2025 ce tenait la [PyConFR 2025](https://www.pycon.fr/2025/) à Lyon.
J'ai choisis d'y animer un atelier: *Créer un petit site web statique et plus avec Python et Jinja*.

.. url-preview:: https://www.pycon.fr/2025/fr/talks/workshop.html#talk-Y8B8QU
    :title: Créer un petit site web statique et plus avec Python et Jinja
    :image: pycon-logo.svg

    L'annonce sur le site de la PyCon

Juste après, vous retrouverez les supports de présentation:

.. url-preview:: https://www.tldraw.com/f/VRC0YZYlbfwPC1fx_iB5B
    :title: tldraw - Support de présentation intéractif
    :image: https://www.tldraw.com/social-twitter.png

Et voici les ressources additionelles. Merci à tout le monde d'etre venu et désolé pour 
le chaos technique, j'espere que ces quelques ressources vous permetrons d'explorer ca à
votre rythme.

Pour approndir comment un site web fonctionne je recommende vraiment la documentation
Mozilla qui est aussi traduite en francais !

- <https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works>

## Jinja

<https://jinja.palletsprojects.com/en/stable/>

Example de template html jinja:

```html
<html lang="en">
<head>
    <title>PyCon Demo</title>
</head>
<body>
    <h1>{{ PAGE_TITLE|escape }}</h1>
    <p>voici une liste d'images:</p>
    {% for img_path in IMGS %}
        <img src="{{ img_path }}">
    {% endfor %}
</body>
</html>
```

Example de recette de build de template:

```python
import jinja2

from pathlib import Path

templates_root = Path("...")

imgs_root = templates_root / "imgs"
imgs = list(imgs_root.glob("*.jpg"))
# les urls HTML ne supported pas les path absolus, nous devons convertir en relatif
imgs = [img.relative_to(templates_root) for img in imgs]

jinja_env = jinja2.Environment(
    undefined=jinja2.StrictUndefined,
    loader=jinja2.FileSystemLoader(templates_root),
)

template = jinja_env.get_template("template_name...")

attributes = {
    # mapping de variables globale propagees dans le template
    # mettez ce que vous voulez
    "PAGE_TITLE": "PyCon démo",
    "IMGS": imgs,
}

# 'content' est une str qu'il faut ensuite sauvegarder sur disque
content: str = template.render(**attributes)

# reste la logique de comment ecrire l'html et lancer le serveur ...
```

## Markdown vers HTML

*Partie qu'on a pas eu le temps de voir*

En utilisant <https://python-markdown.github.io/>

```python
from pathlib import Path
import markdown

# voir la doc pour les settings dispo
settings = {}

markdown_file_path = Path("...")
markdown_content = markdown_file_path.read_text("utf-8")

html = markdown.markdown(
    markdown_content,
    # regardez dans la doc quel extensions sont necessaire pour vous,
    # les extensions permettent de rajouter de nouvelle facon d'ecrire
    # du markdown et sont vraiment pratiques.
    extensions=[
        # builtins.extra
        "abbr",
        "attr_list",
        "def_list",
        "fenced_code",
        "footnotes",
        "md_in_html",
        "tables",
        # builtins
        "admonition",
        "toc",
        ],
    extension_configs=settings,
    output_format="xhtml",
    tab_length=4,
)
```

## Heberger son site

- <https://docs.github.com/en/pages>
    - gratuit pas vraiment de limitation
    - soucis ethique: GitHub est gerer par Microsoft et il n'hesistent pas a entrainer 
      leur IA sur le contenu hebergé sur GitHub.
- <https://codeberg.page/>
    - comme GitHub CodeBerg est une platforme plus ethique
    - marqué comme experimentale sur leur site
- <https://neocities.org/>
    - Assez connu, inlus aussi un editeur HTML en ligne.
    - necessaire de apyer pour mettre un nom de domaine personalisé

Alternative queer (https://eldritch.cafe/@zorume/115247647232654326):

- <https://besties.house/> qui gère:
  - <https://pages.gay/> pour les sites
  - et <https://git.gay/> comme forge git

Et pour faire du "self-host" c'est aussi possible de louer un ordinateur, appelé VPS
et d'utiliser [YunoHost](https://yunohost.org/) pour gerer le systeme. YunoHost rend le processus 
beaucoup moins technique.

- Pour trouver un VPS: <https://european-alternatives.eu/category/vps-virtual-private-server-hosters>
- L'app YunoHost a installer pour gerer un site web: <https://apps.yunohost.org/app/my_webapp>
