import os
from engine.rt.image import Image


def test_something():
    img = Image.load(os.path.join(os.path.dirname(__file__), 'test.pnm'))

    assert img.width == 2
    assert img.height == 1
    assert img.meta == {
        'Author': 'pkubiak',
        'BackgroundColor': '#FF00FF',
    }
    