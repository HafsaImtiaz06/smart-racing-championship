"""A tiny stand-in for pygame, used ONLY when real pygame is not installed (for example on a build server).
It records drawing calls and rejects obviously wrong arguments, so most coding mistakes still show up in the tests.
On your own machine the tests use real pygame with a hidden window (SDL dummy video driver)."""
import sys
import types
from types import SimpleNamespace

CALLS = []


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _point(p):
    return isinstance(p, (tuple, list)) and len(p) == 2 and all(_num(c) for c in p)


def _color(c):
    return isinstance(c, (tuple, list)) and len(c) in (3, 4) and all(isinstance(v, int) and 0 <= v <= 255 for v in c)


class Surface:
    def __init__(self, size):
        self.size = tuple(size)

    def get_size(self):
        return self.size

    def get_width(self):
        return self.size[0]

    def get_height(self):
        return self.size[1]

    def fill(self, color):
        assert _color(color), color
        CALLS.append("fill")

    def blit(self, img, pos):
        assert isinstance(img, Surface) and _point(pos), (img, pos)
        CALLS.append("blit")


def _line(surface, color, start, end, width=1):
    assert isinstance(surface, Surface) and _color(color) and _point(start) and _point(end) and _num(width)
    CALLS.append("line")


def _lines(surface, color, closed, points, width=1):
    assert isinstance(surface, Surface) and _color(color) and len(points) >= 2 and all(_point(p) for p in points)
    CALLS.append("lines")


def _circle(surface, color, center, radius, width=0):
    assert isinstance(surface, Surface) and _color(color) and _point(center) and _num(radius) and radius >= 0
    CALLS.append("circle")


def _rect(surface, color, rect, width=0):
    assert isinstance(surface, Surface) and _color(color) and len(rect) == 4 and all(_num(v) for v in rect)
    CALLS.append("rect")


def _polygon(surface, color, points, width=0):
    assert isinstance(surface, Surface) and _color(color) and len(points) >= 3 and all(_point(p) for p in points)
    CALLS.append("polygon")


class Font:
    def __init__(self, name, size):
        assert name is None and _num(size)
        self.size = size

    def render(self, text, antialias, color):
        assert isinstance(text, str) and _color(color)
        return Surface((7 * len(text), self.size))

    def get_height(self):
        return self.size


_font_state = {"init": False}


def install():
    m = types.ModuleType("pygame")
    m.Surface = Surface
    m.draw = SimpleNamespace(line=_line, lines=_lines, circle=_circle, rect=_rect, polygon=_polygon)
    m.font = SimpleNamespace(init=lambda: _font_state.update(init=True), get_init=lambda: _font_state["init"], Font=Font)
    m.event = SimpleNamespace(Event=lambda t, **kw: SimpleNamespace(type=t, **kw))
    consts = {"QUIT": 256, "KEYDOWN": 768, "MOUSEBUTTONDOWN": 1025, "K_ESCAPE": 27, "K_SPACE": 32, "K_RETURN": 13,
              "K_BACKSPACE": 8, "K_RIGHT": 1073741903, "K_LEFT": 1073741904, "K_F1": 1073741882, "K_F2": 1073741883}
    for i, ch in enumerate("1234"):
        consts["K_" + ch] = 49 + i
    for ch in "acdeklnpqrx":
        consts["K_" + ch] = ord(ch)
    for k, v in consts.items():
        setattr(m, k, v)
    m.FAKE = True
    sys.modules["pygame"] = m
    return m
