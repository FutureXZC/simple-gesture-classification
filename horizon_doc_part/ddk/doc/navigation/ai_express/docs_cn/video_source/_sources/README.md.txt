# 1 简介
video source是一套C++接口，封装了地平线x3系统vio库的功能，支持多平台扩展，例如x3、j3、j5芯片平台。其中内部主要分为vin和vps模块，vin模块和vps模块可以单独使用，也可以组合使用。

## 1.1 内部框架
![video source组件内部结构](./image/video_source.png)
内部主要由VIN(video input)和VPS(video process system)两大模块构成。
   - VIN模块主要是支持接入各种类型的视频源，输出是固定NV12格式的YUV图片。
     - 内部使用了x3芯片中的isp、vdec解码等硬件模块。
     - 输入源目前支持mipi camera、usb camera、feedback回灌、rtsp client等等，用户也可以在此基础上，扩展和修改自己的视频源。
   - VPS模块输入来自VIN的输出(NV12图像)，输出是NV12原图或者Pyramid金字塔图
     - 输出的NV12原图来自ipu裁剪或者缩放后；金字塔图是通过PYM硬件模块的输出
     - 内部包括IPU(image process unit)硬件模块和PYM(pyramid)硬件模块以及GDC模块(用于图像畸变矫正)
  
## 1.2 主要功能 
video source组件支持动态视频处理和静态图片处理
### 1.2.1 动态视频或者静态图片列表处理
  - 支持单路和多路mipi camera视频获取和金字塔输出
  - 支持单路和多路usb camera视频获取和金字塔输出
  - 支持单路和多路回灌，支持jpeg回灌、nv12回灌、video视频回灌(AVI和MP4格式)，内部使用decode硬件解码器，加速解码 (video视频回灌目前还不支持，后面会加入支持)
  - 支持单路和多路rtsp cliet拉流获取和金字塔输出

 ### 1.2.2 静态单张图片处理
   - 支持JPEG单独图片以文件路径方式读入，或者从内存读入。输出原图或者金字塔图
   - 支持NV12图片以文件路径方式读入，或者从内存读入。输出原图或者金字塔图

## 1.3 使用方式
  面对用户主要有两种使用方式：
  1. 支持组件形式单独运行输出，仅依赖系统软件相关动态库。
  2. 支持挂载到xproto总线上，以plugin插件形式使用，输出vio message推送到xproto总线。需要依赖xproto、xstream动态库、系统软件相关动态库。

# 2 依赖库说明
  1. 背景：上述两种功能依赖的库和头文件，都存放在host package压缩包中，它是随每次中间件发版输出的内容。例如host_package_1.1.0.tar.gz。
  2. 使用方式：将host_package_1.1.0.tar.gz解压到当前用户所用开发机的主目录(内部文件夹内容是.horizon文件夹，存放在~/.horizon) 
  3. host_package内容包括：
     - xstream动态库和头文件，提供AI模型集成形成workflow、策略处理和任务调度等功能
     - xproto动态库和头文件，提供多插件消息通信的能力
     - image_utils动态库和头文件，提供了c接口版本的图像处理接口(软件处理)
     - bpu_predict动态库和头文件，提供模型预测的能力
     - appsdk动态库和头文件，提供系统软件相关的能力


# 3 编译和运行
## 3.1 组件形式的使用
### 3.1.1 编译
	   bash make.sh
### 3.1.2 运行
	   编译后，会在当前目录输出output文件夹，该目录下有如下内容：

```shell
.
├── bin
│   └── video_source_sample
├── configs
│   ├── video_source
│   │   └── x3dev
│   │       ├── feedback
│   │       ├── mipi_cam
│   │       ├── rtsp_client
│   │       └── usb_cam
│   ├── x3_video_source.json.fb
│   ├── x3_video_source.json.mipi_cam
│   ├── x3_video_source.json.rtsp
│   └── x3_video_source.json.usb_cam
├── include
│   └── video_source
│       ├── video_source.h
│       └── video_source_type.h
├── lib
│   ├── libvideo_source.so
│   └── sensor
│       ├── libf37.so    # sensor驱动库，与具体使用的sensor相关(如果系统镜像自带驱动库，则忽略)
│       ├── libjxf37_linear.so
│       └── README.md
└── run.sh

```

  将output文件夹挂载到x3设备目录上，直接运行sh run.sh，将会看到如下提示(使用交互式)：
```shell
set default log: [-w]
Choose lunch video source type menu...pick a combo:
	1. video source type
	2. image source type
Which would you like? 
```
支持两种类型的视频源
  - video source type，则表示连续的视频或者静态图片列表(回灌方式)
  - image source type，则表示静态单张图片处理生成金字塔

会提示选择哪个视频类型，例如我们输入1，然后按enter回车键确认
```shell
 You choose 1:video source type 
Choose lunch video source file menu...pick a combo:
	1. single camera: os8a10, 2160P
	2. single camera: os8a10, 1080P
	3. single camera: f37_1080p, 1080P
	4. single camera: usb_cam, 1080P
	5. single rtsp
	6. 1080p feedback
	7. 2160p feedback
Which would you like? 
1
```
接着需要我们选择具体用哪个视频源，我们这边选择1 (os8a10，2160P) mipi sensor为例
```shell
1
 You choose 1:os8a10_2160p 
sensor is os8a10, default resolution 8M, 1080P X3 JPEG Codec...
test type: 0
video source config: ./configs/video_source/x3dev/mipi_cam/x3_mipi_cam_os8a10_2160p_chn0.json
(video_source.cc:218): =========================================================
(video_source.cc:219): VideoSource VERSION: 1.0.4 Thu May 27 16:02:47 2021
(video_source.cc:220): =========================================================
(mipi_cam_vin_module.cc:1111): not surpport sensor type
devId 0 frameDepth 10
(vps_module_hapi.cc:1540): group_id:0 vio_fps:32
(vps_module_hapi.cc:1540): group_id:0 vio_fps:31
(vps_module_hapi.cc:1540): group_id:0 vio_fps:31
(vps_module_hapi.cc:1540): group_id:0 vio_fps:31
```
可以看到os8a10 mipi camera则运行起来了，其中会现在组号为0，fps帧率为31fps
  
