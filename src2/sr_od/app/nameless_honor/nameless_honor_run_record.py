from typing import Optional

from one_dragon.base.operation.application_run_record import AppRunRecord


class NamelessHonorRunRecord(AppRunRecord):

    def __init__(self, instance_idx: Optional[int] = None):
        AppRunRecord.__init__(self, 'nameless_honor', instance_idx=instance_idx)