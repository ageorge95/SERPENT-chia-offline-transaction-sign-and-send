import tkinter as tk
from time import sleep
from queue import Empty
from os import path, chdir, name
from traceback import format_exc
from webbrowser import open_new
import sys
from PIL import Image
from signal import signal,\
    SIGINT
from threading import Thread
from logging import getLogger
from tkinter.scrolledtext import Text, Scrollbar, ScrolledText
from tkinter import tix,\
    simpledialog,\
    Entry,\
    ttk,\
    N, S, E, W,\
    END,\
    Label,\
    NONE
import asyncio

from src.base import configure_logger_and_queue,\
    handle_SERPENT_config
from src.back_end import SERPENT

class buttons_label_state_change():
    entry_coin_filter: Entry
    combobox_asset_to_use: ttk.Combobox
    entry_mnemonic: ScrolledText
    entry_send_to_address: ScrolledText
    entry_send_to_amount: Entry
    entry_attached_fee: Entry
    button_transfer_master_sks: ttk.Button
    label_backend_status: Label
    _log: getLogger

    def __init__(self):

        super(buttons_label_state_change, self).__init__()

    def get_buttons_reference(self):

        self.buttons = [self.entry_coin_filter,
                        self.combobox_asset_to_use,
                        self.entry_mnemonic,
                        self.entry_send_to_address,
                        self.entry_send_to_amount,
                        self.entry_attached_fee,
                        self.button_transfer_master_sks
                        ]
    def disable_all_buttons(self):
        self.get_buttons_reference()
        [button.configure(state='disabled') for button in self.buttons]
        self._log.info('Controls are now disabled until the operation is done. Please wait ...')

    def enable_all_buttons(self):
        self.get_buttons_reference()
        [button.configure(state='normal') for button in self.buttons]
        self._log.info('Controls are now enabled')

    def backend_label_free(self):
        self.label_backend_status.configure(text="Doing nothing ...",
                                            fg='#33cc33')

    def backend_label_busy(self,
                           text: str):
        self.label_backend_status.configure(text=text,
                                            fg='#ff3300')

class sponsor_reminder():
    def __init__(self, frame):
        self.frame = frame

        self.label_sponsor_logo = Label(self.frame, text='Sponsor')
        self.label_sponsor_logo.grid(column=0, row=0)
        donation_img = 'donation.gif' if path.isfile('../media/donation.gif') else path.join(sys._MEIPASS,
                                                                                             '../media/donation.gif')
        info = Image.open(donation_img)
        self.frameCnt = info.n_frames-3
        self.sleep_between_frames = 0.1
        self.frames = [tk.PhotoImage(file=donation_img, format='gif -index %i' % (i)) for i in range(self.frameCnt)]

        self.label_sponsor_text = Label(self.frame,
                                        text='Found this tool helpful?'
                                             '\n\nWant to contribute to its development ?'
                                             '\n\nYou can make a donation to the author.'
                                             '\n\nClick this text for more info. Thank you :)',
                                        font=10)
        self.label_sponsor_text.grid(column=1, row=0)
        self.label_sponsor_text.bind("<Button-1>", self.sponsor_link)

        Thread(target=self.sponsor_gif_animation).start()

    def sponsor_link(self,
                     *args):
        open_new('https://github.com/ageorge95/SERPENT-chia-offline-transaction-sign-and-send#support')

    def sponsor_gif_animation(self):
        while True:
            for frame_index in range(self.frameCnt):
                frame = self.frames[frame_index]
                self.label_sponsor_logo.configure(image=frame)
                sleep(self.sleep_between_frames)
            sleep(self.sleep_between_frames)

class ConsoleUi(configure_logger_and_queue):
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):

        super(ConsoleUi, self).__init__()

        self.frame = frame

        # add a button to clear the text
        self.button_clear_console = ttk.Button(self.frame, text='CLEAR CONSOLE', command=self.clear_console)
        self.button_clear_console.grid(column=0, row=0, sticky=W)
        self.tip_clear_console = tix.Balloon(self.frame)
        self.tip_clear_console.bind_widget(self.button_clear_console,balloonmsg="Will clear the text from the console frame.")

        # Create a ScrolledText widget
        self.h_scroll = Scrollbar(self.frame, orient='horizontal')
        self.h_scroll.grid(row=2, column=0, sticky=(W, E))
        self.v_scroll = Scrollbar(self.frame, orient='vertical')
        self.v_scroll.grid(row=1, column=1, sticky=(N, S))

        self.scrolled_text = Text(frame, state='disabled', width=110, height=30, wrap=NONE, xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.scrolled_text.grid(row=1, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)

        self.h_scroll.config(command=self.scrolled_text.xview)
        self.v_scroll.config(command=self.scrolled_text.yview)

        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')

        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)

    def clear_console(self):
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.delete('1.0', END)
        self.scrolled_text.configure(state='disabled')

