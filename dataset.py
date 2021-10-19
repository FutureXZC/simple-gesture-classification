import os

from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader


def default_sk_loader(path: str):
    """Sketch data loader.

    Args:
        path: Sketch file path.

    Returns:
        Sketch matrix, 224 x 224.
    
    """
    return Image.open(path).convert('RGB').resize((227, 227))


class SketchDataset(Dataset):
    '''Generate sketch dataset

    label: 0 -- triangle
    label: 1 -- square
    label: 2 -- rectangle
    label: 3 -- circle

    Attributes:
        split:
            Partition of data sets.
        transform:
            Transformation applied to the image.
        loader:
            Loader of each sketch.

    '''
    def __init__(self, split: str = 'train', transform: transforms = None, loader=default_sk_loader):
        root = os.path.join('.', 'sketch-shape-dataset')
        label = os.listdir(root)
        imgs = []
        for i in range(len(label)):
            cls_path = os.path.join(root, label[i], split)
            filelist = os.listdir(cls_path)
            for item in filelist:
                imgs.append((os.path.join(cls_path, item), i))
        self.imgs = imgs
        self.transform = transform
        self.loader = loader

    def __getitem__(self, index):
        fn, label = self.imgs[index]
        img = self.loader(fn)
        if self.transform is not None:
            img = self.transform(img)
        return img, label

    def __len__(self):
        return len(self.imgs)


if __name__ == '__main__':
    # load sketch data
    transform_train = transforms.Compose([
        transforms.RandomChoice([transforms.RandomCrop(224),
                                 transforms.RandomRotation(degrees=(0, 180), fill=255)]),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.ToTensor(),
        transforms.Normalize(mean=0.9910072088241577, std=0.07824398577213287),
    ])
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=0.9910072088241577, std=0.07824398577213287),
    ])
    train_data = SketchDataset(split='train', transform=transform_train)
    test_data = SketchDataset(split='test', transform=transform_test)
    train_loader = DataLoader(dataset=train_data, batch_size=64, shuffle=True)
    test_loader = DataLoader(dataset=test_data, batch_size=64, shuffle=True)
    for i, data in enumerate(train_loader):
        sk, label = data
        # sk shape: torch.Size([64, 1, 224, 224]) sk label shape: torch.Size([64])
        print('sk shape:', sk.shape, 'sk label shape:', label.shape)
        break
    print('sketch train data[0]:', train_data[0])
    print('sketch train data length:', len(train_data))  # 967
    print('sketch test data length:', len(test_data))  # 413
