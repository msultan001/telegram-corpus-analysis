from scripts.load_detections import extract_message_id_from_path


def test_extract():
    path1 = r"data\\raw\\images\\1569871437\\1569871437_187733.jpg"
    assert extract_message_id_from_path(path1) == 187733

    path2 = r"/some/path/999_42.png"
    assert extract_message_id_from_path(path2) == 42

    path3 = r"badname.jpg"
    assert extract_message_id_from_path(path3) is None


if __name__ == '__main__':
    test_extract()
    print('tests passed')
