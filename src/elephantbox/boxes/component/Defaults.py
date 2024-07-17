from __future__ import annotations

from elephantbox.support.Argumentable import kwarg_dict


def override(kwarg_dict: dict, **k) -> dict:
    ret = dict(kwarg_dict)
    ret.update(k)
    return ret


DEBUG_OBJ_KWARGS = kwarg_dict(
    fill="grey",
    stroke="blue",
    stroke_width=1,
    opacity="10%",
)

BODY_CUT_KWARGS = kwarg_dict(
    opacity="50%",
    fill="#aaaaff",
    stroke="black",
    stroke_width=2,
)

TAB_CUT_KWARGS = kwarg_dict(
    opacity="50%",
    fill="yellow",
    stroke="blue",
    stroke_width=2,
)

SLOT_CUT_KWARGS = kwarg_dict(
    opacity="50%",
    fill="lime",
    stroke="blue",
    stroke_width=2,
)


FOLD_PERFERATION_KWARGS = kwarg_dict(
    opacity="50%",
    stroke="red",
    stroke_width=2,
)


FINGER_CUTS_KWARGS = kwarg_dict(
    opacity="50%",
    fill="#aaffaa",
    stroke="black",
    stroke_width=2,
)
