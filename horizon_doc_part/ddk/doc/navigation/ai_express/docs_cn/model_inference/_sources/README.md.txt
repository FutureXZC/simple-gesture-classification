# 1 Introduce
model_inference预测组件用于集成推理模型，目的是降低模型集成到上板的复杂度。model_inference组件核心逻辑包括模型前处理、推理预测和后处理模块。组件内置了模型预测模块，用户只需要关注模型的前后处理模块，可以通过扩展前后处理的方式集成自定义的模型。

## 1.1 目前支持的前处理
 1) pyramid_roi_resizer_preprocess

 面向`resizer`的输入方式的模型，输入数据为一系列检测框rois和金字塔图像pyramid。预测时底层会依赖硬件resizer模块。

 2) pyramid_preprocess

 面向`pyramid`输入方式的定点模型，输入数据是金字塔图像pyramid。该处理中取金字塔配置的层，送入模型进行推理。

 3) pyramid_roi_bpu_preprocess

 面向`pyramid`输入方式的模型，输入数据是一系列检测框rois和金字塔图像pyramid，与前处理2)`pyramid_preprocess`不同的是，该处理中取金字塔原图对应的roi图像数据，经过硬件crop&resize到模型输入大小，送入模型进行推理。

 4) pyramid_roi_preprocess

 面向`pyramid`输入方式的模型，输入数据是一系列检测框rois和金字塔图像pyramid，与前处理3)`pyramid_roi_bpu_preprocess`不同的是，该处理中取金字塔原图对应的roi图像数据，经过软件的图像处理操作送入模型进行推理。

 5) image_preprocess

 面向`pyramid`输入方式的模型，输入数据是nv12格式的`RawDataImageFrame`数据。该处理中取输入图像并按配置进行一系列图像处理后送入模型进行推理。

 6) faceid_preprocess

 针对"人脸特征提取"模型的预处理，输入数据是`SnapshotInfo`。

 7) gesture_preprocess

 针对"手势识别"模型的预处理。


## 1.2 目前支持的后处理
 1) age_gender_postprocess

 针对"年龄性别"模型的后处理，输出年龄、性别结果

 2) face_quality_postprocess

 针对"人脸质量"模型的后处理，输出14个人脸质量相关的结果。

 3) faceid_postprocess

针对"人脸特征提取"模型的后处理，输出128维人脸特征数据。

 4) horizon_multitask_postprocess

 针对"多任务检测"模型的后处理，内置后处理包括检测框、人体骨骼点、分割等。

 5) lmks3_postprocess

 针对"手关键点"模型的后处理，输出手关键点。

 6) lmks4_postprocess

 针对"人脸关键点"模型的后处理，输出人脸关键点。

 7) plate_num_postprocess

 针对"车牌号"识别模型的后处理，输出车牌号。

 8) vehicle_color_postprocess

 针对"车辆颜色"模型的后处理，输出车辆颜色。

 9) vehicle_type_postprocess

 针对"车辆类型"模型的后处理，输出车辆类型。

 10) yolov3_postprocess

 针对开源模型"yolov3"的后处理，输出检测框。

 11) mobilenetv2_postprocess

 针对开源模型"mobilenetv2"的后处理，输出类别。

 12) gesture_postprocess

 针对"手势识别"模型的后处理，输出手势类别。



# 2 编译
```
mkdir build && cd build && cmake .. && make && make install
```
在model_inference目录下生成output文件夹，该目录下有如下内容：
```shell
.
├── include
│   └── model_inference
│       ├── inference_data.h
│       ├── inference_engine_bpu.h
│       ├── inference_engine_dnn.h
│       ├── inference_engine.h
│       ├── inference_method.h
│       ├── inferencer.h
│       ├── inference_task.h
│       ├── postprocess
│       │   ├── age_gender_postprocess.h
│       │   ├── faceid_postprocess.h
│       │   ├── face_quality_postprocess.h
│       │   ├── gesture_postprocess.h
│       │   ├── horizon_multitask_postprocess.h
│       │   ├── lmks3_postprocess.h
│       │   ├── lmks4_postprocess.h
│       │   ├── vehicle_color_postprocess.h
│       │   ├── vehicle_type_postprocess.h
│       │   ├── plate_num_postprocess.h
│       │   ├── mobilenetv2_postprocess.h
│       │   └── yolov3_postprocess.h
│       │   ├── postprocess.h
│       │   ├── utils
│       │   │   └── gesture_postprocess_util.h
│       └── preprocess
│           ├── faceid_preprocess.h
│           ├── gesture_preprocess.h
│           ├── image_preprocess.h
│           ├── preprocess.h
│           ├── pyramid_preprocess.h
│           ├── pyramid_roi_bpu_preprocess.h
│           ├── pyramid_roi_preprocess.h
│           ├── pyramid_roi_resizer_preprocess.h
│           └── utils
│               ├── image_process.h
│               ├── lmks_process.h
│               └── roi_process.h
└── lib
    └── libmodel_inference.so
```