如果想运行其他sensor或者回灌，则按照上述方式依次类推。

## 3.2 插件形式的使用
### 3.2.1 编译
```shell
bash make.sh plugin
```
### 3.2.2 运行

编译后，会在当前目录输出output文件夹，该目录下有如下内容：
```shell
.
├── bin
│   └── video_source_plugin_sample
├── configs
│   ├── video_source
│   │   └── x3dev
│   ├── x3_video_source.json.fb
│   ├── x3_video_source.json.mipi_cam
│   ├── x3_video_source.json.rtsp
│   └── x3_video_source.json.usb_cam
├── include
│   └── video_source_plugin
│       └── video_source_plugin.h
├── lib
│   ├── libvideo_source_plugin.so
│   ├── libxproto.so   # 默认会从host package拷贝过来
│   ├── libxstream.so  # 默认会从host package拷贝过来
│   └── sensor
│       ├── libf37.so
│       ├── libjxf37_linear.so
│       └── README.md
└── run.sh
```
将output文件夹挂载到x3设备目录上，直接运行sh run.sh，使用了交互式方式，将会看到提示：
```shell
Choose lunch video source run_mode menu...pick a combo:
log_level: w
Choose lunch video source type menu...pick a combo:
	1. single cam
	2. single feedback
	3. single rtsp
	4. multi cam sync   #目前还不支持，预计后面版本会加入
	5. multi cam async  #目前还不支持
	6. single cam + single feedback  #目前还不支持
Which would you like? 

```
根据提示，选择需要的选项，然后按enter回车键确认选择。

## 3.3 清除
```shell
bash make.sh clean
```
上述命令将会删除生成的目录，例如build目录、output目录

## 3.4 图像调试
  video source支持一些图像调试dump功能，以帮助用户在整个视频通路的各个节点去check图像是否正常。
  - 在output目录下，touch vin_input.txt新建文件, 则会一直dump vin模块的输入，例如usb camera源的jpeg图像。
  - 在output目录下，touch vin_output.txt新建文件，则会dump vin模块输出的nv12图像
  - 在output目录下，touch vps_output.txt新建文件，则会dump vps模块输出的原图或者金字塔图像
  - 如果运行video source plugin sample测试用例，在output目录下，touch pym_output.txt新建文件，则会输出consumer plugin消费插件接收的vio message，dump金字塔图像
  - tips：如果vin_input.txt、vin_output.txt、vps_output.txt文本文件中写入20，则只会dump开始接收的20帧，写入30，则只会dump 30帧，依次类推。

# 4 开发示例
## 4.1 配置文件说明
### 4.1.1 video source plugin插件形式的入口配置
```
{
  "config_index": 0,                                     # 选择confg_0还是config_1
  "board_name": "x3dev",                                 # 开发平台
  "config_0": {
    "produce_name": "panel_camera",                      # 用户自定义产品对象，基于mipi_cam、usb_cam、feedback、rtsp四大基础功能
    "data_type": "mono",                                 # 使用下面的mono还是dual，mono是单路，dual是多路
    "max_vio_buffer": 3,                                 # 上层使用的最大video source buffer个数
    "is_msg_package": 0,                                 # 是否同步，1为多路同步图像到一个message，0为异步推送vio message
    "mono": {
      "channel_id": 0,                                   # 用户指定通道号，用于区分不同的视频源
      "video_source_file": "configs/video_source/x3dev/mipi_cam/x3_mipi_cam_os8a10_2160p_chn0.json" # video source配置文件
    },
    "dual": {
      "channel_id": [0, 1],
      "video_source_file": [
        "configs/video_source/x3dev/mipi_cam/x3_mipi_cam_os8a10_2160p_chn1.json",
        "configs/video_source/x3dev/mipi_cam/x3_mipi_cam_f37_1080p_chn1.json"
      ]
    }
  },
  "config_1": {
    "produce_name": "panel_camera",
    "data_type": "mono",
    "max_vio_buffer": 3,
    "is_msg_package": 0,
    "mono": {
      "channel_id": 0,
      "video_source_file": "configs/video_source/x3dev/mipi_cam/x3_mipi_cam_f37_1080p_chn0.json"
    },
    "dual": {
      "channel_id": [0, 1],
      "video_source_file": [
        "configs/video_source/x3dev/mipi_cam/x3_mipi_cam_f37_1080p_chn0.json",
        "configs/video_source/x3dev/mipi_cam/x3_mipi_cam_f37_1080p_chn1.json"
      ]
    }
  }
}
```

### 4.1.2 video source组件形式的入口配置   
 
 例如x3dev/mipi_cam/x3_mipi_cam_os8a10_2160p_chn0.json

 主要包括VIN和VPS两大模块的配置
