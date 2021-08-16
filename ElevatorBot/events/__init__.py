from os import listdir
from os.path import dirname, basename


# Automatically import every class inside the events package. Magic! :D
__all__ = [
    basename(event_file)[:-3]
    for event_file in listdir(dirname(__file__))
    if event_file.endswith(".py") and not event_file == "__init__.py"
]
