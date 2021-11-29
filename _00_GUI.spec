# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None


a = Analysis(['_00_GUI.py'],
             pathex=['chia_blockchain', silicoin_blockchain],
             binaries=[],
             datas=[('icon.ico', '.'),
			  ('version.txt', '.'),
              ('donation.gif', '.'),
              (sys.prefix+r'/tcl/tix8.4.3', 'tcl/tix8.4.3'),
              ('chia_blockchain/chia', 'chia_blockchain/chia'),
              ('chia_blockchain/chia', 'chia'),
              ('silicoin_blockchain/chia', 'silicoin_blockchain/chia'),
              ('silicoin_blockchain/chia', 'chia')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='_00_GUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
		  icon='icon.ico' )