class FormControls(buttons_label_state_change,
                   configure_logger_and_queue,
                   ):

    def __init__(self,
                 frame):
        super(FormControls, self).__init__()

        self.frame = frame

        self.label_hover_hints = Label(self.frame, text='NOTE: Hover on the widgets below for more info.')
        self.label_hover_hints.grid(column=0, row=0)

        self.config_SERPENT = handle_SERPENT_config()

        def coin_to_filter(*args):
            self.combobox_asset_to_use.configure(values=list(filter(lambda x: self.entry_coin_filter.get().lower() in x.lower(),
                                                                    ['{}__{}'.format(entry[0], entry[1]['friendly_name']) for entry in self.config_SERPENT.items()])))
        self.entry_coin_filter = Entry(self.frame)
        self.entry_coin_filter.grid(column=0, row=2)
        self.entry_coin_filter.bind("<KeyRelease>", coin_to_filter)
        self.tip_show_balance = tix.Balloon(self.frame)
        self.tip_show_balance.bind_widget(self.entry_coin_filter,
                                          balloonmsg="Will filter the entries in the combobox below.")

        self.label_asset_to_use = Label(self.frame, text='Asset to be used:')
        self.asset_to_use = tk.StringVar()
        self.combobox_asset_to_use = ttk.Combobox(
            self.frame,
            textvariable=self.asset_to_use,
            width=18,
            state='readonly',
            values=['{}__{}'.format(entry[0], entry[1]['friendly_name']) for entry in self.config_SERPENT.items()]
        )
        self.combobox_asset_to_use.set('SELECT AN ASSET')
        self.label_asset_to_use.grid(column=0, row=1)
        self.combobox_asset_to_use.grid(column=0, row=3)
        self.tip_coin_to_use = tix.Balloon(self.frame)
        self.tip_coin_to_use.bind_widget(self.combobox_asset_to_use,
                                         balloonmsg="All the configured coins are here. Select the one to be used.")

        self.label_mnemonic = Label(self.frame, text='Mnemonic:')
        self.entry_mnemonic = ScrolledText(self.frame, width=30, height=4)
        self.label_mnemonic.grid(column=0, row=4)
        self.entry_mnemonic.grid(column=0, row=5)
        self.tip_mnemonic = tix.Balloon(self.frame)
        self.tip_mnemonic.bind_widget(self.entry_mnemonic,
                                      balloonmsg="The mnemonic used to sign the transaction. 24 words with a whitespace between them.")

        self.label_send_to_address = Label(self.frame, text='Send to address:')
        self.entry_send_to_address = ScrolledText(self.frame, width=30, height=2)
        self.label_send_to_address.grid(column=0, row=6)
        self.entry_send_to_address.grid(column=0, row=7)
        self.tip_send_to_address = tix.Balloon(self.frame)
        self.tip_send_to_address.bind_widget(self.entry_send_to_address,
                                             balloonmsg="The address where to send the funds.")

        self.label_send_to_amount = Label(self.frame, text='Amount to send:')
        self.entry_send_to_amount = Entry(self.frame)
        self.label_send_to_amount.grid(column=0, row=10)
        self.entry_send_to_amount.grid(column=0, row=11)
        self.tip_send_to_amount = tix.Balloon(self.frame)
        self.tip_send_to_amount.bind_widget(self.entry_send_to_amount,
                                             balloonmsg="The amount of coins to send, ex: 1 OR 1.1 OR 10")

        self.label_attached_fee = Label(self.frame, text='Attached fee:')
        self.entry_attached_fee = Entry(self.frame)
        self.label_attached_fee.grid(column=0, row=12)
        self.entry_attached_fee.grid(column=0, row=13)
        self.tip_attached_fee = tix.Balloon(self.frame)
        self.tip_attached_fee.bind_widget(self.entry_attached_fee,
                                          balloonmsg="The fee to attach to the transaction.")

        self.label_backend_status_notify = Label(self.frame, text='Back-end status:')
        self.label_backend_status_notify.grid(column=2, row=0)
        self.label_backend_status = Label(self.frame, text="Doing nothing ...", fg='#33cc33')
        self.label_backend_status.grid(column=2, row=1)

        self.label_initiate_transfer = Label(self.frame, text='Initiate transfer with:')
        self.label_initiate_transfer.grid(column=0, row=15)

        self.button_transfer_master_sks = ttk.Button(self.frame, text='Master sks', command=lambda :self.master_initiate_transfer(use_farmer_sk=False))
        self.button_transfer_master_sks.grid(column=0, row=16, sticky=W)
        self.tip_transfer_master_sks = tix.Balloon(self.frame)
        self.tip_transfer_master_sks.bind_widget(self.button_transfer_master_sks,
                                                 balloonmsg="Will initiate the coins transfer; will use the derived master sks.")

        self.button_transfer_farmer_sk = ttk.Button(self.frame, text='Farmer sk (aka unstake)', command=lambda :self.master_initiate_transfer(use_farmer_sk=True))
        self.button_transfer_farmer_sk.grid(column=0, row=16, sticky=E)
        self.tip_transfer_farmer_sk = tix.Balloon(self.frame)
        self.tip_transfer_farmer_sk.bind_widget(self.button_transfer_farmer_sk,
                                                balloonmsg="Will initiate the coins transfer; will use the farmer sk.")

        self.separator_filtering_v = ttk.Separator(self.frame, orient='vertical')
        self.separator_filtering_v.grid(column=1, row=0, rowspan=17, sticky=(N, S))

        self.separator_filtering_h = ttk.Separator(self.frame, orient='horizontal')
        self.separator_filtering_h.grid(column=0, row=14, columnspan=2, sticky=(W, E))

    def check_coin_selection(self):
        if self.asset_to_use.get() == 'SELECT AN ASSET':
            self._log.warning('Please select an asset !')
            return False
        return True

    def check_address_to_send(self):
        if self.entry_send_to_address.get("1.0", END).strip() == '':
            self._log.warning('Please provide an address to send to. !')
            return False
        return True

    def check_amount_fees(self):
        try:
            float(self.entry_send_to_amount.get())
        except:
            self._log.warning('Please provide proper int/float to the amount entry !')
            return False

        try:
            float(self.entry_attached_fee.get())
        except:
            self._log.warning('Please provide proper int/float to the fee entry !')
            return False

        return True

    def master_initiate_transfer(self,
                                 use_farmer_sk: bool):
        if self.check_coin_selection() and self.check_address_to_send() and self.check_amount_fees():
            async def action():
                self.disable_all_buttons()
                self.backend_label_busy(text='Busy with transferring the funds !')
                self._log.info('Backend process started. Please wait ...')

                try:
                    snake = SERPENT(asset=self.asset_to_use.get().split('__')[0],
                                    mnemonic=self.entry_mnemonic.get('1.0', END).strip(),
                                    send_to_address=self.entry_send_to_address.get('1.0', END).strip(),
                                    amount_to_transfer=float(self.entry_send_to_amount.get()),
                                    fee=float(self.entry_attached_fee.get()),
                                    use_farmer_sk=use_farmer_sk)
                    snake.create_unsigned_transaction()
                    snake.sign_tx()
                    snake.push_tx()
                except:
                    self._log.error(f'Could not execute the transfer ! \n{ format_exc(chain=False) }')

                self.enable_all_buttons()
                self.backend_label_free()

            loop = asyncio.get_event_loop()
            loop.run_until_complete(action())
            # using threading would cause clvm to "panick"
            # Thread(target=action).start()

