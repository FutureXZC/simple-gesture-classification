import os

root = os.path.join('.', 'sketch-shape-dataset')
rectangle = os.listdir(os.path.join(root, 'rectangle'))
square = os.listdir(os.path.join(root, 'square'))
triangle = os.listdir(os.path.join(root, 'triangle'))
# print(rectangle, square, triangle)

workspace = [rectangle, square, triangle]
label = ['rectangle', 'square', 'triangle']
for i in range(len(workspace)):
    count = 0
    if not os.path.exists(os.path.join(root, label[i] + '-new')):
        os.mkdir(os.path.join(root, label[i] + '-new'))
        os.mkdir(os.path.join(root, label[i] + '-new', 'train'))
        os.mkdir(os.path.join(root, label[i] + '-new', 'test'))
    for item in workspace[i]:
        if count % 10 < 7:
            os.rename(os.path.join(root, label[i], item),
                      os.path.join(root, label[i] + '-new', 'train',
                                   str(count) + '.jpg'))
        else:
            os.rename(os.path.join(root, label[i], item),
                      os.path.join(root, label[i] + '-new', 'test',
                                   str(count) + '.jpg'))
        count += 1
print('done')