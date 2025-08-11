try:
    from src.executables.executables import Executables
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.executables.executables import Executables


class GameCalculations(Executables):
    pass