```json
{
  "data_source": "mipi_cam",               # 支持mipi_cam、usb_cam、feedback、rtsp四种基础功能
  "channel_id": 0,                         # 用户自定义使用的通道号，用于区分不同的sensor
  "vin_out_en": 0,                         # 支持vin输出的能力，默认关闭输出。如果使能，可以直接利用SDK的接口获取vin输出的nv12图
  "vps_en": 1,                             # vps模块是否使能，包括图像裁剪、金字塔生成，默认使能。如果关闭，vps模块则不会运行。
  "config_file": {
    "vin_config_file": "configs/video_source/x3dev/mipi_cam/vin/x3_vin_os8a10_2160p_chn0.json",   # vin模块的配置文件
    "vps_config_file": "configs/video_source/x3dev/mipi_cam/vps/x3_vps_os8a10_2160p.json"         # vps模块的配置文件
  }
}
```
VIN配置如下，以os8a10为例
```json
{
  "bind_chn_id": -1,                               # -1表示该vin模块的来源是当前自己的camera输出的数据，如果是非负数，则表示来源是其他vin模块的输出数据
  "vin_vps_mode": 1,                               # vin vps模块的连接方式
  "sensor": {
    "sensor_id": 5,                                # sensor的枚举号
    "sensor_plugin_en": 0,                         # 是否是插件形式导入sensor参数配置，默认关闭状态
    "sensor_plugin_path": "./lib/",                # sensor插件库的存放目录
    "sensor_plugin_name": "os8a10_plugin",         # sensor插件库的名称
    "sensor_plugin_type": "linear",                # sensor插件库的类型，支持linear、dol2、dol3模块，根据sensor的配置来决定
    "sensor_port": 0,                              # sensor端口配置，默认为0
    "i2c_bus": 2,                                  # i2c总线，根据具体的硬件配置
    "need_clk": 1,                                 # 是否使用x3输出的clk供給sensor子板
    "serdes_index": 0,                             # 使用FPD-Link线束的解串形式的sensor的索引号
    "serdes_port": 0,                              # 解串的端口号
    "extra_mode": 0                                # 扩展模式，默认为0为正常模式。如果extra_mode为1，需要与bind_chn_id参数配合使用，用于输入数据来源于其他的sensor
  },
  "mipi": {
    "host_index": 1,                               # mipi host索引号
    "vc_index": 0,                                 # 虚拟通道索引号
    "dol2_vc_index": 1                             # dol2的虚拟通道起始索引号
  },
  "sif": {
    "need_md": 0,                                  # 是否启用sif功能的motion detect，默认关闭
    "sif_out_buf_num": 8                           # sif->ddr的输出buffer个数配置
  },
  "isp": {
    "temper_mode": 2,                              # 3d降噪模式等级，设置为0或者1是不使能，设置2和3分别是temper2和temper3等级，默认是temper2等级
    "isp_3a_en": 1,                                # isp 3a功能的使能，1为打开，0为关闭，默认打开
    "isp_out_buf_num": 5                           # isp->ddr的输出buffer个数配置
  },
  "dwe": {
    "ldc": {
      "ldc_en": 0                                  # ldc模块是否使能，默认关闭
    },
    "dis": {
      "dis_en": 0                                  # dis模块是否使能，默认关闭
    }
  }
}
```
VPS配置如下，以os8a10为例
```json
{
  "debug": {
    "vps_dump_num": 0,                             # 是否起开vps图像dump的功能，0为不dump，大于0则是dump多少帧图像，5为5帧图像
    "vps_layer_dump": 4                            # dump金字塔哪一层图像，4为第4层，20为第20层，24则dump所有层使能的金字塔图像
  },
  "input": {
    "width": 3840,                                 # vps输入的图像分辨率，如果使能了vin模块，则应该与vin模块的输出分辨率一致
    "height": 2160
  },
  "gdc": {
    "gdc0": {
      "enable": 1,                                 # 使能gdc0模块
      "gdc_type": 1,                               # gdc的类型，0为非法模式，1为isp->ddr->gdc，2为ipu_chn->ddr->gdc，3为pym->ddr->gdc
      "frame_depth": 2,                            # gdc的输入buffer个数，即vps组的个数
      "rotate": 0,                                 # gdc旋转，0为不旋转，1为90度旋转，2为180度旋转，3为270度旋转
      "path": "/app/bin/hapi_xj3/os8a10.bin",      # gdc文件的路径
      "bind_ipu_chn": -1                           # 如果gdc_type为2，则这里表示绑定到ipu的哪个通道
    },
    "gdc1": {
      "enable": 0,                                 # gdc1模块，功能与gdc0一样
      "gdc_type": 2,
      "frame_depth": 2,
      "rotate": 0,
      "path": "",
      "bind_ipu_chn": -1
    }
  },
  "ipu": {
    "chn0": {
      "ipu_chn_en": 0,                             # 使能ipu通道，图像仅经过ipu硬件
      "pym_chn_en": 0,                             # 使能pym通道，图像经过金字塔模块
      "roi_en": 0,                                 # roi裁剪功能是否使能，ipu通道使能才有效
      "roi_x": 0,                                  # roi裁剪的左上角x坐标，ipu通道使能才有效
      "roi_y": 0,                                  # roi裁剪的左上角y坐标，ipu通道使能才有效
      "roi_w": 3840,                               # roi裁剪的左上角roi宽度，ipu通道使能才有效
      "roi_h": 2160,                               # roi裁剪的左上角roi高度，ipu通道使能才有效
      "scale_w": 3840,                             # ipu输出的图像缩放宽度，ipu通道使能才有效
      "scale_h": 2160,                             # ipu输出的图像缩放高度，ipu通道使能才有效
      "frame_depth": 8,                            # ipu->ddr的buffer个数，ipu通道使能才有效
      "timeout": 2000                              # 获取ipu输出图像的超时时间
    },
    "chn1": {
      "ipu_chn_en": 0,
      "pym_chn_en": 0,
      "roi_en": 0,
      "roi_x": 0,
      "roi_y": 0,
      "roi_w": 3840,
      "roi_h": 2160,
      "scale_w": 3840,
      "scale_h": 2160,
      "frame_depth": 8,
      "timeout": 2000
    },
    "chn2": {
      "ipu_chn_en": 0,
      "pym_chn_en": 0,
      "roi_en": 0,
      "roi_x": 0,
      "roi_y": 0,
      "roi_w": 3840,
      "roi_h": 2160,
      "scale_w": 3840,
      "scale_h": 2160,
      "frame_depth": 8,
      "timeout": 2000
    },
    "chn3": {
      "ipu_chn_en": 0,
      "pym_chn_en": 0,
      "roi_en": 0,
      "roi_x": 0,
      "roi_y": 0,
      "roi_w": 3840,
      "roi_h": 2160,
      "scale_w": 3840,
      "scale_h": 2160,
      "frame_depth": 8,
      "timeout": 2000
    },
    "chn4": {
      "ipu_chn_en": 0,
      "pym_chn_en": 0,
      "roi_en": 0,
      "roi_x": 0,
      "roi_y": 0,
      "roi_w": 3840,
      "roi_h": 2160,
      "scale_w": 3840,
      "scale_h": 2160,
      "frame_depth": 8,
      "timeout": 2000
    },
    "chn5": {
      "ipu_chn_en": 0,
      "pym_chn_en": 0,
      "roi_en": 0,
      "roi_x": 0,
      "roi_y": 0,
      "roi_w": 3840,
      "roi_h": 2160,
      "scale_w": 3840,
      "scale_h": 2160,
      "frame_depth": 8,
      "timeout": 2000
    },
    "chn6": {
      "ipu_chn_en": 1,
      "pym_chn_en": 1,
      "roi_en": 0,
      "roi_x": 0,
      "roi_y": 0,
      "roi_w": 3840,
      "roi_h": 2160,
      "scale_w": 3840,
      "scale_h": 2160,
      "frame_depth": 8,
      "timeout": 2000
    }
  },
  "pym": {
    "pym_ctrl_config": {
      "frame_id": 1,                                 # frame_id起始帧号
      "ds_layer_en": 23,                             # 金字塔down scale的使能金字塔层数，23则为0~23层全部使能，5为0~5层使能，取值为4~24
      "ds_uv_bypass": 0,                             # 金字塔down scale uv分量bypass，默认为0则说明使用uv分量(金字塔层使能的情况下才有效)
      "us_layer_en": 0,                              # 金字塔up scale金字塔层是否使能，默认为0关闭
      "us_uv_bypass": 0,                             # 金字塔up scale uv分量bypass，默认为0则说明使用uv分量(金字塔层使能的情况下才有效)
      "frame_depth": 5,                              # pym->ddr的buffer个数
      "timeout": 2000                                # 获取金字塔帧的超时时间
    },
    "pym_ds_config": {
      "roi_x_1": 0,                                  # roi 区域相对于对应基本层左顶点坐标,需为偶数
      "roi_y_1": 0,                                  # roi 区域相对于对应基本层左顶点坐标，需为偶数
      "roi_w_1": 0,                                  # roi 区域大小,不能超过基本层大小，需为偶数
      "roi_h_1": 0,                                  # roi 区域大小,不能超过基本层大小，需为偶数
      "factor_1": 0,                                 # roi 缩放系数 64/(64 + factor),factor 为0时，表示disable 该层缩放，factor 取值范围 0--63
      "roi_x_2": 0,
      "roi_y_2": 0,
      "roi_w_2": 0,
      "roi_h_2": 0,
      "factor_2": 0,
      "roi_x_3": 0,
      "roi_y_3": 0,
      "roi_w_3": 0,
      "roi_h_3": 0,
      "factor_3": 0,
      "roi_x_5": 0,
      "roi_y_5": 0,
      "roi_w_5": 1920,
      "roi_h_5": 1080,
      "factor_5": 32,
      "roi_x_6": 0,
      "roi_y_6": 0,
      "roi_w_6": 0,
      "roi_h_6": 0,
      "factor_6": 0,
      "roi_x_7": 0,
      "roi_y_7": 0,
      "roi_w_7": 0,
      "roi_h_7": 0,
      "factor_7": 0,
      "roi_x_9": 0,
      "roi_y_9": 0,
      "roi_w_9": 960,
      "roi_h_9": 540,
      "factor_9": 32,
      "roi_x_10": 0,
      "roi_y_10": 0,
      "roi_w_10": 0,
      "roi_h_10": 0,
      "factor_10": 0,
      "roi_x_11": 0,
      "roi_y_11": 0,
      "roi_w_11": 0,
      "roi_h_11": 0,
      "factor_11": 0,
      "roi_x_13": 0,
      "roi_y_13": 0,
      "roi_w_13": 0,
      "roi_h_13": 0,
      "factor_13": 0,
      "roi_x_14": 0,
      "roi_y_14": 0,
      "roi_w_14": 0,
      "roi_h_14": 0,
      "factor_14": 0,
      "roi_x_15": 0,
      "roi_y_15": 0,
      "roi_w_15": 0,
      "roi_h_15": 0,
      "factor_15": 0,
      "roi_x_17": 0,
      "roi_y_17": 0,
      "roi_w_17": 0,
      "roi_h_17": 0,
      "factor_17": 0,
      "roi_x_18": 0,
      "roi_y_18": 0,
      "roi_w_18": 0,
      "roi_h_18": 0,
      "factor_18": 0,
      "roi_x_19": 0,
      "roi_y_19": 0,
      "roi_w_19": 0,
      "roi_h_19": 0,
      "factor_19": 0,
      "roi_x_21": 0,
      "roi_y_21": 0,
      "roi_w_21": 0,
      "roi_h_21": 0,
      "factor_21": 0,
      "roi_x_22": 0,
      "roi_y_22": 0,
      "roi_w_22": 0,
      "roi_h_22": 0,
      "factor_22": 0,
      "roi_x_23": 0,
      "roi_y_23": 0,
      "roi_w_23": 0,
      "roi_h_23": 0,
      "factor_23": 0
    },
    "pym_us_config": {
      "roi_x_0": 0,
      "roi_y_0": 0,
      "roi_w_0": 0,
      "roi_h_0": 0,
      "factor_0": 0,
      "roi_x_1": 0,
      "roi_y_1": 0,
      "roi_w_1": 0,
      "roi_h_1": 0,
      "factor_1": 0,
      "roi_x_2": 0,
      "roi_y_2": 0,
      "roi_w_2": 0,
      "roi_h_2": 0,
      "factor_2": 0,
      "roi_x_3": 0,
      "roi_y_3": 0,
      "roi_w_3": 0,
      "roi_h_3": 0,
      "factor_3": 0,
      "roi_x_4": 0,
      "roi_y_4": 0,
      "roi_w_4": 0,
      "roi_h_4": 0,
      "factor_4": 0,
      "roi_x_5": 0,
      "roi_y_5": 0,
      "roi_w_5": 0,
      "roi_h_5": 0,
      "factor_5": 0
    }
  }
}
```
## 4.2 接口介绍
### 4.2.1 video source关键数据结构
1. video source目前仅支持以下的图像类型，如果用户需要扩展，可以自行添加
2. 输出的图像数据结构，只有原图ImageFrame数据结构，以及金字塔PyramidFrame数据结构
3. 针对FrameInfo信息的说明：
   -  channel_id是针对不同video设备而言，由用户自定义，一般从0开始，最大为7 (最大同时支持8路)
   - 数据从进入到vin module到从vps输出，同一帧图像frame_id唯一，一直跟随这一帧数据的流向
   - time_stamp_字段只有video 设备是mipi camera时候才有效，它实际是硬件sif根据晶振打上去的时间
   - system_time_stamp_字段是linux系统的时间，它是产生原图数据时的系统时间
   - buf_index_是vin module内部buffer的索引，防止用户同时获取几帧图像，在释放时并不是按照获取图像顺序导致释放错误
   - vps_chn_是由用户指定获取的IPU通道输出的数据(ipu channel号是从0~6，其中chn0~chn5是offline模式，可以输出原图到ddr; chn6是online模式，无法直接获取原图)
