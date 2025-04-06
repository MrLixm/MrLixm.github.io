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


def test_read_siteignore(tmp_path):
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


def test_collect_site_files(tmp_path):

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


def test_parse_site_files(tmp_path):

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
    parsed = lxmsite.parse_site_files(collected)

    assert len(parsed) == 4
    shelf = parsed[0]
    assert isinstance(shelf, lxmsite.ShelfResource)
    assert len(shelf.children) == 3