class App():

    def __init__(self, root):
        chdir(path.dirname(__file__))

        self.root = root
        self.root.title('SERPENT-chia-offline-transaction-sign-and-send | ' + open('version.txt' if path.isfile('version.txt') else path.join(sys._MEIPASS, 'version.txt') , 'r').read())
        self.root.iconbitmap('icon.ico' if path.isfile('../media/icon.ico') else path.join(sys._MEIPASS,
                                                                                           '../media/icon.ico'))

        sponsor_frame = ttk.Labelframe(text="Sponsor")
        sponsor_frame.grid(row=0, column=0, sticky="nsw")
        self.sponsor_frame = sponsor_reminder(sponsor_frame)

        controls_frame = ttk.Labelframe(text="Controls")
        controls_frame.grid(row=1, column=0, sticky="nsew")
        self.controls_frame = FormControls(controls_frame)

        console_frame = ttk.Labelframe(text="Console")
        console_frame.grid(row=0, column=1, sticky="nsew", rowspan=3)
        self.console_frame = ConsoleUi(console_frame)

        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)
        signal(SIGINT, self.quit)

    def quit(self):
        # self.root.destroy()
        sys.exit()

def main():
    root = tix.Tk()
    root.resizable(False, False)
    app = App(root)
    app.root.mainloop()

if __name__ == '__main__':
    main()