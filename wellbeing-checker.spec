# wellbeing-checker.spec
block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/ui/welcome.kv', 'ui'),
        ('src/ui/login.kv', 'ui'),
        ('src/ui/signup.kv', 'ui'),
        ('src/ui/diary.kv', 'ui'),
        ('src/ui/summary.kv', 'ui'),
        ('src/ui/settings.kv', 'ui'),
        ('src/ui/monthly_summary.kv', 'ui'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='wellbeing-checker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # GUI app, no console window
    icon=None        # you can add an .ico file here later
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='wellbeing-checker'
)