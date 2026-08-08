import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from src.cli.main import main

if __name__ == '__main__':
    main()