## 2.1 依赖库说明
  1. 背景：上述两种功能依赖的库和头文件，都存放在host package压缩包中，它是随每次中间件发版输出的内容。例如host_package_1.1.0.tar.gz。
  2. 使用方式：将host_package_1.1.0.tar.gz解压到当前用户所用开发机的主目录(内部文件夹内容是.horizon文件夹，存放在~/.horizon)
  3. host_package内容包括:
     a) xstream动态库和头文件，提供AI模型集成形成workflow、任务调度等功能。
	 b) image_utils动态库和头文件，提供了c++接口版本的图像处理接口(软件处理)。
	 c) bpu_predict动态库和头文件，提供模型预测的能力。


# 3 使用说明
model_inference组件内部扩展了`InferMethod`和`PostMethod`以支持在xstream中使用。用户可以在xstream的worflow中配置两个method使用预测组件。

## 3.1 预处理
model_inference组件以配置为驱动，内置了部分通用预处理模块。

### 3.1.1 图像预处理
模型预处理部分，对于Image类型，包括如下功能：

 a) pad(height, width)

 其中height和width为参数，默认采用对图像右下边进行padding，填充数据默认为0；目前仅支持nv12图像格式，且限制height和width参数需大于等于原始图像宽高。

 b) resize(height, width)

 其中height和width为参数，默认对原始图像resize到参数大小，不保持宽高比；目前仅支持nv12图像格式。

 c) crop(x1, y1, x2, y2)

 其中x1,y1表示左上角坐标，x2,y2表示右下角坐标，默认裁剪原始图像的指定区域（包括左上角、右下角所在行列）；目前仅支持nv12图像格式。

### 3.1.2 roi预处理
模型预处理部分，对于ROI类型，提供了集中不同类型的外扩方案，包括norm_by_width_length、norm_by_width_ratio、norm_by_height_length、norm_by_height_ratio、norm_by_lside_length、norm_by_lside_ratio、norm_by_lside_square、norm_by_diagonal_square、norm_by_width_square、norm_by_height_square、norm_by_nothing。并可以在外扩方法后接参数(expand_scale, aspect_ratio)。

### 3.1.3 使用示例
1. 以`pyramid_preprocess`内置预处理为例，添加配置文件如下：
```json
{
    "class_name": "pyramid_preprocess",
    "pyramid_layer": 4,
    "config": {
        "image_process_pipeline": [
            "pad(960, 960)",
            "resize(416, 416)"
        ]
    }
}
```
输入金字塔图像pyramid，以上述配置文件为例，假设输入金字塔原图大小是1080p（1920x1080）。取金字塔第4层（960x540），padding到960x960，再resize到416x416大小。

2. 以`image_preprocess`内置预处理为例，添加配置文件如下：
```json
{
    "class_name": "image_preprocess",
    "config": {
        "image_process_pipeline": [
            "crop(0, 0, 959, 899)",
            "pad(960, 960)",
            "resize(416, 416)"
        ]
    }
}
```
输入RawData图像数据，以上述配置文件为例，假设输入图像大小是1080p（1920x1080）。裁剪图像感兴趣区域，左上角坐标(0,0)、右下角坐标(959, 899)，即得到960x900大小的图像，padding到960x960，再resize到416x416大小。


3. 以`pyramid_roi_preprocess`内置预处理的使用为例，添加配置如下：
```json
{
    "class_name": "pyramid_roi_preprocess",
    "config": {
        "roi_process_pipeline": ["norm_by_lside_length(1.2)"],
        "image_process_pipeline": [
            "resize(128, 128)"
        ]
    }
}
```
输入一系列检测框rois和金字塔图像pyramid，以上述配置文件为例，对检测框roi进行外扩系数为1.2的`norm_by_lside_length`的外扩处理后，取外扩后的norm_roi在金字塔原图对应的图像数据，并resize到128x128大小；上述预处理都是软件处理。


4. 以`pyramid_roi_bpu_preprocess`内置预处理为例，添加配置文件如下：
```json
{
    "class_name": "pyramid_roi_bpu_preprocess",
    "config": {
        "roi_process_pipeline": ["norm_by_lside_length(1.08)"]
    }
}
```
输入一系列检测框rois和金字塔图像pyramid，以上述配置文件为例，对检测框roi进行外扩系数为1.08的`norm_by_lside_length`的外扩处理后，crop外扩后的norm_roi在金字塔原图对应的图像数据，并resize到模型输入大小；上述crop&&resize的处理是硬件处理。

