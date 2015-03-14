#!/usr/bin/env python
"""
Finding blobs in an image.

Example script for OpenData Hackathon Freiburg 2015.
"""


import skimage.data
import skimage.feature
import skimage.color

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

import math

import scipy.stats.kde
import numpy as np

import csv
import os.path

import logging
_log = logging.getLogger(__file__)


def kde_image_from_peaks(image):
    image_gray = skimage.color.rgb2gray(image)

    _log.info("Finding peaks...")
    peaks = skimage.feature.peak_local_max(image_gray, min_distance=1)

    _log.info("Finding KDE...")
    bw_method = 0.1
    kernel = scipy.stats.kde.gaussian_kde(peaks.transpose(), bw_method=bw_method )

    xmin, ymin = 0, 0
    xmax, ymax = image_gray.shape

    sample_step = 25

    X, Y = np.mgrid[xmin:xmax:sample_step, ymin:ymax:sample_step]
    #X, Y = np.mgrid[range(xmax), range(ymax)]
    positions = np.vstack([X.ravel(), Y.ravel()])

    # Z = np.reshape(kernel(positions), X.T.shape)

    _log.info("Evaluating KDE at positions..")
    # Z = kernel(positions)
    # Z = kernel.resample()
    Z = np.reshape(kernel(positions), X.shape)

    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    # image_plot = ax.imshow(Z, cmap=plt.cm.hot, interpolation='nearest')

    


    return Z


def find_blobs(image):
    """Find blobs.

    Parameters
    ----------

     image: numpy array
        image data as NumPy array

     
    Return
    ------

     A sequence of tuples

       (y,x,size)

     one for each blob found.
     Reversly sorted by blob size, largest blobs first.
    """
    _log.info("Finding blobs...")

    image_gray = skimage.color.rgb2gray(image)

    #
    # we could also use other blob functions here
    # see skimage.feature
    # 
    blobs = skimage.feature.blob_dog(image_gray, max_sigma=20, threshold=.1)

    #blobs = skimage.feature.blob_doh(image_gray, max_sigma=10, threshold=.01)
    #blobs = skimage.feature.blob_log(image_gray, max_sigma=200, min_sigma=1, num_sigma=20, 
    #                                 threshold=.1, log_scale=False)

    if len(blobs)==0:
        _log.info("No blobs found.")
        return []    

    # Compute radii in the 3rd column. (dog+log)
    blobs[:, 2] = blobs[:, 2] * math.sqrt(2)


    sorted_blobs = blobs[blobs[:,2].argsort()][::-1] # sort, reverse
    
    return sorted_blobs

def plot_blobs(ax, blobs, **plot_kwds):
    """Plot blobs to given axes.

    Parameters
    ----------

    ax: matplotlib.Axes

    blobs: output of find_blobs()

    plot_kwds: dict
       additional arguments for plot function
    """
    for y,x,r in blobs:
        _log.debug("Plot blobs (%d,%d) with size %f..", x, y, r)
        c = mpatches.Circle((x, y), r, **plot_kwds)
        ax.add_patch(c)

def save_plot(stem, suffix, image, blobs):
    figname = stem+'-%s.png' % (suffix,)

    _log.info("Generating plot '%s'...", figname)
    fig, ax = plt.subplots(1,1)

    ax.imshow(image, interpolation='nearest')
    plot_blobs(ax, blobs, color='g', linewidth=2, fill=False)

    fig.savefig(figname)


if __name__=='__main__':

    logging.basicConfig(level=logging.INFO)
    _log.setLevel(logging.INFO)

    import argparse

    description = """
    Finding blobs in given images.

    Output is a CSV file with columns

      x:    x position of blob
      y:    y position of blob 
      size: size of blob in pixels

    The CSV file is named after the input file,
    replacing the extension with "-blobs.csv".

    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('infiles', metavar='image', type=str, nargs='+',
                        help='file names of image files')
    parser.add_argument('--plot', action='store_true', 
                        help="Generate a plot and save picture.")
    parser.add_argument('--debug', action='store_true', 
                        help="More log messages.")

    args = parser.parse_args()


    if args.debug:
        _log.setLevel(logging.DEBUG)

    for fname in args.infiles:
        _log.info("Processing image '%s'...", fname)
        image = skimage.data.imread(fname)

        kde_image = kde_image_from_peaks(image)
        blobs = find_blobs(image)

        _log.info("Found %d blobs.", len(blobs))

        stem, ext = os.path.splitext(fname)

        #
        # Exporting blobs
        #
        csvname = stem+'-blobs.csv'
        _log.info("Exporting to '%s'...", csvname)

        csvfile = open(csvname, 'w')
        writer = csv.writer(csvfile)
        
        writer.writerow(['x', 'y', 'size'])
        for blob in blobs:
            y,x,r = blob
            writer.writerow((x,y,r))
        
        csvfile.close()

        #
        # Optionally plotting blobs
        #
        if args.plot:

            save_plot(stem, "-blobs", image, blobs)
            save_plot(stem, "-kdeblobs", kde_image, blobs)

    _log.info("Done.")

            
