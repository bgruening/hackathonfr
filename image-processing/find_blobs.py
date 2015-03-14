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
#import numpy as np
import math

import csv
import os.path

import logging
_log = logging.getLogger(__file__)


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
    blobs = skimage.feature.blob_dog(image_gray, max_sigma=30, threshold=.1)
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
            
            figname = stem+'-blobs.png'

            _log.info("Generating plot '%s'...", figname)
            fig, ax = plt.subplots(1,1)

            ax.imshow(image, interpolation='nearest')
            plot_blobs(ax, blobs, color='g', linewidth=2, fill=False)

            fig.savefig(figname)

    _log.info("Done.")

            
