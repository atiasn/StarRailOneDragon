from typing import ClassVar, Optional, Tuple

from cv2.typing import MatLike

from basic import Rect, str_utils
from basic.i18_utils import gt
from basic.img import cv2_utils
from basic.log_utils import log
from sr.app.application_base import Application
from sr.app.sim_uni.sim_uni_app import SimUniApp
from sr.app.trailblaze_power.trailblaze_power_config import TrailblazePowerPlanItem
from sr.const import phone_menu_const
from sr.context.context import Context
from sr.div_uni.op.ornamenet_extraction import ChallengeOrnamentExtraction
from sr.operation import StateOperationNode, StateOperationEdge, OperationOneRoundResult
from sr.operation.battle.use_trailblaze_power import UseTrailblazePower
from sr.operation.common.back_to_normal_world_plus import BackToNormalWorldPlus
from sr.operation.common.cancel_mission_trace import CancelMissionTrace
from sr.interastral_peace_guide.guide_const import GuideTabEnum, GuideMission, GuideMissionEnum
from sr.interastral_peace_guide.choose_guide_tab import ChooseGuideTab
from sr.operation.unit.menu.click_phone_menu_item import ClickPhoneMenuItem
from sr.operation.unit.menu.open_phone_menu import OpenPhoneMenu


