from logging import getLogger
from json import dump,\
    load
from os import path as os_path
from asyncio import run

from _00_base import initial_config

class SERPENT_back_end():

    _log: getLogger = None

    def __init__(self):

        if not os_path.isfile('config.json'):

            self.config = initial_config
            with open('config.json', 'w') as json_out_handle:
                dump(self.config, json_out_handle, indent=2)

        with open('config.json', 'r') as json_in_handle:
            self.config = load(json_in_handle)

        if not self._log:
            self._log = getLogger()

        super(SERPENT_back_end, self).__init__()

    async def initiate_transfer(self,
                          **kwargs):
        if kwargs['coin'] == 'SIT':
            from _00_back_end_SIT import SERPENT_back_end
        else:
            from _00_back_end_XCH import SERPENT_back_end

        do = SERPENT_back_end()
        await do.initiate_transfer_final(**kwargs)

# *********** debugging code ***********
if __name__ == '__main__':
    from _00_base import configure_logger
    configure_logger()
    do_transfer = SERPENT_back_end()
    run(do_transfer.initiate_transfer(coin='',
                         mnemonic='',
                         address_to_send='',
                         amount_to_send=0,
                         fees_to_attach=0))