4. 针对ImageFrame原图的说明：
   - src_context_字段是内部的数据结构，包括原图相关的更多信息
5. 针对PyramidFrame金字塔图的说明：
   - src_info_是金字塔0层的输出，一般和金字塔的输入一样
   - bl_ds_是双线性输出，对于x3是表示全部最大24层缩放的输出；对于j5是仅仅表示最大输出5层双线性金字塔层
   - gs_ds_仅仅是针对j5高斯金字塔输出而言，最大输出5层
   - roi_ds_是针对j5的双线性、高斯金字塔层中的roi模块
   - roi_us_是金字塔放大层。x3是最大是6层，j5最大为1层
   - pym_context_和src_context_字段是内部的数据结构，包括更多的金字塔和原图信息

```c++
enum HorizonVisionPixelFormat {
    kHorizonVisionPixelFormatNone = 0,
    kHorizonVisionPixelFormatRaw,
    kHorizonVisionPixelFormatYUY2,
    kHorizonVisionPixelFormatNV12,
    kHorizonVisionPixelFormatPYM,
    kHorizonVisionPixelFormatJPEG = 30,  // hard codec support
    kHorizonVisionPixelFormatMJPEG,      // hard codec support
    kHorizonVisionPixelFormatH264,       // hard codec support
    kHorizonVisionPixelFormatH265,       // hard codec support
    kHorizonVisionPixelFormatMax
};

struct FrameInfo {
  virtual ~FrameInfo() {}
  HorizonVisionPixelFormat pixel_format_ =
    HorizonVisionPixelFormat::kHorizonVisionPixelFormatNone;
  uint32_t channel_id_ = 0;
  uint64_t time_stamp_ = 0;  // HW time stamp
  // struct timeval tv_;  //system time
  uint64_t system_time_stamp_ = 0;  // system time
  uint64_t frame_id_ = 0;
  uint32_t buf_index_ = 0;
  uint32_t vps_chn_ = 0;
};

struct ImageLevelInfo {
  uint16_t width;
  uint16_t height;
  uint16_t stride;
  uint64_t y_paddr;
  uint64_t c_paddr;
  uint64_t y_vaddr;
  uint64_t c_vaddr;
};

// source image frame: nv12 or raw format
struct ImageFrame : public FrameInfo {
  ImageFrame() {
    pixel_format_ = HorizonVisionPixelFormat::kHorizonVisionPixelFormatNV12;
  }
  ImageLevelInfo src_info_ = { 0 };
  void *src_context_ = nullptr;
};

// pyramid image frame, compatible xj3 and j5
struct PyramidFrame : public FrameInfo {
  PyramidFrame() {
    pixel_format_ = HorizonVisionPixelFormat::kHorizonVisionPixelFormatPYM;
  }

  /**
   * 1. src_info is source image output for xj3 or j5.
   *    a) pyramid 0-layer ouput for xj3
   *    b) source image ouput without pyramid process for j5
   * 2. bl_ds is bilinear downscale for xj3 or j5.
   *    a) xj3 including all bilinear base layer and roi layer.
   *    b) j5 only for bilinear base layer.
   * 3. gs_ds is gauss downscale only for j5, including all gauss base layer
   * 4. roi_ds is roi downscale only for j5, including some downscale roi layer
   *    which input based on either of them as follow:
   *    a) bilinear pyramid certain some base layer
   *    b) gauss pyramid certain some base layer
   *    c) source image.
   * 5. roi_us is roi upscale for xj3 or j5.
   *    a) including some upscale roi layer
   *       which base on as well as roi_ds for j5.
   *    b) it is independent module for xj3.
   */
  ImageLevelInfo src_info_ = { 0 };
  // max bilinear layer is 24 for xj3 or 5 for j5
  std::vector<ImageLevelInfo> bl_ds_;
  // max gauss layer is 5 for j5
  std::vector<ImageLevelInfo> gs_ds_;
  // max roi downscale is 6 for j5
  std::vector<ImageLevelInfo> roi_ds_;
  // max roi upscale layer is 6 for xj3 or 1 for j5
  std::vector<ImageLevelInfo> roi_us_;
  // pyramid context for xj3 or j5
  void *pym_context_ = nullptr;
  // source context for j5
  void *src_context_ = nullptr;
};
```

