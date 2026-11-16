"""Axis-aligned rectangle overlap. Rectangles are (x, y, w, h) with (x, y) the bottom-left."""


def overlaps(ax, ay, aw, ah, bx, by, bw, bh):
    """True if the two rectangles overlap. Touching edges do not count.

    Same arithmetic as v1's Rect.colliderect, so results match it bit for bit.
    """
    max_h = max(abs(ax + aw - bx), abs(ax - (bx + bw)))
    max_v = max(abs(ay - (by + bh)), abs(ay + ah - by))
    return max_h < aw + bw and max_v < ah + bh
