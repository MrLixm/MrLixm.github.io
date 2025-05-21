from pathlib import Path

import lxmsite


def mkdir(root: Path, dirname: str):
    path = root / dirname
    path.mkdir()
    return path


def mkfile(root: Path, filename: str, content=""):
    path = root / filename
    path.write_text(content)
    return path


def test__read_siteignore(tmp_path):
    file1 = mkfile(tmp_path, "file1.txt")
    file1md = mkfile(tmp_path, "file1.md")
    file2 = mkfile(tmp_path, "file2.txt")

    dir_foo = mkdir(tmp_path, "foo")
    file_foo_1 = mkfile(dir_foo, "file_foo_1.txt")
    file_foo_2 = mkfile(dir_foo, "file_foo_2.txt")

    dir_bar = mkdir(tmp_path, "bar")
    dir_barachat = mkdir(dir_bar, "barachat")
    file_barachat_1 = mkfile(dir_barachat, "file_barachat_1.txt")
    file_barachat_2 = mkfile(dir_barachat, "file_barachat_2.md")

    dir_feur = mkdir(tmp_path, "feur")

    sitignore_path = tmp_path / ".siteignore"
    sitignore_content = "file1.*\nfoo/*\nbar/**/*.txt\nfeur/"
    sitignore_path.write_text(sitignore_content)

    ignored = lxmsite.read_siteignore(sitignore_path)
    assert file1 in ignored
    assert file1md in ignored
    assert file2 not in ignored
    assert dir_foo not in ignored
    assert file_foo_1 in ignored
    assert file_foo_2 in ignored
    assert dir_bar not in ignored
    assert dir_barachat not in ignored
    assert file_barachat_1 in ignored
    assert file_barachat_2 not in ignored
    assert dir_feur in ignored
    assert len(ignored) == 6


def test__collect_site_files(tmp_path):

    file1 = mkfile(tmp_path, "file1.txt")
    file1md = mkfile(tmp_path, "file1.md")
    file2 = mkfile(tmp_path, "file2.txt")

    dir_foo = mkdir(tmp_path, "foo")
    file_foo_1 = mkfile(dir_foo, "file_foo_1.txt")
    file_foo_2 = mkfile(dir_foo, "file_foo_2.txt")

    dir_bar = mkdir(tmp_path, "bar")
    file_bar_1 = mkfile(dir_bar, "file_bar_1.txt")
    dir_barachat = mkdir(dir_bar, "barachat")
    file_barachat_1 = mkfile(dir_barachat, "file_barachat_1.txt")
    file_barachat_2 = mkfile(dir_barachat, "file_barachat_2.md")

    dir_feur = mkdir(tmp_path, "feur")

    sitignore_path1 = mkfile(tmp_path, ".siteignore", "file1.*\nfoo/*")
    sitignore_path2 = mkfile(dir_bar, ".siteignore", "**/*.md")

    collected = lxmsite.collect_site_files(tmp_path)
    assert file1 not in collected
    assert file1md not in collected
    assert file2 in collected
    assert dir_foo not in collected
    assert file_foo_1 not in collected
    assert file_foo_2 not in collected
    assert dir_bar not in collected
    assert file_bar_1 in collected
    assert dir_barachat not in collected
    assert file_barachat_1 in collected
    assert file_barachat_2 not in collected
    assert dir_feur not in collected
    assert sitignore_path1 not in collected
    assert sitignore_path2 not in collected
    assert len(collected) == 3


def test__collect_shelves(tmp_path):

    file1 = mkfile(tmp_path, "abc.txt")
    file2 = mkfile(tmp_path, "file2.rst")
    file3 = mkfile(tmp_path, "image.jpg")

    dir_blog = mkdir(tmp_path, "blog")
    shelf_blog = mkfile(dir_blog, ".shelf", 'default_template: "blog.html"')
    file_blog_2 = mkfile(dir_blog, "post2.rst")
    file_blog_3 = mkfile(dir_blog, "image.jpg")

    dir_blog_post1 = mkdir(dir_blog, "post1")
    sitignore_post1 = mkfile(dir_blog_post1, ".siteignore", "block.html")
    file_blog_post1 = mkfile(dir_blog_post1, "index.rst")
    file_blog_post2 = mkfile(dir_blog_post1, "block.html")

    collected = lxmsite.collect_site_files(tmp_path)
    parsed = lxmsite.collect_shelves(collected)

    assert len(parsed) == 1
    assert shelf_blog in parsed
    assert len(parsed[shelf_blog]) == 3


def test__MetaFileCollection(tmp_path):
    file_meta = mkfile(
        tmp_path, ".meta.json", '{"styles": ["main.css", "foo.css"], "label":"coco"}'
    )
    file_html = mkfile(tmp_path, "file.html")
    dir_qwert = mkdir(tmp_path, "qwert")
    file_qwert_meta = mkfile(
        dir_qwert, ".meta.json", '{"styles": ["qwert.css"], "label":"azertyuiop"}'
    )
    file_qwert_html = mkfile(dir_qwert, "file.html")
    dir_qwert_banana = mkdir(dir_qwert, "banana")
    file_qwert_banana_meta = mkfile(
        dir_qwert_banana, ".meta.json", '{"styles": ["banana.css"], "author":"Sauron"}'
    )
    file_qwert_banana_html = mkfile(dir_qwert_banana, "somefile.html")

    site_files = lxmsite.collect_site_files(tmp_path)
    meta_collection = lxmsite.collect_meta_files(site_files)
    assert len(meta_collection.meta_files) == 3
    result = meta_collection.get_path_meta(file_qwert_banana_html, "@")
    assert result["styles"] == "@".join(
        ["main.css", "foo.css", "qwert.css", "banana.css"]
    )
    assert result["author"] == "Sauron"
    assert result["label"] == "azertyuiop"


def test__MetaFileCollection__list_to_str(tmp_path):
    # test conversion from str to list in meta fields
    file_meta = mkfile(tmp_path, ".meta.json", '{"styles": "main.css", "label":"coco"}')
    dir_qwert = mkdir(tmp_path, "qwert")
    file_qwert_meta = mkfile(
        dir_qwert, ".meta.json", '{"styles": ["qwert.css"], "label":"azertyuiop"}'
    )
    dir_qwert_banana = mkdir(dir_qwert, "banana")
    file_qwert_banana_meta = mkfile(
        dir_qwert_banana, ".meta.json", '{"styles": ["banana.css"], "author":"Sauron"}'
    )
    file_qwert_banana_html = mkfile(dir_qwert_banana, "somefile.html")

    dir_qwert_coco = mkdir(dir_qwert, "coco")
    file_qwert_coco_meta = mkfile(
        dir_qwert_coco, ".meta.json", '{"styles": "coco.css", "author":"Galadriel"}'
    )
    file_qwert_coco_html = mkfile(dir_qwert_coco, "somefile.html")

    site_files = lxmsite.collect_site_files(tmp_path)
    meta_collection = lxmsite.collect_meta_files(site_files)
    assert len(meta_collection.meta_files) == 4

    result = meta_collection.get_path_meta(file_qwert_banana_html)
    assert result["styles"] == ",".join(["main.css", "qwert.css", "banana.css"])
    assert result["author"] == "Sauron"
    assert result["label"] == "azertyuiop"

    result = meta_collection.get_path_meta(file_qwert_coco_html)
    assert result["styles"] == "coco.css"
    assert result["author"] == "Galadriel"
    assert result["label"] == "azertyuiop"