### 4.2.2 vide source组件接口介绍
video source对象的构造函数主要有两种：
   - video source type类型。用户需要指定channel id号，用于在同时接入多路视频源时，区分不同的视频源，config_file是video source的入口配置
   - image source type类型。没有channel_id号，默认是同步获取，用户可以根据需要使用异步获取
如下是VideoSource对象对外的接口：
```c++
class VideoSource {
 public:
  VideoSource() = delete;
  /**
   * video source class. including
   * -- a) mipi camera
   * -- b) usb camera
   * -- c) feedback(nv12 image list, jpeg image list)
   * -- d) rtsp client
   */
  explicit VideoSource(const int &channel_id,
      const std::string &config_file);
  /**
   * video source class. only including
   * -- a) feedback(single nv12 image or jpeg image)
   */
  explicit VideoSource(const std::string &config_file,
      bool is_sync_mode = true);
  ~VideoSource();
  int Init();
  int DeInit();
  int Start();
  int Stop();

  VideoSourceType GetSourceType() { return source_type_; }
  void SetLoggingLevel(VideoSourceLogLevel &log_level);
  /**
   * @description: Get one nv12 image frame data from diffent vin(video_input)
   * module, such as mipi_cam, usb_cam, feedback, rtsp_stream and so on.
   * @param[in]  vin_nv12_image is nullptr
   * @param[out] vin_nv12_image is shared_ptr which including image data
   * @return The interface returns 0 to indicate that the function is
   * successful, otherwise it indicates that the return failed.
   */
  int GetVinImageFrame(OUT std::shared_ptr<ImageFrame> &nv12_image);
  /**
   * @description: Free one or more nv12 image frame data from vin module
   * @param[in]  vin_nv12_image is shared pointer being used by user
   * @return The interface returns 0 to indicate that the function is
   * successful, otherwise it indicates that the return failed.
   */
  int FreeVinImageFrame(IN std::shared_ptr<ImageFrame> &nv12_image);
  /**
   * @description: Get one or more nv12 images frame data from vps(video
   * processsing system) hardware module in xj3 or j5.If soc is xj3,
   * image frame data is derived from ipu multi-channel ouput in vps.
   * @param[in]  vps_nv12_image is nullptr
   * @param[out] vps_nv12_image is shared_ptr which including image data
   * @return The interface returns 0 to indicate that the function is
   * successful, otherwise it indicates that the return failed.
   */
  int GetVpsImageFrame(OUT std::vector<std::shared_ptr<ImageFrame>>
      &nv12_image_list);
  /**
   * @description: Free one or more nv12 image frame data from vps module
   * @param[in]  vps_nv12_image is shared pointer being used by user
   * @return The interface returns 0 to indicate that the function is
   * successful, otherwise it indicates that the return failed.
   */
  int FreeVpsImageFrame(IN std::vector<std::shared_ptr<ImageFrame>>
      &nv12_image_list);
  /**
   * @description: Get one pyramid image frame data from pyramid
   * hardware module in xj3 or j5.
   * @param[in]  pym_image is nullptr
   * @param[out] pym_image is shared_ptr which including pyramid data
   * @return The interface returns 0 to indicate that the function is
   * successful, otherwise it indicates that the return failed.
   */
  int GetPyramidFrame(OUT std::shared_ptr<PyramidFrame> &pym_image);
  /**
   * @description: Free pyramid frame data from pyramid module
   * @param[in]  pym_image is shared pointer being used by user
   * @return The interface returns 0 to indicate that the function is
   * successful, otherwise it indicates that the return failed.
   */
  int FreePyramidFrame(IN std::shared_ptr<PyramidFrame> &pym_image);

  bool GetVinOutEnable() { return vin_out_en_; }
  bool GetVpsEnable() { return vps_en_; }
  int ReadImage(IN const std::string &path,
      IN const uint32_t &width, IN const uint32_t &height,
      IN const HorizonVisionPixelFormat &pixel_format);
  int ReadImage(IN char* data, IN const uint32_t &len,
      IN const uint32_t &width, IN const uint32_t &height,
      IN const HorizonVisionPixelFormat &pixel_format);
....
};
```

