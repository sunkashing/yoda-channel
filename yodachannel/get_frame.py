import os
from os.path import sep

import cv2


def get_frame_from_video(video_name, frame_time, img_dir, img_name):
    """
    get a specific frame of a video by time in milliseconds
    :param video_name: video name
    :param frame_time: time of the desired frame
    :param img_dir: path which use to store output image
    :param img_name: name of output image
    :return: None
    """
    vidcap = cv2.VideoCapture(video_name)
    # Current position of the video file in milliseconds.
    vidcap.set(cv2.CAP_PROP_POS_MSEC, frame_time - 1)
    # read(): Grabs, decodes and returns the next video frame
    success, image = vidcap.read()

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    if success:
        # save frame as JPEG file
        cv2.imwrite(img_dir + sep + img_name, image)
        # cv2.imshow("frame%s" % frame_time, image)
        # cv2.waitKey()