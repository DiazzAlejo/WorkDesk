from typing import Callable

ItemCallback = Callable[[str], None]
TodoEditCallback = Callable[[str, str], None]
RefreshCallback = Callable[[], None]
