from Backend.misc.helperFunctions import make_progress_bar_text


def test_make_progress_bar_text():
    assert make_progress_bar_text(0, bar_length=2) == "AA"
    assert make_progress_bar_text(0.1, bar_length=2) == "AA"
    assert make_progress_bar_text(0.2, bar_length=2) == "CA"
    assert make_progress_bar_text(0.3, bar_length=2) == "DA"
    assert make_progress_bar_text(0.4, bar_length=2) == "EA"
    assert make_progress_bar_text(0.5, bar_length=2) == "FB"
    assert make_progress_bar_text(0.6, bar_length=2) == "FB"
    assert make_progress_bar_text(0.7, bar_length=2) == "FC"
    assert make_progress_bar_text(0.8, bar_length=2) == "FD"
    assert make_progress_bar_text(0.9, bar_length=2) == "FE"
    assert make_progress_bar_text(1, bar_length=2) == "FF"
