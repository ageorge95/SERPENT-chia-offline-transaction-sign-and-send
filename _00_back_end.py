from logging import getLogger
from json import dump,\
    load
from os import path as os_path
import sys
from asyncio import run

from _00_base import initial_config

class SERPENT_back_end():

    _log: getLogger = None

    def __init__(self):

        config_path = 'config_SERPENT.json' if '_MEIPASS' in sys.__dict__ \
                                            else os_path.join(os_path.dirname(__file__), 'config_SERPENT.json')

        if not os_path.isfile(config_path):

            self.config = initial_config
            with open(config_path, 'w') as json_out_handle:
                dump(self.config, json_out_handle, indent=2)

        with open(config_path, 'r') as json_in_handle:
            self.config = load(json_in_handle)

        if not self._log:
            self._log = getLogger()

        super(SERPENT_back_end, self).__init__()

    async def initiate_transfer(self,
                          **kwargs):
        if kwargs['coin'] == 'SIT':
            from _00_back_end_SIT import SERPENT_back_end
        elif kwargs['coin'] == 'XETH':
            from _00_back_end_XETH import SERPENT_back_end
        elif kwargs['coin'] == 'MELON':
            from _00_back_end_MELON import SERPENT_back_end
        elif kwargs['coin'] == 'XNT':
            from _00_back_end_XNT import SERPENT_back_end
        elif kwargs['coin'] == 'STAI':
            from _00_back_end_STAI import SERPENT_back_end
        else:
            from _00_back_end_XCH import SERPENT_back_end

        do = SERPENT_back_end()
        return await do.initiate_transfer_final(**kwargs)
