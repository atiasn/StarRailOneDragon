from one_dragon.base.geometry.point import Point

STANDARD_RESOLUTION_W = 1920
STANDARD_RESOLUTION_H = 1080
STANDARD_CENTER_POS = Point(STANDARD_RESOLUTION_W // 2, STANDARD_RESOLUTION_H // 2)

TEMPLATE_ARROW = "arrow"
TEMPLATE_ARROW_LEN = 31  # 箭头的图片大小
TEMPLATE_ARROW_LEN_PLUS = 35  # 箭头图片在拼接图中的大小
TEMPLATE_ARROW_R = TEMPLATE_ARROW_LEN // 2  # 箭头的图片半径
TEMPLATE_TRANSPORT_LEN = 51  # 传送点的图片大小

THRESHOLD_SP_TEMPLATE_IN_LARGE_MAP = 0.7  # 特殊点模板在大地图上的阈值
COLOR_WHITE_GRAY = 255  # 地图上道路颜色
COLOR_MAP_ROAD_GRAY = 0  # 地图上道路颜色
COLOR_MAP_ROAD_BGR = (60, 60, 60)  # 地图上道路颜色
COLOR_ARROW_BGR = (0, 200, 255)  # 小箭头颜色

OPPOSITE_DIRECTION = {'w': 's', 'a': 'd', 's': 'w', 'd': 'a'}  # 反方向