## 4.3  示例程序
### 4.3.1 video source type动态视频示例

```c++
  int channel_id = 0;
  auto video_source = std::make_shared<VideoSource>(channel_id, config_file);

  video_source->SetLoggingLevel(level);

  std::cout << "video source config: " << config_file << std::endl;
  ret = video_source->Init();
  if (ret) {
    std::cout << "video source init failed, ret: " << ret << std::endl;
    return ret;
  }
  ret = video_source->Start();
  if (ret) {
    std::cout << "video source start failed, ret: " << ret << std::endl;
    return ret;
  }

  bool vin_out_en = video_source->GetVinOutEnable();
  bool vps_en = video_source->GetVpsEnable();
  while (!g_ctx.exit) {
    // 1. get vin output
    if (vin_out_en == true) {
      std::shared_ptr<ImageFrame> vin_image = nullptr;
      ret = video_source->GetVinImageFrame(vin_image);
      if (ret) {
        std::cout << "get vin image frame failed, ret: " << ret << std::endl;
      }
      ret = video_source->FreeVinImageFrame(vin_image);
      if (ret) {
        std::cout << "free vin image frame failed, ret: " << ret << std::endl;
      }
    }

    // 2. get vps output
    if (vps_en == true) {
      std::shared_ptr<PyramidFrame> pym_image = nullptr;
      ret = video_source->GetPyramidFrame(pym_image);
      if (ret) {
        std::cout << "get pyramid frame failed, ret: " << ret << std::endl;
      }
      ret = video_source->FreePyramidFrame(pym_image);
      if (ret) {
        std::cout << "free pyramid frame failed, ret: " << ret << std::endl;
      }
    }
  }

  std::cout << "video source sample quit\n\n" << std::endl;
  ret = video_source->Stop();
  if (ret) {
    std::cout << "video source stop failed, ret: " << ret << std::endl;
    return ret;
  }
  ret = video_source->DeInit();
  if (ret) {
    std::cout << "video source deinit failed, ret: " << ret << std::endl;
    return ret;
  }
```
注意，该config file是video source的入口配置，例如x3_mipi_cam_os8a10_1080p_chn0.json
```shell
{
  "data_source": "mipi_cam",
  "channel_id": 0,
  "vin_out_en": 0,
  "vin_frame_depth": 8,
  "vps_en": 1,
  "config_file": {
    "vin_config_file": "configs/video_source/x3dev/mipi_cam/vin/x3_vin_os8a10_2160p_chn0.json",
    "vps_config_file": "configs/video_source/x3dev/mipi_cam/vps/x3_vps_os8a10_1080p.json"
  }
}
```

