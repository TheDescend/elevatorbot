from __future__ import annotations


def make_progress_bar_text(percentage: float, bar_length: int = 2) -> str:
    """
    Get the progress bar used by seasonal challenges and catalysts and more

    Translations:
        "A" -> Empty Emoji
        "B" -> Empty Emoji with edge
        "C" -> 1 Quarter Full Emoji
        "D" -> 2 Quarter Full Emoji
        "E" -> 3 Quarter Full Emoji
        "F" -> 4 Quarter Full Emoji
    """

    to_beat = 1 / bar_length / 4

    bar_text = ""
    for i in range(bar_length):
        # 100%
        if percentage >= (x := (to_beat * 4)):
            bar_text += "F"
            percentage -= x
        # 75%
        elif percentage >= (x := (to_beat * 3)):
            bar_text += "E"
            percentage -= x
        # 50%
        elif percentage >= (x := (to_beat * 2)):
            bar_text += "D"
            percentage -= x
        # 25%
        elif percentage >= (x := (to_beat * 1)):
            bar_text += "C"
            percentage -= x
        # 0%
        else:
            # if it's the first one or the last one was empty too, set it to completely empty
            if bar_text == "" or bar_text[-1:] != "F":
                bar_text += "A"
            # else keep the tiny edge
            else:
                bar_text += "B"

    return bar_text
