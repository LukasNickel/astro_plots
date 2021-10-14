from ctapipe.visualization import CameraDisplay
from matplotlib.collections import PatchCollection
from ctapipe.instrument import PixelShape
from matplotlib import pyplot as plt
from astropy import units as u
from matplotlib.patches import RegularPolygon, Rectangle, Circle
from ctapipe.io import EventSource, EventSeeker
from ctapipe.image import tailcuts_clean, LocalPeakWindowSum
from ctapipe.utils import get_dataset_path
from ctapipe.calib import CameraCalibrator
import copy
import numpy as np


class MYCameraDisplay(CameraDisplay):
    """
    Based on the ctapipe camera display from
    https://github.com/cta-observatory/ctapipe/blob/8851e1214409eac4564996cc0f4b76dfe05cf9cf/ctapipe/visualization/mpl_camera.py
    No title, axis labels and no autoscale
    """

    def __init__(
        self,
        geometry,
        image=None,
        ax=None,
        norm="lin",
        cmap=None,
        autoscale=True,
    ):
        self.axes = ax if ax is not None else plt.gca()
        self.pixels = None
        self.colorbar = None
        self.autoscale = autoscale

        self.geom = geometry

        patches = []
        if hasattr(self.geom, "mask"):
            self.mask = self.geom.mask
        else:
            self.mask = np.ones_like(self.geom.pix_x.value, dtype=bool)

        pix_x = self.geom.pix_x.value[self.mask]
        pix_y = self.geom.pix_y.value[self.mask]
        pix_width = self.geom.pixel_width.value[self.mask]

        for x, y, w in zip(pix_x, pix_y, pix_width):
            if self.geom.pix_type == PixelShape.HEXAGON:
                r = w / np.sqrt(3)
                patch = RegularPolygon(
                    (x, y),
                    6,
                    radius=r,
                    orientation=self.geom.pix_rotation.to_value(u.rad),
                    fill=True,
                )
            elif self.geom.pix_type == PixelShape.CIRCLE:
                patch = Circle((x, y), radius=w / 2, fill=True)
            elif self.geom.pix_type == PixelShape.SQUARE:
                patch = Rectangle(
                    (x - w / 2, y - w / 2),
                    width=w,
                    height=w,
                    angle=self.geom.pix_rotation.to_value(u.deg),
                    fill=True,
                )
            else:
                raise ValueError(f"Unsupported pixel_shape {self.geom.pix_type}")

            patches.append(patch)

        self.pixels = PatchCollection(patches, cmap=cmap, linewidth=0)
        self.axes.add_collection(self.pixels)

        self.pixel_highlighting = copy.copy(self.pixels)
        self.pixel_highlighting.set_facecolor("none")
        self.pixel_highlighting.set_linewidth(0)
        self.axes.add_collection(self.pixel_highlighting)

        self.axes.set_aspect("equal")

        if image is not None:
            self.image = image
        else:
            self.image = np.zeros_like(self.geom.pix_id, dtype=np.float64)
        self.norm = norm
        self.axes.xticks = None