### 4.3.2 image source type静态图片示例

```c++
 auto video_source = std::make_shared<VideoSource>(config_file);
  video_source->SetLoggingLevel(level);

  ret = video_source->ReadImage(image_name, width, height, pixel_format);
  if (ret) {
    std::cout << "read image: " << image_name
      << " failed, ret: " << ret << std::endl;
    return ret;
  }
  bool vin_out_en = video_source->GetVinOutEnable();
  bool vps_en = video_source->GetVpsEnable();
  // 1. get vin output
  if (vin_out_en == true) {
    std::shared_ptr<ImageFrame> vin_image = nullptr;
    ret = video_source->GetVinImageFrame(vin_image);
    if (ret) {
      std::cout << "get vin image frame failed, ret: " << ret << std::endl;
      return ret;
    }
    ret = video_source->FreeVinImageFrame(vin_image);
    if (ret) {
      std::cout << "free vin image frame failed, ret: " << ret << std::endl;
      return ret;
    }
  }

  // 2. get vps output
  if (vps_en == true) {
    std::shared_ptr<PyramidFrame> pym_image = nullptr;
    ret = video_source->GetPyramidFrame(pym_image);
    if (ret) {
      std::cout << "get pyramid frame failed, ret: " << ret << std::endl;
      return ret;
    }
    ret = video_source->FreePyramidFrame(pym_image);
    if (ret) {
      std::cout << "free pyramid frame failed, ret: " << ret << std::endl;
      return ret;
    }
  }
```
注意，静态图片config_file固定使用 configs/video_source/x3dev/feedback/x3_image_feedback.json
 ```json
 {
  "data_source": "feedback",
  "vin_out_en": 1,
  "vin_frame_depth": 3,
  "vps_en": 1,
  "config_file": {
    "vps_config_file": [   
      // 默认提供4种VPS配置文件模板，video source组件内部会自动根据用户图像输入分辨率来选择合适的vps配置文件，无需用户指定(如果vps配置不满足用户需要，可以自己添加或者修改)
      "configs/video_source/x3dev/feedback/vps/x3_vps_feedback_640_480.json",
      "configs/video_source/x3dev/feedback/vps/x3_vps_feedback_720p.json",
      "configs/video_source/x3dev/feedback/vps/x3_vps_feedback_1080p.json",
      "configs/video_source/x3dev/feedback/vps/x3_vps_feedback_2160p.json"
    ]
  }
}
 
 ```

 # 5 videosource设计原理
上面的章节描述的video source层的接口和使用方式，相当于是从用户角度来阐述。

本章节将描述video source层以下的设计原理
## 5.1 vin module
vinmodule内部包括mipi_cam、usb_cam、feedback、rtsp等视频源，支持用户扩展其他视频源。内部同时集成了一个x3 decodec解码器，用于加速编码数据的解码


### 5.1.1 vin module类的继承关系
1. vin module是基类, 接口Init()、DeInit()、Start()、Stop()均由子类来实现。
2. vin module内部由自己的VinInit()、VinDeInit()、VinStart()、VinStop()接口，主要是用于内部的buffer管理和解码器的管理。
3. vin module子类(各种video设备)与vinmodule基类对接的入口是InputData()函数。该接口函数是将各种类型的数据送入到vinmodule，由vinmodule来统一管理和消费。
4. vin module的输出是nv12格式的图像。
5. 如下是vin module继承关系
![vin module继承关系内部结构](./image/vinmodule继承关系.png)

### 5.1.2 vin module初始化
vin module初始化采用动态加载过程。只有当vin module收到第一帧数据后，才开始进行vin modue本身的init和start操作。这种动态加载的有如下优势：
1. video设备在运行过程中可能会改变输出格式或者分辨率，这样整个video source系统不需要退出进程重新启动，而快速自动适配重新加载整个vin module设备，提升了系统的灵活性
2. 针对于rtsp源的设备，实际用户在拉流的过程中，并不需要知道所要拉流的分辨率，只有再收到视频后，才获取到分辨率。这种动态加载也大大增强的系统实时性。
3. 如下是vin module的初始化流程 (vps模块也采用了动态加载，跟随vin设备的输出而动态切换系统所需的参数)
![vin module初始化](./image/初始化流程.png)

### 5.1.3 vin module数据流向
1. 各种类型的video设备源对象(mipi camera不走该vin module模块)，在自己的接口函数中获取不同的视频数据，然后通过vin module提供的InputData()接口函数，将数据传输到vin module对象中。
2. 在vin module对象中有一个数据缓存池，用于缓存原始的数据(例如H264、H265、JPEG或者yuv数据)，数据缓冲池buffer的最大个数在配置文件中由用户指定，默认是8个(如果8个buffer数据满了，则会自动将最前面一帧buffer的数据给drop掉)。
3. 经过vin module内部的解码或者图像处理之后，将输出nv12图像，图像放入vin module管理的buffer队列中。
4. 如果用户在配置文件中使能了vps模块，则数据会自动流转到vps模块进行相应的处理。如果用户没有使能vps模块，则数据将在vin module中截止。
5. vin module也提供了输出处理完的nv12原图的接口，供用户获取

![vin module数据流向](./image/vin数据流向.png)

