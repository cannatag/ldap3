"""
"""
from ...extend.operation import ExtendedOperation

class FastBind(ExtendedOperation):
    def config(self):
        self.request_name = '1.2.840.113556.1.4.1781'
