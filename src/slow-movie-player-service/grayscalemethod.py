import enum


@enum.unique
class GrayscaleMethod(str, enum.Enum):
    """
    See the following excerpt from the ImageMagick documentation for further
    details about the available grayscale methods.

    The following formulas are currently provided, and will first convert
    the pixel values to linear-RGB or non-linear sRGB colorspace before being
    applied to calculate the final grayscale value:

    | Method          | Formula                                   |
    | --------------- | ----------------------------------------- |
    | Rec601Luma      | 0.298839R' + 0.586811G' + 0.114350B'      |
    | Rec601Luminance | 0.298839R  + 0.586811G  + 0.114350B       |
    | Rec709Luma      | 0.212656R' + 0.715158G' + 0.072186B'      |
    | Rec709Luminance | 0.212656R  + 0.715158G  + 0.072186B       |
    | Brightness      | max(R', G', B')                           |
    | Lightness       | (min(R', G', B') + max(R', G', B')) / 2.0 |

    Note that the above R,G,B values is the image's linear-RGB values,
    while R',G',B' are sRGB non-linear values.

    The following methods are mathematical in nature and will use the current
    value in the images respective R,G,B channel regardless of what that is,
    or what colorspace the image is currently using:

    | Method  | Formula                          |
    | ------- | -------------------------------- |
    | Average | (R' + G' + B') / 3.0             |
    | RMS     | sqrt((R'^2 + G'^2 + B'^2) / 3.0) |

    These methods are often used for other purposes, such as generating
    a grayscale difference image between two color images.

    For further details please see:
      * https://imagemagick.org/Usage/color_mods/#grayscale
      * https://imagemagick.org/script/command-line-options.php?#grayscale
      * https://imagemagick.org/script/command-line-options.php?#intensity
    """

    REC601LUMA = 'Rec601Luma'
    REC601LUMINANCE = 'Rec601Luminance'
    REC709LUMA = 'Rec709Luma'
    REC709LUMINANCE = 'Rec709Luminance'
    BRIGHTNESS = 'Brightness'
    LIGHTNESS = 'Lightness'
    AVERAGE = 'Average'
    RMS = 'RMS'

    @classmethod
    def _missing_(cls, _: str):
        return cls.REC709LUMA
