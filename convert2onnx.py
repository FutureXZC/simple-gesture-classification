import os

import numpy as np
import onnxruntime
from onnxruntime.datasets import get_example
import torch
import torch.onnx

from model import ResNet


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


def convert(num_classes: int):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResNet(num_class=num_classes).to(device)
    model = torch.nn.DataParallel(model, device_ids=[0, 1])
    pthfile = os.path.join('.', 'checkpoints', 'best_acc_99.7579.pth')
    loaded_model = torch.load(pthfile)
    model.load_state_dict(loaded_model['resnet18_state_dict'])

    dummy_input = torch.randn(64, 1, 224, 224)
    with torch.no_grad():
        torch_out = model(dummy_input)
    print('torch out:', torch_out)

    model = model.to('cpu')
    # print(model, model.module)

    #data type nchw
    input_names = ["input"]
    output_names = ["output"]
    torch.onnx.export(model.module,
                      dummy_input,
                      "cls.onnx",
                      verbose=True,
                      input_names=input_names,
                      output_names=output_names)
    example_model = get_example('/home/czx/simple-gesture-classification/cls.onnx')
    sess = onnxruntime.InferenceSession(example_model)
    print(example_model)
    onnx_out = sess.run(None, {'input': to_numpy(dummy_input)})
    print('onnx out:', torch_out)

    # np.testing.assert_almost_equal(to_numpy(torch_out), onnx_out[0], decimal=3)
    # np.testing.assert_allclose(to_numpy(torch_out), onnx_out[0], rtol=1e-3, atol=0)


if __name__ == "__main__":
    convert(num_classes=4)
