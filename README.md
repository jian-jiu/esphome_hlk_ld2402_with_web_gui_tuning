# esphome-hlk-ld2402-with-web-gui-tuning
ESPHome外部组件-海凌科LD2402雷达传感器，自带web-gui调参

A ESPhome External Component Working With HLK-LD2402 Radar Sensor. Tuning with build-in web gui

！！！由于为了支持esp8266修改代码后 未测试esp32,请注意一下！！！

## 使用说明：
* 雷达固件版本需高于或等于v3.3.5,使用官方上位机连接到雷达uart来检查固件及ota固件
* 仅提供传感器类HA实体(距离、人在、固件版本、工作模式等)，所有调参实体集中到web-gui
* 没有自动门限生成功能
* 在esphome 2026.4.5上测试通过
  ```yaml
  # esp32 示例(调整看门狗和任务堆大小防止崩溃)
  esp32:
    board: esp32-c3-devkitm-1
    variant: esp32c3
    framework:
      type: esp-idf
      sdkconfig_options:
        CONFIG_ESP_TASK_WDT_TIMEOUT_S: "30"
        CONFIG_ESP_INT_WDT_TIMEOUT_MS: "800"
      advanced:
        loop_task_stack_size: 10240
  ```
* 100% AI Coding

## 界面截图
* HA实体
  <img width="344" height="171" alt="image" src="https://github.com/user-attachments/assets/a772bc08-965b-43f1-9026-e1af5b18d4b0" />
  <img width="315" height="107" alt="image" src="https://github.com/user-attachments/assets/103855b2-38f1-4175-9c6e-4e58c3946b29" />
* web-gui
* 
   <img src="https://github.com/jian-jiu/esphome_hlk_ld2402_with_web_gui_tuning/blob/main/web-gui.webp" />

## 配置示例
```
web_server:
  port: 80
  auth:
    username: !secret username
    password: !secret password

external_components:
  - source:
      type: git
      url: https://github.com/jian-jiu/esphome_hlk_ld2402_with_web_gui_tuning
      ref: main
    components: [ld2402]
    refresh: always

uart:
  id: uart_ld2402
  tx_pin: GPIO6   #your uart tx pin
  rx_pin: GPIO7  #your uart rx pin
  rx_buffer_size: 2048 # 根据需要调整缓冲区大小
  baud_rate: 115200
  parity: NONE
  stop_bits: 1
  data_bits: 8  

ld2402:
  id: ld2402_radar
  uart_id: uart_ld2402

binary_sensor:
  - platform: ld2402
    ld2402_id: ld2402_radar
    name: "Occupancy"
    device_class: occupancy

  - platform: ld2402
    ld2402_id: ld2402_radar
    name: "电源干扰报警"
    type: interference

sensor:
  - platform: ld2402
    ld2402_id: ld2402_radar
    distance:
      name: "Target Distance"
      filters:
          - throttle: 2s  
text_sensor:
  - platform: ld2402
    ld2402_id: ld2402_radar
    firmware_version:
      name: "LD2402 Firmware"
      icon: "mdi:chip"
      entity_category: "diagnostic"
    work_mode:
      name: "LD2402 Work Mode"
      icon: "mdi:cog-play"
      entity_category: "diagnostic"
```
## web调参
* 访问设备IP:web_port/config,进入调参界面
* 实时能量需要先开启工程模式，调试完记得关闭工程模式
* 任何修改都记得保存到flash来持久化

## 已知问题
* 工程模式下特别容易出现 Command error 现象(导致命令执行失败)m,目前不清楚原因.建议调参时先关闭工程模式,可大幅提高命令成功率
* 保存配置后 重新 加载或者刷新界面容易导致之前的配置没生效(因为需要加载配置)，实际已生效(也可能因为上面的错误命令已执行失败),需要多刷新几次

## 开发
[文档地址](https://h.hlktech.com/Mobile/download/FDetail/318.html)


PDF手册 vs 项目实现对比分析 （ai分析）

已实现的功能

| 功能                                                                       | 命令字             |
|--------------------------------------------------------------------------|-----------------|
| 读取固件版本                                                                   | 0x0000          |
| 使能/结束配置模式                                                                | 0x00FF / 0x00FE |
| 读取序列号（字符形式）                                                              | 0x0011          |
| 读取传感器参数                                                                  | 0x0008          |
| 配置传感器参数                                                                  | 0x0007          |
| 配置数据输出模式（正常/工程）                                                          | 0x0012          |
| 自动门限生成                                                                   | 0x0009          |
| 自动门限进度查询                                                                 | 0x000A          |
| 参数保存（掉电保存）                                                               | 0x00FD          |
| 上电自动增益调节                                                                 | 0x00EE          |
| 正常模式文本解析（OFF / distance:XX）                                              |                 |
| 工程模式二进制帧解析                                                               |                 |
| 参数ID：最大距离(0x0001)、目标消失延迟(0x0004)、运动门限(0x0010~0x001F)、微动门限(0x0030~0x003F) |                 |
| 电源干扰报警(0x0005) 只读                                                        |                 |
| Web配置界面                                                                  |                 |

未实现的功能

1. 自动门限干扰上报 — CMD 0x0014
- 手册 5.2.11 节描述：模块主动上报哪些距离门存在运动干扰
- 手册 4.2.3 / 图4-7、4-8 描述：门限生成期间检测到人体会提示，存在干扰会提示受影响的距离门
- 返回值包含状态字节 + 距离门位图(bitmask)
- 项目完全没有处理这个异步上报帧
- 项目虽然发送了自动门限命令，但没有处理0x0014干扰上报来给用户反馈

2. 距离门数量不匹配（重要）(?????)
- 手册明确说明：32个距离门 × 4字节 × 2组（运动+微动）= 256字节能量值
- 项目代码 ld2402.h:43 写死 NUM_GATES = 16，只解析前16个门的数据
- 这意味着最大探测距离超过约5.6m（16门 × 0.7m/门 ≈ 11.2m，但实际能量数据只取了一半）

3. 上位机"距离VS时间"图表功能
- 手册 4.2.2 节描述：显示过去60秒内目标距离变化的时间序列图
- Web界面只显示实时数据，没有历史距离变化曲线