def main():
    # using toymodel would generate a nicer shower, but I want accurate waveforms as well
    source = EventSource(get_dataset_path("gamma_test_large.simtel.gz"), max_events=100)
    seeker = EventSeeker(source)
    # Define calibrator and extractor
    # Calib should use the same extractor to be most accurate in the waveform plot
    ex = LocalPeakWindowSum(subarray=source.subarray)
    calib = CameraCalibrator(
        subarray=source.subarray, image_extractor_type="LocalPeakWindowSum"
    )
    # A reasonable bright event, there might be better ones still
    event = seeker.get_event_index(91)
    calib(event)

    tel_id = 1  # LST-1
    geom = source.subarray.tel[tel_id].camera.geometry
    image = event.dl1.tel[tel_id].image

    fig, ax = plt.subplots(figsize=(12, 6))
    # d is our natural unit here, the width of one pixel
    # Since all pixels are the same, we can use this to fine tune the view of the first zoom
    d = geom.pixel_width.value[0]
    norm = "lin"
    color_shower_zoom = "red"
    color_waveform_zoom = "blue"
    color_extractor = "green"
    color_waveform_peak = "magenta"
    # add space on the right for the inset axes
    ax.set_xlim(-1.5, 4.5)
    ax.set_ylim(-1.5, 1.5)

    main_cam_display = MYCameraDisplay(geom, ax=ax, norm=norm)
    main_cam_display.image = image
    # This is manually chosen to match the figure size!
    main_cam_display.add_colorbar(location="left", fraction=0.04, pad=0.001, aspect=10)
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.spines.left.set_visible(False)
    ax.spines.bottom.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    ax_shower_zoom = ax.inset_axes([0.45, 0.41, 0.2, 0.5])
    zoomed_cam_display = MYCameraDisplay(geom, ax=ax_shower_zoom, norm=norm)
    mask = tailcuts_clean(geom, image, 14, 7, 2)
    zoomed_cam_display.image = image
    zoomed_cam_display.highlight_pixels(mask, alpha=0.4, color=color_shower_zoom)
    ax_shower_zoom.set_xlim(
        geom.pix_x[mask].value.min() - d, geom.pix_x[mask].value.max() + d
    )
    ax_shower_zoom.set_ylim(
        geom.pix_y[mask].value.min() - d, geom.pix_y[mask].value.max() + d
    )
    ax_shower_zoom.set_xticks([])
    ax_shower_zoom.set_yticks([])
    ax.indicate_inset_zoom(ax_shower_zoom, edgecolor=color_shower_zoom)

    # Select the pixel
    # This will select a square instead of a hexagon
    # It would require some manual work to properly select the
    # pixel, but would also avoid our scaling issues below
    # Maybe at some point in the future
    xl = geom.pix_x.value[np.argmax(image)] - d / 2
    xu = geom.pix_x.value[np.argmax(image)] + d / 2
    yl = geom.pix_y.value[np.argmax(image)] - d / 2
    yu = geom.pix_y.value[np.argmax(image)] + d / 2
    mask_brightest = np.zeros(len(image), dtype=bool)
    mask_brightest[np.argmax(image)] = True

    ax_waveform = ax.inset_axes([0.6, 0.1, 0.3, 0.3])
    ax_waveform.set_xlim(xl, xu)
    ax_waveform.set_ylim(yl, yu)
    ax_waveform.set_xticks([])
    ax_waveform.set_yticks([])
    ax_shower_zoom.indicate_inset_zoom(ax_waveform, edgecolor=color_waveform_zoom)
    wf = event.r1.tel[1].waveform[mask_brightest][0, :]

    # Some hacks to make the waveform fit the axis limits
    # We cant change the limits, because that would change the zoomed area
    # This could be avoided by manually constructing this instead of relying
    # on indicate_inset_zoom
    def adapt(x):
        s = max(x) / (yu - yl)
        x /= 1.1 * s
        x += yl - min(x)
        return x

    wf = adapt(wf)
    x = np.linspace(xl, xu, len(wf))

    # These are indices, not the absolute values:
    peak = wf.argmax(axis=-1).astype(np.int64)
    left = peak - ex.window_width.tel[tel_id]
    right = peak + ex.window_width.tel[tel_id]

    ax_waveform.plot(
        x, wf, marker=".", color=color_waveform_zoom, label="Calibrated Waveform"
    )
    ax_waveform.axvline(
        x[peak], color=color_waveform_peak, label="Peak Time", alpha=0.4
    )
    ax_waveform.axvline(
        x[left], color=color_extractor, label="Integration_window", alpha=0.4
    )
    ax_waveform.axvline(x[right], color=color_extractor, alpha=0.4)
    ax_waveform.fill_between(
        x[left : right + 1],
        wf[left : right + 1],
        min(wf),
        color=color_extractor,
        alpha=0.2,
        label="Charge",
    )
    ax_waveform.legend(bbox_to_anchor=(0.4, 1.6), loc="upper left", borderaxespad=0.0)
    fig.savefig("iact.png")


if __name__ == "__main__":
    main()
