from src.utils import python_code_content


def test_python_code_content():
    ui_frame = python_code_content("../test/unit/utils_test.py")
    print((ui_frame[0]).text_xl.content)
    assert ui_frame[0].text_xl.content == "Application Code"
