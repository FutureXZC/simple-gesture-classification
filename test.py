import os
import sys
import torch
from model import AlexNet
from PIL import Image
from torchvision import transforms


def test_sketch(pthfile_path: str, img_path: str):
    '''Identify the classification of individual sketches.
    label: 0 -- triangle
    label: 1 -- rectangle
    label: 2 -- circle
    
    Args:
        pthfile_path: Path of .pth file.
        img_path: Path of sketch file.

    Returns:
        label: A int number representing the category.
    '''

    # load model
    model = AlexNet(num_classes=3).to('cuda')
    loaded_model = torch.load(pthfile_path)
    model.load_state_dict(loaded_model['state_dict'])

    # load sketch
    img = Image.open(img_path).convert('RGB').resize((224, 224))
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=0.9869946837425232, std=0.09663939476013184),
    ])
    # torch.Size([1, 3, 224, 224])
    img = transform(img).unsqueeze(0).to('cuda')

    # predict
    predict = model(img)
    _, idx = predict.max(-1)
    label = idx.item()
    return label


def main():
    pthfile_path = os.path.join('.', 'src', 'model.pth')
    img_path = os.path.join('.', 'src', 'test_sketch.jpg')
    label = test_sketch(pthfile_path, img_path)
    sys.exit(label)


if __name__ == '__main__':
    main()