"""
Simple Build Script for Stock Market Game (Improved)
Uses 'python -m PyInstaller' to avoid PATH issues
"""

import os
import sys
import subprocess
import shutil

print("=" * 60)
print("Stock Market Game - Simple Build Script")
print("=" * 60 + "\n")

# Check if we're in the right directory
if not os.path.exists('Game_code'):
    print("❌ ERROR: Game_code folder not found!")
    print("   Make sure you're running this script from the main game folder.")
    print(f"   Current directory: {os.getcwd()}")
    input("\nPress Enter to exit...")
    sys.exit(1)

if not os.path.exists('Game_code/main.py'):
    print("❌ ERROR: Game_code/main.py not found!")
    print("   The Game_code folder must contain main.py")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("✅ Game_code folder found")

# Clean old builds
print("\n🗑️  Cleaning old build files...")
for folder in ['build', '__pycache__']:
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            print(f"   Removed {folder}/")
        except Exception as e:
            print(f"   Warning: Could not remove {folder}: {e}")

for spec_file in [f for f in os.listdir('.') if f.endswith('.spec')]:
    try:
        os.remove(spec_file)
        print(f"   Removed {spec_file}")
    except Exception as e:
        print(f"   Warning: Could not remove {spec_file}: {e}")

print("\n🔨 Building executable...")
print("This will take 5-15 minutes. Please be patient!\n")

# Determine separator based on OS
separator = ';' if sys.platform == 'win32' else ':'

# Build command using python -m PyInstaller
cmd = [
    sys.executable,  # Use the current Python interpreter
    '-m',
    'PyInstaller',
    '--name=StockMarketGame',
    '--windowed',
    '--onefile',
    '--distpath=.',
    f'--add-data=images{separator}images',
    f'--add-data=sounds{separator}sounds',
    '--hidden-import=PySide6',
    '--hidden-import=openai',
    '--hidden-import=pandas',
    '--hidden-import=yfinance',
    '--hidden-import=matplotlib',
    '--hidden-import=dotenv',
    '--collect-all=PySide6',
    '--noconfirm',
    'Game_code/main.py'
]

# Add .env if exists
if os.path.exists('.env'):
    cmd.insert(-1, f'--add-data=.env{separator}.')
    print("📝 Including .env file")

# Add icon if exists
if os.path.exists('images/logo.ico'):
    cmd.insert(-1, '--icon=images/logo.ico')
    print("🎨 Using custom icon")

print("\n⏳ Running PyInstaller...")
print("   (This is the slow part - please wait!)\n")

# Run build
try:
    # Show the command being run
    print("Command:", ' '.join(cmd))
    print("\n" + "-" * 60 + "\n")

    result = subprocess.run(cmd, check=True)

    print("\n" + "=" * 60)
    print("🎉 BUILD SUCCESSFUL!")
    print("=" * 60)

    # Find executable
    if sys.platform == 'win32':
        exe = 'StockMarketGame.exe'
    elif sys.platform == 'darwin':
        exe = 'StockMarketGame.app'
    else:
        exe = 'StockMarketGame'

    if os.path.exists(exe):
        size_mb = os.path.getsize(exe) / (1024 * 1024)
        print(f"\n📦 Executable: {exe}")
        print(f"📊 Size: {size_mb:.2f} MB")
        print(f"📍 Location: {os.path.abspath(exe)}")
    else:
        print(f"\n⚠️  Warning: Could not find {exe}")
        print("   The build may have completed but the file is in an unexpected location.")

    print("\n✅ Your game is ready to play!")
    print("=" * 60)

except subprocess.CalledProcessError as e:
    print("\n" + "=" * 60)
    print("❌ BUILD FAILED!")
    print("=" * 60)
    print("\nThe build process encountered an error.")
    print("Check the error messages above for details.")
    print("\nCommon issues:")
    print("1. PyInstaller not installed → Run: pip install pyinstaller")
    print("2. Missing packages → Run: pip install -r requirements.txt")
    print("3. Wrong directory → Make sure you're in the main game folder")
    print("\nFor detailed diagnostics, run: python diagnose.py")
    input("\nPress Enter to exit...")
    sys.exit(1)

except FileNotFoundError as e:
    print("\n" + "=" * 60)
    print("❌ ERROR: File Not Found")
    print("=" * 60)
    print(f"\n{e}")
    print("\nThis usually means:")
    print("1. PyInstaller is not installed")
    print("   → Run: pip install pyinstaller")
    print("\n2. Python is not in PATH")
    print("   → This script uses the current Python, so this is unlikely")
    print("\n3. A required file is missing")
    print("   → Run: python diagnose.py")
    input("\nPress Enter to exit...")
    sys.exit(1)

except Exception as e:
    print("\n" + "=" * 60)
    print("❌ UNEXPECTED ERROR")
    print("=" * 60)
    print(f"\n{type(e).__name__}: {e}")
    print("\nFor detailed diagnostics, run: python diagnose.py")
    input("\nPress Enter to exit...")
    sys.exit(1)

input("\nPress Enter to exit...")