class TrailblazePower(Application):

    SIM_UNI_POWER_RECT: ClassVar[Rect] = Rect(1474, 56, 1518, 78)  # 模拟宇宙 体力
    SIM_UNI_QTY_RECT: ClassVar[Rect] = Rect(1672, 56, 1707, 78)  # 模拟宇宙 沉浸器数量

    STATUS_NORMAL_TASK: ClassVar[str] = '普通副本'
    STATUS_SIM_UNI_TASK: ClassVar[str] = '模拟宇宙'
    STATUS_OE_TASK: ClassVar[str] = '饰品提取'
    STATUS_NO_ENOUGH_POWER: ClassVar[str] = '体力不足'
    STATUS_NO_PLAN: ClassVar[str] = '没有开拓力计划'
    STATUS_WITH_PLAN: ClassVar[str] = '有开拓力计划'
    STATUS_PLAN_FINISHED: ClassVar[str] = '完成计划'

    def __init__(self, ctx: Context):
        edges = []

        world = StateOperationNode('返回大世界', op=BackToNormalWorldPlus(ctx))

        cancel_trace = StateOperationNode('取消任务追踪', op=CancelMissionTrace(ctx))
        edges.append(StateOperationEdge(world, cancel_trace))

        check_task = StateOperationNode('检查当前需要挑战的关卡', self._check_task)
        edges.append(StateOperationEdge(cancel_trace, check_task))

        check_power = StateOperationNode('检查剩余开拓力', self._check_power)
        edges.append(StateOperationEdge(check_task, check_power, status=TrailblazePower.STATUS_WITH_PLAN))

        execute = StateOperationNode('执行开拓力计划', self._execute_plan)
        edges.append(StateOperationEdge(check_power, execute))
        edges.append(StateOperationEdge(execute, execute))  # 循环挑战

        back = StateOperationNode('完成后返回大世界', op=BackToNormalWorldPlus(ctx))
        edges.append(StateOperationEdge(execute, back, status=TrailblazePower.STATUS_NO_ENOUGH_POWER))
        edges.append(StateOperationEdge(execute, back, status=TrailblazePower.STATUS_PLAN_FINISHED))

        super().__init__(ctx, try_times=5,
                         op_name=gt('开拓力', 'ui'),
                         edges=edges,
                         run_record=ctx.tp_run_record)

    def handle_init(self) -> Optional[OperationOneRoundResult]:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        可以返回初始化后判断的结果
        - 成功时跳过本指令
        - 失败时立刻返回失败
        - 不返回时正常运行本指令
        """
        self.last_mission: Optional[GuideMission] = None  # 上一个挑战副本
        self.power: int = 0  # 剩余开拓力
        self.qty: int = 0  # 沉浸器数量

        return None

    def _check_task(self) -> OperationOneRoundResult:
        """
        判断下一个是什么副本
        :return:
        """
        self.ctx.tp_config.check_plan_finished()
        plan: Optional[TrailblazePowerPlanItem] = self.ctx.tp_config.next_plan_item

        if plan is None:
            return self.round_success(status=TrailblazePower.STATUS_NO_PLAN)

        return self.round_success(status=TrailblazePower.STATUS_WITH_PLAN)

    def _check_power(self) -> OperationOneRoundResult:
        """
        识别开拓力和沉浸器
        :return:
        """
        ops = [
            OpenPhoneMenu(self.ctx),
            ClickPhoneMenuItem(self.ctx, phone_menu_const.INTERASTRAL_GUIDE),
            ChooseGuideTab(self.ctx, GuideTabEnum.TAB_2.value)
        ]

        for op in ops:
            op_result = op.execute()
            if not op_result.success:
                return self.round_by_op(op_result)

        screen = self.screenshot()
        x, y = self._get_power_and_qty(screen)

        if x is None or y is None:
            return self.round_retry('检测开拓力和沉浸器数量失败', wait=1)

        log.info('检测当前体力 %d 沉浸器数量 %d', x, y)
        self.power = x
        self.qty = y

        return self.round_success()

    def _get_power_and_qty(self, screen: MatLike) -> Tuple[int, int]:
        """
        获取开拓力和沉浸器数量
        :param screen: 屏幕截图
        :return:
        """
        part = cv2_utils.crop_image_only(screen, TrailblazePower.SIM_UNI_POWER_RECT)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        power = str_utils.get_positive_digits(ocr_result, err=None)

        part = cv2_utils.crop_image_only(screen, TrailblazePower.SIM_UNI_QTY_RECT)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        qty = str_utils.get_positive_digits(ocr_result, err=None)

        return power, qty

    def _execute_plan(self) -> OperationOneRoundResult:
        plan: Optional[TrailblazePowerPlanItem] = self.ctx.tp_config.next_plan_item
        mission: Optional[GuideMission] = GuideMissionEnum.get_by_unique_id(plan['mission_id'])
        can_run_times: int = self.power // mission.power
        if mission.sim_world is not None or mission.ornament_extraction is not None:  # 模拟宇宙相关的增加沉浸器数量
            can_run_times += self.qty
        if can_run_times == 0:
            return self.round_success(TrailblazePower.STATUS_NO_ENOUGH_POWER)

        if can_run_times + plan['run_times'] > plan['plan_times']:
            run_times = plan['plan_times'] - plan['run_times']
        else:
            run_times = can_run_times
        log.info(f'准备挑战 {mission.ui_cn} 次数 {run_times}')
        if run_times == 0:
            return self.round_success(TrailblazePower.STATUS_PLAN_FINISHED)

        self.ctx.sim_uni_run_record.check_and_update_status()

        if mission.tp is not None:
            op = UseTrailblazePower(self.ctx, mission, plan['team_num'], run_times,
                                    support=plan['support'] if plan['support'] != 'none' else None,
                                    on_battle_success=self._on_normal_task_success,
                                    need_transport=mission != self.last_mission)
        elif mission.sim_world is not None:
            op = SimUniApp(self.ctx,
                           specified_uni_num=mission.sim_world.idx,
                           max_reward_to_get=run_times,
                           get_reward_callback=self._on_sim_uni_get_reward
                           )
            op.init_context_before_start = False
            op.stop_context_after_stop = False
        elif mission.ornament_extraction is not None:
            op = ChallengeOrnamentExtraction(self.ctx, mission.ornament_extraction,
                                             run_times=run_times,
                                             diff=0,
                                             file_num=plan['team_num'],
                                             support_character=plan['support'] if plan['support'] != 'none' else None,
                                             get_reward_callback=self.on_oe_get_reward)
        else:
            return self.round_fail('未知副本类型')

        self.last_mission = mission
        return self.round_by_op(op.execute())

    def _on_normal_task_success(self, finished_times: int, use_power: int):
        """
        普通副本获取一次奖励时候的回调
        :param finished_times: 完成次数
        :param use_power: 使用的体力
        :return:
        """
        log.info('挑战成功 完成次数 %d 使用体力 %d', finished_times, use_power)
        self.power -= use_power
        plan: Optional[TrailblazePowerPlanItem] = self.ctx.tp_config.next_plan_item
        plan['run_times'] += finished_times
        self.ctx.tp_config.save()

    def _on_sim_uni_get_reward(self, use_power: int, user_qty: int):
        """
        模拟宇宙 获取沉浸奖励后的回调
        :return:
        """
        log.info('获取沉浸奖励 使用体力 %d 使用沉浸器 %d', use_power, user_qty)
        plan: Optional[TrailblazePowerPlanItem] = self.ctx.tp_config.next_plan_item
        plan['run_times'] += 1
        self.ctx.tp_config.save()

        self.power -= use_power
        self.qty -= user_qty

    def on_oe_get_reward(self, qty: int):
        """
        饰品提取 获取奖励后的回调
        :return:
        """
        log.info('饰品提取获取奖励 次数 %d', qty)
        plan: Optional[TrailblazePowerPlanItem] = self.ctx.tp_config.next_plan_item
        mission: Optional[GuideMission] = GuideMissionEnum.get_by_unique_id(plan['mission_id'])
        for _ in range(qty):
            if self.qty > 0:  # 优先使用沉浸器
                self.qty -= 1
            elif self.power >= mission.power:
                self.power -= mission.power

            plan['run_times'] += 1
            self.ctx.tp_config.save()
