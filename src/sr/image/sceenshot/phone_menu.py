from cv2.typing import MatLike

from basic import Rect, str_utils
from basic.i18_utils import gt
from basic.img import cv2_utils, MatchResult, MatchResultList
from sr.const.phone_menu_const import PhoneMenuItem
from sr.image import ImageMatcher
from sr.image.ocr_matcher import OcrMatcher


TRAILBLAZE_LEVEL_PART = Rect(1280, 240, 1460, 270)  # 等级
MENU_ITEMS_PART = Rect(1270, 300, 1810, 1070)  # 菜单选项
MENU_ITEMS_AT_RIGHT_PART = Rect(1810, 230, 1915, 1030)  # 菜单侧栏选项


def in_phone_menu(screen: MatLike, ocr: OcrMatcher) -> bool:
    """
    是否在菜单页面 有显示等级
    :param screen:
    :param ocr:
    :return:
    """
    part, _ = cv2_utils.crop_image(screen, TRAILBLAZE_LEVEL_PART)

    ocr_result: str = ocr.ocr_for_single_line(part)

    if str_utils.find_by_lcs(gt('开拓等级', 'ocr'), ocr_result, percent=0.55):
        return True

    return False


def get_phone_menu_item_pos(screen: MatLike, im: ImageMatcher, item: PhoneMenuItem) -> MatchResult:
    """
    获取菜单中某个具体选项的位置
    :param screen:
    :param im:
    :param item:
    :return:
    """
    part, _ = cv2_utils.crop_image(screen, MENU_ITEMS_PART)
    result_list: MatchResultList = im.match_template(part, item.template_id, only_best=True)

    if result_list.max is not None:
        result_list.max.x += MENU_ITEMS_PART.x1
        result_list.max.y += MENU_ITEMS_PART.y1

    return result_list.max


def get_phone_menu_item_pos_at_right(screen: MatLike, im: ImageMatcher, item: PhoneMenuItem, alert: bool = False) -> MatchResult:
    """
    获取菜单侧栏中某个具体选项的位置
    :param screen:
    :param im:
    :param item:
    :param alert: 是否有感叹号红点
    :return:
    """
    part, _ = cv2_utils.crop_image(screen, MENU_ITEMS_AT_RIGHT_PART)
    result_list: MatchResultList = im.match_template(part, item.template_id, only_best=True)

    if result_list.max is None:
        return None

    result_list.max.x += MENU_ITEMS_AT_RIGHT_PART.x1
    result_list.max.y += MENU_ITEMS_AT_RIGHT_PART.y1

    if alert:
        x1, y1 = result_list.max.x, result_list.max.y - 50
        x2, y2 = result_list.max.x + result_list.max.w + 50, result_list.max.y + result_list.max.h
        with_alert_part, _ = cv2_utils.crop_image(screen, Rect(x1, y1, x2, y2))
        cv2_utils.show_image(with_alert_part, win_name='with_alert_part')
        alert_result: MatchResultList = im.match_template(with_alert_part, 'ui_alert', only_best=True)
        if alert_result.max is not None:
            return result_list.max
        else:
            return None
    else:
        return result_list.max
