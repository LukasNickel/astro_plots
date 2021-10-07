from ctapipe.visualization import CameraDisplay
from matplotlib.collections import PatchCollection
from ctapipe.instrument import PixelShape
from matplotlib import pyplot as plt
from astropy import units as u
from matplotlib.patches import Ellipse, RegularPolygon, Rectangle, Circle
from ctapipe.io import EventSource, EventSeeker
from ctapipe.image import tailcuts_clean, LocalPeakWindowSum
from ctapipe.utils import get_dataset_path
from ctapipe.calib import CameraCalibrator
import copy
import numpy as np


class MYCameraDisplay(CameraDisplay):
    """
    using the ctapipe camera display with slight adjustments
    No title, axis labels and no autoscale
    """

    def __init__(
        self,
        geometry,
        image=None,
        ax=None,
        title=None,
        norm="lin",
        cmap=None,
        allow_pick=False,
        autoupdate=True,
        autoscale=True,
        show_frame=True,
    ):
        self.axes = ax if ax is not None else plt.gca()
        self.pixels = None
        self.colorbar = None
        self.autoupdate = autoupdate
        self.autoscale = autoscale

        self.geom = geometry

        # initialize the plot and generate the pixels as a
        # RegularPolyCollection

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

        # Set up some nice plot defaults

        self.axes.set_aspect("equal")
        #self.axes.autoscale_view()

        if image is not None:
            self.image = image
        else:
            self.image = np.zeros_like(self.geom.pix_id, dtype=np.float64)

        self.norm = norm
        self.axes.xticks = None


def main():
    # using toymodel would generate a nicer shower, but I want accurate waveforms as well
    source = EventSource(get_dataset_path("gamma_test_large.simtel.gz"), max_events=100, back_seekable=True)
    seeker = EventSeeker(source)
    ex = LocalPeakWindowSum(subarray=source.subarray)
    calib = CameraCalibrator(subarray=source.subarray, image_extractor_type="LocalPeakWindowSum")
    event = seeker.get_event_index(91)
    calib(event)
    
    tel_id = 1 # LST-1
    geom = source.subarray.tel[tel_id].camera.geometry
    image=event.dl1.tel[tel_id].image
    mask = tailcuts_clean(geom, image, 14, 7, 2)
    # brightest pixel for second zoom
    mask2 = np.zeros(len(image), dtype=bool)
    mask2[np.argmax(image)] = True

    fig, ax = plt.subplots(figsize=(12,6))
    norm = "lin"
    d = geom.pixel_width.value[0]
    c1 = "red"
    c2 = "blue"
    # add space on the right for the inset axes
    ax.set_xlim(-1.5, 4.5)
    ax.set_ylim(-1.5, 1.5)

    disp = MYCameraDisplay(geom, ax=ax, norm=norm)#, cmap="hot")
    disp.image = image
    disp.add_colorbar(location="left", fraction=.04, pad=.001, aspect=10)
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.spines.left.set_visible(False)
    ax.spines.bottom.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    
    axins = ax.inset_axes([0.45, 0.41, 0.2, 0.5])
    disp2 = MYCameraDisplay(geom, ax=axins, norm=norm)
    disp2.image = image
    disp2.highlight_pixels(mask, alpha=0.4, color=c1)    
    axins.set_xlim(geom.pix_x[mask].value.min()-d, geom.pix_x[mask].value.max()+d)
    axins.set_ylim(geom.pix_y[mask].value.min()-d, geom.pix_y[mask].value.max()+d)
    axins.set_xticks([])
    axins.set_yticks([])
    ax.indicate_inset_zoom(axins, edgecolor=c1)

    
    xl = geom.pix_x.value[np.argmax(image)] - d/2
    xu = geom.pix_x.value[np.argmax(image)] + d/2
    yl = geom.pix_y.value[np.argmax(image)] - d/2
    yu = geom.pix_y.value[np.argmax(image)] + d/2

    axwf = ax.inset_axes([0.6, 0.1, 0.3, 0.3])
    axwf.set_xlim(xl, xu)
    axwf.set_ylim(yl, yu)
    axwf.set_xticks([])
    axwf.set_yticks([])
    axins.indicate_inset_zoom(axwf, edgecolor=c2)
    wf = event.r1.tel[1].waveform[mask2][0, :]
    
    
    # scale and shift the wf to fit the axes 
    # this is a bit hacky, but we dont label the y-axis anyway
    def adapt(x):
        s = max(x) / (yu-yl)
        x /= (1.1*s)
        x += (yl-min(x))
        return x
    wf = adapt(wf)
    x = np.linspace(xl, xu, len(wf))
    peak = wf.argmax(axis=-1).astype(np.int64)
    left = peak - ex.window_width.tel[tel_id]
    right = peak + ex.window_width.tel[tel_id]
    axwf.axvline(x[peak], color="magenta", label="Peak Time", alpha=.4)
    axwf.axvline(x[left], color="green", label="Integration_window", alpha=.4)
    axwf.axvline(x[right], color="green", alpha=.4)
    axwf.fill_between(x[left:right+1],wf[left:right+1],min(wf) , color="green", alpha=0.2, label="Charge")
    axwf.plot(x, wf, "b.-", )
    axwf.legend(bbox_to_anchor=(0.4, 1.4), loc='upper left', borderaxespad=0.)
    fig.savefig("iact.png")
    

if __name__ == "__main__":
    main()