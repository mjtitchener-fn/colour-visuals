"""
Common Utilities
================

Define the common utilities objects that don't fall in any specific category.
"""

from __future__ import annotations

import re

import numpy as np
from colour.graph import convert
from colour.hints import (
    ArrayLike,
    DType,
    LiteralColourspaceModel,
    NDArray,
    Tuple,
    Type,
)
from colour.models import COLOURSPACE_MODELS_DOMAIN_RANGE_SCALE_1_TO_REFERENCE
from colour.utilities import full, optional

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "DEFAULT_FLOAT_DTYPE_WGPU",
    "DEFAULT_INT_DTYPE_WGPU",
    "NORMALISE_COLOURSPACE_MODEL",
    "XYZ_to_colourspace_model",
    "as_contiguous_array",
    "conform_primitive_dtype",
    "append_channel",
    "unlatexify",
]


DEFAULT_FLOAT_DTYPE_WGPU = np.float32
"""Default int number dtype."""

DEFAULT_INT_DTYPE_WGPU = np.uint32
"""Default floating point number dtype."""

NORMALISE_COLOURSPACE_MODEL: bool = True
"""Whether to normalize the colourspace models."""


def XYZ_to_colourspace_model(
    XYZ: ArrayLike,
    illuminant: ArrayLike,
    model: LiteralColourspaceModel | str = "CIE xyY",
    normalise_model: bool | None = None,
    **kwargs,
) -> NDArray:
    """
    Convert from *CIE XYZ* tristimulus values to given colourspace model while
    normalising some of the absolute models.

    Parameters
    ----------
    XYZ
        *CIE XYZ* tristimulus values to convert to  given colourspace model.
    illuminant
        Reference *illuminant* *CIE xy* chromaticity coordinates or *CIE xyY*
        colourspace array.
    model
        Colourspace model, see :attr:`colour.COLOURSPACE_MODELS` attribute for
        the list of supported colourspace models.
    normalise_model
        Whether to normalise colourspace models such as :math:`IC_TC_P` and
        :math:`J_za_zb_z`.

    Other Parameters
    ----------------
    kwargs
        See the documentation of the supported conversion definitions.

    Returns
    -------
    Any
        Converted *CIE XYZ* tristimulus values.
    """

    ijk = convert(
        XYZ,
        "CIE XYZ",
        model,
        illuminant=illuminant,
        **kwargs,
    )

    if not optional(normalise_model, NORMALISE_COLOURSPACE_MODEL):
        ijk = np.nan_to_num(ijk)
        ijk *= COLOURSPACE_MODELS_DOMAIN_RANGE_SCALE_1_TO_REFERENCE[model]

    return ijk


def as_contiguous_array(
    a: NDArray, dtype: Type[DType] = DEFAULT_FLOAT_DTYPE_WGPU
) -> NDArray:
    """
    Convert given array to a contiguous array (ndim >= 1) in memory (C order).

    Parameters
    ----------
    a
        Variable :math:`a` to convert.
    dtype
        :class:`numpy.dtype` to use for conversion, default to the
        :class:`numpy.dtype` defined by the
        :attr:`colour.constant.DEFAULT_FLOAT_DTYPE_WGPU` attribute.

    Returns
    -------
    :class:`numpy.ndarray`
        Converted variable :math:`a`.
    """

    return np.ascontiguousarray(a.astype(dtype))


def conform_primitive_dtype(
    primitive: Tuple[NDArray, NDArray, NDArray],
) -> Tuple[NDArray, NDArray, NDArray]:
    """
    Conform the given primitive to the required *WebGPU* dtype.

    Parameters
    ----------
    primitive
        Primitive to conform the dtype of.

    Returns
    -------
    :class:`numpy.ndarray`
        Conformed primitive.
    """

    vertices, faces, outline = primitive

    return (
        vertices.astype(
            [
                ("position", DEFAULT_FLOAT_DTYPE_WGPU, (3,)),
                ("uv", DEFAULT_FLOAT_DTYPE_WGPU, (2,)),
                ("normal", DEFAULT_FLOAT_DTYPE_WGPU, (3,)),
                ("colour", DEFAULT_FLOAT_DTYPE_WGPU, (4,)),
            ]
        ),
        faces.astype(DEFAULT_INT_DTYPE_WGPU),
        outline.astype(DEFAULT_INT_DTYPE_WGPU),
    )


def append_channel(a: ArrayLike, value: float = 1) -> NDArray:
    """
    Append a channel to given variable :math:`a`.

    Parameters
    ----------
    a
        Variable :math:`a` to append a channel to.
    value
        Channel value.

    Returns
    -------
    :class:`numpy.ndarray`
        Variable :math:`a` with appended channel.
    """

    a = np.copy(a)

    return np.hstack(  # pyright: ignore
        [
            a,
            full(
                (*list(a.shape[:-1]), 1),
                value,
                dtype=a.dtype,  # pyright: ignore
            ),
        ]
    )


def unlatexify(text: str) -> str:
    """
    Unlatexify given string.


    Parameters
    ----------
    text
        String to remove the *LaTeX* character markup from.

    Returns
    -------
    :class:`str`
        Unlatexified  string.
    """

    return re.sub(r"[$^_{}]", "", text)
