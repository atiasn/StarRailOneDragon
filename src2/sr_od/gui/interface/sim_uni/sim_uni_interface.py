from qfluentwidgets import FluentIcon

from one_dragon.gui.component.interface.pivot_navi_interface import PivotNavigatorInterface
from sr_od.context.sr_context import SrContext
from sr_od.gui.interface.world_patrol.world_patrol_run_interface import WorldPatrolRunInterface


class SimUniInterface(PivotNavigatorInterface):

    def __init__(self, ctx: SrContext, parent=None):
        self.ctx: SrContext = ctx
        PivotNavigatorInterface.__init__(self, object_name='sr_sim_uni_interface', parent=parent,
                                         nav_text_cn='模拟宇宙', nav_icon=FluentIcon.IOT)

    def create_sub_interface(self):
        """
        创建下面的子页面
        :return:
        """
        self.add_sub_interface(WorldPatrolRunInterface(ctx=self.ctx))