#图片说明
所有截图都是在 1920 * 1080 分辨率下截取

# map - 地图
由于游戏中的雷达小地图对应就是使用最小缩放比例的大地图，因此截取都是用最小缩放比例的。

不同地图存放在不同文件夹
- 空间站黑塔 - kjzht
    - 主控舱段 - zkcd
    - 基座舱段 - jzcd
    - 支援舱段 - zycd

每个文件夹中，会有以下文件：（均无透明通道）
- origin.png - 对应地图的全图，使用最小缩放比例截取的。
- mask.png - 对应地图的黑白图，白色部分为可走部分，用于后续掩码相关操作。
- gray.png - 原图根据黑白图掩码进行扣图得到的灰度图，是最纯粹的地图部分，道路部分和背景部分进行了统一颜色。

### 新增地图方法
游戏中打开对应地图后，调用 dev.screenshot_map_vertically 即可。


# template - 模板

## arrow - 小地图上的箭头
使用 25 * 25 尺寸，手工初步裁剪后可使用 dev.screenshot.convert_arrow_color 生成

## transport_x - 地图上的传送点
统一使用 50*50 尺寸，地图缩放到最大，找到深色背景色的传送点截取后，使用 dev.screenshot.cut_icon_from_black_bg 扣图即可。