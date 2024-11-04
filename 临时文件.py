import onnx
import torch

from nets.siamese import Siamese


cuda = torch.cuda.is_available()
device = torch.device('cuda:0' if cuda else 'cpu')
model = Siamese([105, 105])
model.load_state_dict(torch.load("C:/Users/Administrator/Downloads/best_epoch_weights.pth", map_location=device))
input_image1 = torch.randn(1, 3, 105, 105).to(device)
input_image2 = torch.randn(1, 3, 105, 105).to(device)
onnx_outpath = "C:/Users/Administrator/Downloads/BilibiliAutoReport/src/pre_model_v6.onnx"
torch.onnx.export(model,
                  (input_image1, input_image2),
                  onnx_outpath,
                  opset_version=13,
                  verbose=True,
                  do_constant_folding=True,
                  input_names=['x1', 'x2'],
                  output_names=['output'],
                  dynamic_axes={'x1': {0: 'batch_size'}, 'x2': {0: 'batch_size'}})

# 检查导出的onnx模型
onnx_model = onnx.load(onnx_outpath)
onnx.checker.check_model(onnx_model, full_check=True)
inferred = onnx.shape_inference.infer_shapes(onnx_model, check_type=True)







import onnx
import onnxsim

# 加载已导出的ONNX模型
onnx_model_path = "C:/Users/Administrator/Downloads/BilibiliAutoReport/src/pre_model_v6.onnx"
onnx_model = onnx.load(onnx_model_path)

try:
    # 尝试对ONNX模型进行简化处理
    print('\nStarting to simplify ONNX...')
    simplified_model, check = onnxsim.simplify(onnx_model)
    assert check, 'Simplification check failed'
except Exception as e:
    print(f'Simplifier failure: {e}')

# 保存简化后的ONNX模型
simplified_model_path = "C:/Users/Administrator/Downloads/BilibiliAutoReport/src/pre_model_v6_simplified.onnx"
onnx.save(simplified_model, simplified_model_path)
print('ONNX model has been simplified and saved as %s' % simplified_model_path)