### 5.1.4 vin module buffer轮转
vin module内部管理使用了三种队列状态来管理frame数据。frame buffer的个数由用户在配置文件中指定。

1. vin module初始化后，利用ION申请vin buffer(会分配连续的物理地址和虚拟地址)，同时带地址vin Buffer的结构体都推进FreeQueue队列中
2. 一帧数据获取后(如果是编码数据，需要解码为nv12)，从free queue中pop出一个buffer，拷贝nv12数据到buffer中；如果使能了vps，则同时send 该frame到vps，最后将该buffer推进Done Queue队列中。
3. Done Queue buffer是完成数据的buffer队列，有三种情况会从该buffer队列中pop出来
   - 当done buffer满了后，最前面的第一帧buffer将被pop出，同时推送进FreeQueue队列中 (用户不取buffer，导致done queue满了) 
   - 检测到Free Queue的长度为空时，从Done Queue中pop最前面一帧buffer推进FreeQueue中 (用户buffer不及时释放，导致无free queue可用，而此时done queue未满)
   - 如果上层用户主动从VIN获取数据，最前面的第一帧buffer将被pop出，同时推送进UserQueue队列中
4. UserQueue队列是用户正在使用的buffer状态，此时需要用户主动调用FreeVinImageFrame()函数，才会将buffer返回给free queue队列
5. 对于各个Queue队列的长度说明：
   - FreeQueue的最大长度为：用户设置的buffer数量+2
   - DoneQueue的最大长度为：用户设置的buffer数量+1
   - UserQueue的最大长度为：用户设置的buffer数量+0

![vin module buffer轮转](./image/vin_buffer轮转.png)

### 5.1.5 vin module内置解码器
1. vin module内部使用了x3内部自带的硬件解码器，支持H264、H265、JPEG、MJPEG的解码，解码分辨率最大支持4K.
2. vin module内部的解码器支持创建多通道解码(每个通道对应一个视频源)，同一台设备JPEG/MJPEG最大支持64路;H265/H265最大支持32路。硬件是分时复用
3. 解码器通道采用有名管理进行统一分配和管理(支持多进程)

## 5.2 vps module
vps模块内部包括ipu、gdc、pym三个模块。
  - ipu支持图像的缩小、放大、裁剪、帧率控制配置。chn0~chn4是缩小，chn5是放大，chn6是online→pym模式，输入和输出支持online和offline模式
  - gdc支持图像旋转、矫正、镜像功能，输入和输出必须是offline模式
  - pym生成金字塔图像，输入支持online和offline，输出一般是offline

如下是vps module内部硬件结构

  ![vps module内部硬件结构](./image/vps硬件说明.png)

### 5.2.1 vps module继承关系
vps module内部包括vps module继承以及VpsModuleHapi子类，其中VpsModuleHapi子类使用了系统软件的x3 Hapi接口来进行使用。
 ![vps module继承关系](./image/vpsmodule继承关系.png)

 注意：
 1. vps module同时支持扩展j3 VAPI接口以及J5接口。
 2. vin->vps之间的数据传递是通过SendFrame接口来完成(mipi_camera设备除外)

### 5.2.1 vps module group和channel说明
1. vps module在同一台设备上支持最大创建8个vps group同时运行(硬件是通过分时复用)，vps group是虚拟的概念。
2. vps group组号是通过有名管道进行分配和管理（支持多进程）
3. vps module内部包括6个ipu channel硬件通道(chn0~chn5)，其中chn0~chn4是缩放通道(支持crop裁剪，先裁剪再缩放)，chn5是放大通道，chn6是虚拟通道(与chn2实际是同一个硬件设备，只是它是online模式到pyramid金字塔)，其余chn0~chn5均是offline模式到pyramind金字塔
4. online和offlime说明
   - online模式到金字塔含义是chn通道输出的数据直接送入金字塔模块进行处理，不经过ddr
   - offline模式到金字塔含义是chn通道输出的数据先写入ddr，然后再从ddr读入到金字塔进行处理

### 5.2.2 vps输出说明
vps module支持输出两种类型的数据：
1. ipu输出的原图数据(可能经过裁剪或者缩放)，通过GetFrame()接口获取
2. pyramind输出的金字塔数据(默认基础层全开,roi层根据需要用户在配置文件中获取)，通过GetPyramidFrame()接口获取
3. vps模块实际也是动态加载的，在vps配置文件中，用户可以写入一组vps配置文件，然后vps根据vin输出的分辨率，来选择合适的vps配置文件来进行动态加载，如果找不到合适vps配置文件，则会报错退出

### 5.3 vin-vps场景
vin->vps的配置灵活多变，默认video source已经配置号，无法用户关心。而对于高阶用户，需要修改自己的vin->vps配置，需要了解此章节。
1. 对于mipi camera设备，vin->vps可以是online，也可以是offline模式。如果是online模式，下面条件需要全部满足：
   - 单路camera设备
   - 如果使能isp，则必须使能ldc(镜头畸变矫正)模块
   - 如果不使能isp，则sif可以直接online到ipu模块

如下是典型的mipi-camera的vin->vps场景的经过各个模块的数据流
![mipi_camera数据流向](./image/mipi_camera数据流向.png)

2. 对于非mipi caeram设备，vin->vps之间是offline的，因为vinmodule产生的数据均先存放在buffer queue中，然后再通过send frame to vps，从ddr读入vps模块中
3. 下面是几种常见的vin->vps场景(实线是数据online模式，虚线是offline模式)
   - 第一种是典型的mipi camera模式，vin->vps支持online或者offline，vps输出支持ipu通道输出和金字塔输出
   - 第二种是vin->vps offline模式，输出ipu chn0缩放输出和 chn5放大输出
   - 第三种是vin->vps offline模式，vps使用了gdc进行图像畸变矫正，ipu chn2缩放输出
   - 第四种是vin->vps offline模式，vps使用了gdc进行图像畸变矫正，pyramid金字塔输出

![vin-vps场景](./image/vin-vps场景.png)

