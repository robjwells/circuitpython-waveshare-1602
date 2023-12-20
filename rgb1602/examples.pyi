from .display import Screen

def _show_colours(
    screen: Screen,
    delay: int,
    colours: dict[str, tuple[int, int, int]],
    colour_set_name: str,
): ...
def show_css_colours(screen: Screen, delay: int = 2): ...
def show_waveshare_colours(screen: Screen, delay: int = 2): ...
def show_discoloration_sample(screen: Screen): ...
