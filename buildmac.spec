# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess
import sys
from pathlib import Path

block_cipher = None
a = Analysis(
    ['rock_sickle.py'],
    pathex=[],
    binaries=[],
    datas=[('Assets', 'Assets')],  # Add your assets folder
    hiddenimports=['pygame'],
    hookspath=[],
    hooksconfig={},
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
    name='Rock Sickle',  # More user-friendly name with spaces
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Rock Sickle',
)
app = BUNDLE(
    coll,
    name='Rock Sickle.app',
icon='Assets/Images/Icons/RockSickle.icns',
    bundle_identifier='com.yourdomain.rocksickle',  # Change to your domain
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'CFBundleDisplayName': 'Rock Sickle',
        'LSBackgroundOnly': 'False',
        'NSRequiresAquaSystemAppearance': 'False',
    },
)

# The actual DMG creation function that will run
def create_dmg():
    print("\n" + "-"*50)
    print("STARTING DMG CREATION PROCESS")
    print("-"*50)
    
    # Define paths
    app_path = os.path.join('dist', 'Rock Sickle.app')
    dist_dir = os.path.abspath('dist')
    dmg_name = os.path.join(dist_dir, 'Rock Sickle.dmg')
    volume_name = 'Rock Sickle'
    dmg_icon_path = 'Assets/Images/Icons/StoneDrive.icns'
    
    # Make sure paths exist
    print(f"Checking if app exists at: {app_path}")
    if not os.path.exists(app_path):
        print(f"ERROR: App bundle not found at {app_path}")
        return False
    
    print(f"Checking if icon exists at: {dmg_icon_path}")
    if not os.path.exists(dmg_icon_path):
        print(f"WARNING: Icon file not found at {dmg_icon_path}. DMG will use default icon.")
    
    # Check if create-dmg is installed
    print("Checking if create-dmg is installed...")
    try:
        result = subprocess.run(['which', 'create-dmg'], 
                               capture_output=True, 
                               text=True, 
                               check=False)
        if result.returncode != 0:
            print("ERROR: create-dmg not found. Please install it with: brew install create-dmg")
            return False
        else:
            print(f"create-dmg found at: {result.stdout.strip()}")
    except Exception as e:
        print(f"ERROR checking for create-dmg: {e}")
        return False
    
    # Remove existing DMG if it exists
    if os.path.exists(dmg_name):
        print(f"Removing existing DMG at {dmg_name}")
        try:
            os.remove(dmg_name)
        except Exception as e:
            print(f"WARNING: Could not remove existing DMG: {e}")
    
    # Create DMG with Applications folder shortcut
    print(f"Creating DMG file at: {dmg_name}")
    cmd = [
        'create-dmg',
        '--volname', volume_name,
        '--volicon', dmg_icon_path,
        '--window-pos', '200', '120',
        '--window-size', '800', '400',
        '--icon-size', '100',
        '--icon', 'Rock Sickle.app', '200', '190',
        '--app-drop-link', '600', '190',  # Creates shortcut to Applications folder
        '--no-internet-enable',
        dmg_name,
        app_path
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, 
                                capture_output=True, 
                                text=True, 
                                check=False)
        
        if result.returncode == 0:
            print(f"DMG created successfully: {dmg_name}")
            print(f"Full path to DMG: {os.path.abspath(dmg_name)}")
            return True
        else:
            print(f"ERROR: create-dmg command failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR running create-dmg: {e}")
        return False
    finally:
        print("-"*50)
        print("DMG CREATION PROCESS FINISHED")
        print("-"*50 + "\n")

# This ensures the DMG creation function runs after PyInstaller completes the build
# Important! PyInstaller executes this script twice - once to analyze dependencies and once to build
# Only create DMG during the actual build phase
if BUNDLE and not hasattr(sys, 'frozen'):
    create_dmg()