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
    # imgs = imgs.astype(np.float32) / 255.
    imgs = imgs.astype(np.float32)
    print('Shape: ({}, {}), total: {}'.format(imgs.shape[0], imgs.shape[1], imgs.shape[2]))

    pixels = imgs.ravel()
    means = np.mean(pixels)
    stdevs = np.std(pixels)
    print('Normalize Mean of dataset = {}'.format(means))
    print('Normalize Std of dataset = {}'.format(stdevs))


if __name__ == '__main__':
    # 原始：
    # mean = 0.9910072088241577, std = 0.07824398577213287
    # mean = 252.7069854736328, std = 19.952280044555664
    # 2000：
    # mean = 0.9869946837425232, std = 0.09663939476013184
    # mean = 251.6833953857422, std = 24.643047332763672
    path = os.path.join('.', 'sketch-shape-2000')
    getMeanAndStd(path)