5. 以`pyramid_roi_resizer_preprocess`内置预处理为例，添加配置文件如下：
```json
{
    "class_name": "pyramid_roi_resizer_preprocess",
    "config": {
        "roi_process_pipeline": [
            "norm_by_lside_square(1.2, 0.91)"
        ]
    }
}
```
针对`resizer`输入方式的模型，输入一系列检测框rois和金字塔图像pyramid，以上述配置文件为例，对检测框roi进行外扩系数为1.2，宽高比为0.91的`norm_by_lside_square`的外扩处理，将处理后的norm_roi和金字塔封装为推理任务送入推理队列。


## 3.2 预测
预测部分配置包括：模型路径、packed属性以及该模型任务需要运行在哪个bpu核上。
```json
{
    "model_file_path": "**.hbm",
    "is_packed_model": false,
    "model_name": "**",
    "run_mode": {
        "bpu_core": 1
    }
}
```

## 3.3 后处理
后处理同预处理配置类似，需要指定`class_name`字段，以使用对应的后处理方法。
```json
{
    "class_name": "age_gender_postprocess"
}
```

## 3.4 model_inference配置
 a) 组件中默认预测和后处理过程是同步，即在InferMethod中输出后处理的结果；若用户想将预测后处理过程pipeline起来，需要配置`with_postprocess`字段为false，表示InferMethod中不做后处理，这种情况下，InferMethod有两个输出：该帧的"infer"对象和"tasks"推理任务。**注意**："with_postprocess"的配置需要和workflow中的Method对应，当`with_postprocess`字段为false，InferMethod需要与PostMethod串联；否则不需要。

 b) 组件中默认对模型输出的BPU结果进行转浮点操作；若用户不需要将定点模型输出结果转浮点，则需要配置`convert_to_float`字段为false，表示不对BPU输出结果转换。**注意**：配置"convert_to_float"=false后，后处理直接处理BPU输出结果后，需要将BPU内存释放。

```json
{
    "with_postprocess": false,
    "convert_to_float": false
}
```

## 3.5 结合workflow使用
以多任务检测+年龄性别识别任务为例，workflow需要串联多任务检测和年龄性别识别两个模型。workflow配置如下：
```json
{
  "inputs": [
    "image"
  ],
  "outputs": [
    "image",
    "face_box",
    "head_box",
    "body_box",
    "pose",
    "lmk",
    "kps",
    "age",
    "gender"
  ],
  "workflow": [
    {
      "method_type": "InferMethod",
      "unique_name": "multi_task",
      "inputs": [
        "image"
      ],
      "outputs": [
        "body_box",
        "head_box",
        "face_box",
        "lmk",
        "pose",
        "kps"
      ],
      "method_config_file": "infer_multitask_config.json"
    },
    {
      "method_type": "InferMethod",
      "unique_name": "age_gender_infer",
      "inputs": [
        "face_final_box",
        "image"
      ],
      "outputs": [
        "age_gender_infer",
        "age_gender_task"
      ],
      "method_config_file": "infer_age_gender.json"
    },
    {
      "method_type": "PostMethod",
      "unique_name": "age_gender_post",
      "inputs": [
        "age_gender_infer",
        "age_gender_task"
      ],
      "outputs": [
        "age",
        "gender"
      ],
      "method_config_file": ""
    }
  ]
}
```

