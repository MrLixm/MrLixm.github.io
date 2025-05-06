from lxmsite import read_image_meta_file

file1 = (
    "__format__: 1\n"
    "date-shot: 2024-12\n"
    "location:France\n"
    "caption: A narrow passage stuck between\n"
    "  building. You think it could looks\n"
    "  creepy at this time of the night.\n"
)

file2 = (
    "__format__: 1\n"
    "caption: A narrow passage\n"
    " \n"
    "   Stuck between building.\n"
    "\n"
    "  Lost in space\n"
    "\n"
    "  And time."
)


def test__read_image_meta_file__file1(tmp_path):

    file1path = tmp_path / "image1.jpg.meta"
    file1path.write_text(file1)

    metadata = read_image_meta_file(file1path)
    assert metadata["location"] == "France"
    assert metadata["date-shot"] == "2024-12"
    assert (
        metadata["caption"]
        == "A narrow passage stuck between building. You think it could looks creepy at this time of the night."
    )


def test__read_image_meta_file__file2(tmp_path):

    file2path = tmp_path / "image2.jpg.meta"
    file2path.write_text(file2)

    metadata = read_image_meta_file(file2path)
    assert (
        metadata["caption"]
        == "A narrow passage\nStuck between building.\nLost in space\nAnd time."
    )
