# flake8: noqa
from input_manager import InputManager
try:
    from gpio_inpput_manager import GPIOManager
except ImportError:
    pass