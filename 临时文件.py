import onnx
import torch

from nets.siamese import Siamese


cuda = torch.cuda.is_available()
device = torch.device('cuda:0' if cuda else 'cpu')
model = Siamese([105, 105])
model.load_state_dict(torch.load("C:/Users/Administrator/Desktop/best_epoch_weights.pth", map_location=device))
input_image1 = torch.randn(1, 3, 105, 105).to(device)
input_image2 = torch.randn(1, 3, 105, 105).to(device)
onnx_outpath = "C:/Users/Administrator/Downloads/BilibiliAutoReport/src/pre_model_v61.onnx"
torch.onnx.export(model,
                  (input_image1, input_image2),
                  onnx_outpath,
                  opset_version=13,
                  verbose=True,
                  do_constant_folding=True,
                  input_names=['x1', 'x2'],
                  output_names=['output'],
                  dynamic_axes={'x1': {0: 'batch_size'}, 'x2': {0: 'batch_size'}})




import onnxruntime
from onnxruntime.quantization import quantize_dynamic, QuantType

# 加载你的 ONNX 模型
onnx_model_path = "C:/Users/Administrator/Downloads/BilibiliAutoReport/src/pre_model_v61.onnx"
quantized_model_path = "C:/Users/Administrator/Downloads/BilibiliAutoReport/src/pre_model_v6_quantized.onnx"

# 动态量化
quantize_dynamic(
    model_input=onnx_model_path,
    model_output=quantized_model_path,
    weight_type=QuantType.QUInt8 , # 使用 QInt8 进行量化
   # 是否优化模型

)

print("量化完成，量化后的模型已保存到:", quantized_model_path)