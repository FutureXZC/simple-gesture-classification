import os

import numpy as np
from PIL import Image
from glob import glob
from tqdm import tqdm


def getMeanAndStd(load_path: str):
    """Calculate the mean and standard deviation of the data set
    
    Args:
        load_path: Path of the dataset.

    """
    img_list = list()
    image_fns = list()
    image_fns = glob(os.path.join(load_path, '*', '*', '*.*'))

    for path in tqdm(image_fns):
        img = np.array(Image.open(path).convert('L').resize((224, 224)))
        img = img[:, :, np.newaxis]
        img_list.append(img)

    imgs = np.concatenate(img_list, axis=2)
    imgs = imgs.astype(np.float32) / 255.
    print('Shape: ({}, {}), total: {}'.format(imgs.shape[0], imgs.shape[1], imgs.shape[2]))

    pixels = imgs.ravel()
    means = np.mean(pixels)
    stdevs = np.std(pixels)
    print('Normalize Mean of dataset = {}'.format(means))
    print('Normalize Std of dataset = {}'.format(stdevs))


if __name__ == '__main__':
    # mean = 0.9910072088241577, std = 0.07824398577213287
    path = os.path.join('.', 'sketch-shape-dataset')
    getMeanAndStd(path)
