from logging import getLogger
from json import dump,\
    load
from os import path as os_path
import sys
from _00_base import initial_config

class SERPENT_back_end():

    _log: getLogger = None

    def __init__(self):

        config_SERPENT_path = 'config_SERPENT.json' if '_MEIPASS' in sys.__dict__ \
                                            else os_path.join(os_path.dirname(__file__), 'config_SERPENT.json')

        if not os_path.isfile(config_SERPENT_path):

            self.config_SERPENT = initial_config
            with open(config_SERPENT_path, 'w') as json_out_handle:
                dump(self.config_SERPENT, json_out_handle, indent=2)

        with open(config_SERPENT_path, 'r') as json_in_handle:
            self.config_SERPENT = load(json_in_handle)

        if not self._log:
            self._log = getLogger()

        super(SERPENT_back_end, self).__init__()

    async def initiate_transfer(self,
                          **kwargs):
        if kwargs['asset'] == 'SIT':
            from _00_back_end_SIT import SERPENT_back_end
        elif kwargs['asset'] == 'XETH':
            from _00_back_end_XETH import SERPENT_back_end
        elif kwargs['asset'] == 'MELON':
            from _00_back_end_MELON import SERPENT_back_end
        elif kwargs['asset'] == 'XNT':
            from _00_back_end_XNT import SERPENT_back_end
        elif kwargs['asset'] == 'STAI':
            from _00_back_end_STAI import SERPENT_back_end
        elif kwargs['asset'] == 'XCC':
            from _00_back_end_XCC import SERPENT_back_end
        elif kwargs['asset'] == 'GL':
            from _00_back_end_GL import SERPENT_back_end
        elif kwargs['asset'] == 'PROFIT':
            from _00_back_end_PROFIT import SERPENT_back_end
        elif kwargs['asset'] == 'XJK':
            from _00_back_end_XJK import SERPENT_back_end
        else:
            from _00_back_end_XCH import SERPENT_back_end

        do = SERPENT_back_end()
        return await do.initiate_transfer_final(**kwargs)
