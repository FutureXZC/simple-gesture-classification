import os

root = os.path.join('.', 'sketch-shape-dataset')
rectangle = os.listdir(os.path.join(root, 'rectangle'))
square = os.listdir(os.path.join(root, 'square'))
triangle = os.listdir(os.path.join(root, 'triangle'))
circle = os.listdir(os.path.join(root, 'circle'))

workspace = [rectangle, square, triangle, circle]
label = ['rectangle', 'square', 'triangle', 'circle']
for i in range(len(workspace)):
    count = 0
    if not os.path.exists(os.path.join(root, label[i], 'train')):
        os.mkdir(os.path.join(root, label[i], 'train'))
        os.mkdir(os.path.join(root, label[i], 'test'))
    for item in workspace[i]:
        format = item[-4:]
        if count % 10 < 7:
            os.rename(os.path.join(root, label[i], item), os.path.join(root, label[i], 'train', str(count) + format))
        else:
            os.rename(os.path.join(root, label[i], item), os.path.join(root, label[i], 'test', str(count) + format))
        count += 1
print('done')