对应的多任务检测配置infer_multitask_config.json，配置"convert_to_float"为false，"with_postprocess"为true，即不对BPU结果转换浮点，并在InferMethod中进行后处理操作，输出智能结果。
```json
{
    "with_postprocess": true,
    "convert_to_float": false,
    "model_preprocess":{
        "class_name": "pyramid_preprocess",
        "pyramid_layer": 4,
        "config": {
            "image_process_pipeline": [
            ]
        }
    },
    "model_predict": {
        "model_file_path": "../../models/personMultitask.hbm",
        "is_packed_model": false,
        "model_name": "personMultitask",
        "run_mode": {
            "bpu_core": 2
        }
    },
    "model_post_process": {
        "class_name": "horizon_multitask_postprocess",
        "net_info": {
            "model_name": "personMultitask",
            "model_version": "0.0.27",
            "model_out_sequence": [
              {
                "name": "body_box_int",
                "type": "invalid"
              },
              {
                "name": "body_box",
                "type": "bbox"
              },
              {
                "name": "head_box_int",
                "type": "invalid"
              },
              {
                "name": "head_box",
                "type": "bbox"
              },
              {
                "name": "face_box_int",
                "type": "invalid"
              },
              {
                "name": "face_box",
                "type": "bbox"
              },
              {
                "name": "lmks2_label",
                "type": "lmks2_label",
                "box_name": "face_box"
              },
              {
                "name": "lmks2_offset",
                "type": "lmks2_offset"
              },
              {
                "name": "pose",
                "type": "3d_pose",
                "box_name": "face_box"
              },
              {
                "name": "lmks1_label",
                "type": "lmks1",
                "box_name": "face_box"
              },
              {
                "name": "kps_label",
                "type": "kps_label",
                "box_name": "body_box"
              },
              {
                "name": "kps_offset",
                "type": "kps_offset"
              }
            ],
            "model_input_width": 960,
            "model_input_height": 540,
            "src_image_width": 1920,
            "src_image_height": 1080,
            "pyramid_layer": 4,
            "kps_pos_distance": 25,
            "kps_feat_width": 16,
            "kps_feat_height": 16,
            "kps_points_number": 17,
            "lmk_feat_width": 8,
            "lmk_feat_height": 8,
            "lmk_points_number": 5,
            "lmk_pos_distance": 12,
            "lmk_feat_stride": 16,
            "3d_pose_number": 3
          },
        "method_outs": ["body_box", "head_box", "face_box", "landmark", "pose", "kps"]
    }
}
```

对应的年龄性别识别配置infer_age_gender.json，配置"with_postprocess"为false，默认"convert_to_float"为true，即不在InferMethod中进行后处理操作，InferMethod输出中间结果。注意"with_postprocess"的设置需要与workflow配置的method对应。
```json
{
    "with_postprocess": false,
    "model_preprocess":{
        "class_name": "pyramid_roi_resizer_preprocess",
        "config": {
            "roi_process_pipeline": [
                "norm_by_nothing"
            ]
        }
    },
    "model_predict": {
        "model_file_path": "../../models/faceAgeGender.hbm",
        "is_packed_model": false,
        "model_name": "faceAgeGender",
        "run_mode": {
            "bpu_core":1
        }
    },
    "model_post_process": {
        "class_name": "age_gender_postprocess"
    }
}
```

# 4 如何扩展自定义模型
首先用户需要了解需要扩展自定义模型的前后处理，以及编译模型时的输入方式。

若模型编译为`resizer`方式，则预测任务类型是`RoiInferenceEngineTask`，否则任务类型是`TensorInferenceEngineTask`。

## 4.1 扩展预处理
预处理中的主要操作：1) 获取模型输入输出维度大小、数据类型、排布等属性；2) 根据模型类型创建对应的预测任务；3) 解析输入数据，根据需要申请BPU输入、输出内存空间，并将输入数据复制到对应的BPU输入中；4) 返回task预测任务

扩展CustomPreProcess，并实现`Execute`函数，即实现上述主要操作。
```c++
class CustomPreProcess : public PreProcess {
 public:
  explicit CustomPreProcess(Inferencer* infer) : PreProcess(infer) {}
  virtual ~CustomPreProcess() {}

  virtual int Init(const std::string &json_str);

  virtual int Execute(const std::vector<xstream::BaseDataPtr> &input,
                      std::vector<std::shared_ptr<InferenceEngineTask>>& tasks);
};
```

在`PreProcess::GetInstance()`中注册对应的自定义预处理。
```c++
std::shared_ptr<PreProcess> PreProcess::GetInstance(
    std::string class_name, Inferencer* infer) {
  if (class_name == "custom_preprocess") {
    return std::make_shared<CustomPreProcess>(infer);
  } else {
    return nullptr;
  }
}
```

设置配置文件：
```json
{
    "class_name": "custom_preprocess",
    "config": {
    }
}
```

## 4.2 扩展后处理
后处理中的主要操作获取预测任务，取输出结果，进行解析。需要注意的是，若扩展的后处理不需要转浮点操作，则需要在解析完成后，自行将BPU输出内存释放。

扩展CustomPostProcess，并实现`Execute`函数，即实现上述主要操作。
```c++
class CustomPostProcess : public PostProcess {
 public:
  virtual int Init(const std::string &json_str);

  virtual int Execute(
      const std::vector<std::shared_ptr<InferenceEngineTask>> &tasks,
      std::vector<xstream::BaseDataPtr> *frame_result);
};
```

在`PostProcess::GetInstance()`中注册对应的自定义预处理。
```c++
std::shared_ptr<PostProcess> PostProcess::GetInstance(std::string class_name) {
  if (class_name == "custom_postprocess") {
    return std::make_shared<CustomPostProcess>();
  } else {
    return nullptr;
  }
}
```

设置配置文件：
```json
{
    "class_name": "custom_postprocess",
    "xx": "xx"
}
```