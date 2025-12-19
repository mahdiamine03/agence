import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import TravelApp

if __name__ == "__main__":
    app = TravelApp()
    app.mainloop()
