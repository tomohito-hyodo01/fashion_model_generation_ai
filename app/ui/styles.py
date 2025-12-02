"""
Unified style definitions for the Virtual Fashion Try-On application.
Supports multiple themes with dynamic switching and premium visual effects.

Each theme now includes distinct design language:
- Different border radii (sharp vs rounded)
- Different shadows (flat vs elevated)
- Visual effects (glass morphism, gradients, glow)
- Unique button and input styles
"""

from pathlib import Path
from ui.themes import get_theme, ThemeDesign, DEFAULT_THEME

# Get path to icons
_ICONS_PATH = Path(__file__).parent.parent / "assets" / "icons"

# Current theme (can be changed at runtime)
_current_theme_name = DEFAULT_THEME
_current_theme: ThemeDesign = get_theme(DEFAULT_THEME)


def set_theme(theme_name: str):
    """Set the current theme"""
    global _current_theme_name, _current_theme
    _current_theme_name = theme_name
    _current_theme = get_theme(theme_name)
    # Rebuild styles with new theme
    _rebuild_styles()


def get_current_theme_name() -> str:
    """Get the current theme name"""
    return _current_theme_name


# =============================================================================
# Dynamic Color Accessor
# =============================================================================

class Colors:
    """Application color palette - dynamically references current theme"""

    @staticmethod
    def _get(attr: str) -> str:
        return getattr(_current_theme, attr)

    # Primary colors
    @property
    def PRIMARY(self) -> str: return _current_theme.PRIMARY
    @property
    def PRIMARY_HOVER(self) -> str: return _current_theme.PRIMARY_HOVER
    @property
    def PRIMARY_LIGHT(self) -> str: return _current_theme.PRIMARY_LIGHT
    @property
    def PRIMARY_DARK(self) -> str: return _current_theme.PRIMARY_DARK

    # Secondary colors
    @property
    def SECONDARY(self) -> str: return _current_theme.SECONDARY
    @property
    def SECONDARY_HOVER(self) -> str: return _current_theme.SECONDARY_HOVER
    @property
    def SECONDARY_LIGHT(self) -> str: return _current_theme.SECONDARY_LIGHT

    # Accent colors
    @property
    def ACCENT_GREEN(self) -> str: return _current_theme.ACCENT_GREEN
    @property
    def ACCENT_ORANGE(self) -> str: return _current_theme.ACCENT_ORANGE
    @property
    def ACCENT_RED(self) -> str: return _current_theme.ACCENT_RED
    @property
    def ACCENT_PINK(self) -> str: return _current_theme.ACCENT_PINK

    # Background colors
    @property
    def BG_MAIN(self) -> str: return _current_theme.BG_MAIN
    @property
    def BG_SECONDARY(self) -> str: return _current_theme.BG_SECONDARY
    @property
    def BG_TERTIARY(self) -> str: return _current_theme.BG_TERTIARY
    @property
    def BG_CARD(self) -> str: return _current_theme.BG_CARD
    @property
    def BG_CARD_HOVER(self) -> str: return _current_theme.BG_CARD_HOVER
    @property
    def BG_INPUT(self) -> str: return _current_theme.BG_INPUT
    @property
    def BG_ELEVATED(self) -> str: return _current_theme.BG_ELEVATED

    # Border colors
    @property
    def BORDER_LIGHT(self) -> str: return _current_theme.BORDER_LIGHT
    @property
    def BORDER_MEDIUM(self) -> str: return _current_theme.BORDER_MEDIUM
    @property
    def BORDER_FOCUS(self) -> str: return _current_theme.BORDER_FOCUS
    @property
    def BORDER_SUBTLE(self) -> str: return _current_theme.BORDER_SUBTLE

    # Text colors
    @property
    def TEXT_PRIMARY(self) -> str: return _current_theme.TEXT_PRIMARY
    @property
    def TEXT_SECONDARY(self) -> str: return _current_theme.TEXT_SECONDARY
    @property
    def TEXT_MUTED(self) -> str: return _current_theme.TEXT_MUTED
    @property
    def TEXT_WHITE(self) -> str: return _current_theme.TEXT_WHITE
    @property
    def TEXT_ON_PRIMARY(self) -> str: return _current_theme.TEXT_ON_PRIMARY

    # Status colors
    @property
    def SUCCESS(self) -> str: return _current_theme.SUCCESS
    @property
    def SUCCESS_LIGHT(self) -> str: return _current_theme.SUCCESS_LIGHT
    @property
    def WARNING(self) -> str: return _current_theme.WARNING
    @property
    def WARNING_LIGHT(self) -> str: return _current_theme.WARNING_LIGHT
    @property
    def ERROR(self) -> str: return _current_theme.ERROR
    @property
    def ERROR_LIGHT(self) -> str: return _current_theme.ERROR_LIGHT
    @property
    def INFO(self) -> str: return _current_theme.INFO
    @property
    def INFO_LIGHT(self) -> str: return _current_theme.INFO_LIGHT


# Singleton instance
Colors = Colors()


# =============================================================================
# Dynamic Spacing & Sizing (theme-aware)
# =============================================================================

class Spacing:
    """Spacing values - adjusts based on theme's spacing multiplier"""
    @property
    def XS(self) -> int:
        return int(4 * _current_theme.SPACING_NORMAL)
    @property
    def SM(self) -> int:
        return int(8 * _current_theme.SPACING_NORMAL)
    @property
    def MD(self) -> int:
        return int(12 * _current_theme.SPACING_NORMAL)
    @property
    def LG(self) -> int:
        return int(16 * _current_theme.SPACING_NORMAL)
    @property
    def XL(self) -> int:
        return int(24 * _current_theme.SPACING_NORMAL)
    @property
    def XXL(self) -> int:
        return int(32 * _current_theme.SPACING_NORMAL)
    @property
    def XXXL(self) -> int:
        return int(48 * _current_theme.SPACING_NORMAL)


Spacing = Spacing()


class BorderRadius:
    """Border radius values - dynamically from theme"""
    @property
    def XS(self) -> int:
        return max(2, _current_theme.RADIUS_SM - 2)
    @property
    def SM(self) -> int:
        return _current_theme.RADIUS_SM
    @property
    def MD(self) -> int:
        return _current_theme.RADIUS_MD
    @property
    def LG(self) -> int:
        return _current_theme.RADIUS_LG
    @property
    def XL(self) -> int:
        return _current_theme.RADIUS_XL
    @property
    def XXL(self) -> int:
        return _current_theme.RADIUS_XL + 4
    @property
    def ROUND(self) -> int:
        return _current_theme.RADIUS_ROUND


BorderRadius = BorderRadius()


class Shadows:
    """Box shadows - dynamically from theme"""
    @property
    def SM(self) -> str:
        return _current_theme.SHADOW_SM
    @property
    def MD(self) -> str:
        return _current_theme.SHADOW_MD
    @property
    def LG(self) -> str:
        return _current_theme.SHADOW_LG
    @property
    def XL(self) -> str:
        return _current_theme.SHADOW_XL
    @property
    def GLOW(self) -> str:
        return _current_theme.SHADOW_GLOW
    @property
    def INSET(self) -> str:
        return _current_theme.SHADOW_INSET


Shadows = Shadows()


class Fonts:
    """Font size and weight definitions"""
    SIZE_XS = "11px"
    SIZE_SM = "13px"
    SIZE_MD = "15px"
    SIZE_LG = "17px"
    SIZE_XL = "20px"
    SIZE_XXL = "24px"
    SIZE_TITLE = "28px"
    SIZE_HERO = "34px"

    @property
    def WEIGHT_NORMAL(self) -> str:
        return str(_current_theme.FONT_WEIGHT_NORMAL)
    @property
    def WEIGHT_MEDIUM(self) -> str:
        return str(_current_theme.FONT_WEIGHT_MEDIUM)
    @property
    def WEIGHT_SEMIBOLD(self) -> str:
        return str(_current_theme.FONT_WEIGHT_SEMIBOLD)
    @property
    def WEIGHT_BOLD(self) -> str:
        return str(_current_theme.FONT_WEIGHT_BOLD)


Fonts = Fonts()


# =============================================================================
# Component Styles - Dynamically generated with premium effects
# =============================================================================

class Styles:
    """Pre-defined component styles - rebuilt when theme changes"""

    # These will be populated by _rebuild_styles()
    MAIN_WINDOW = ""
    CENTRAL_WIDGET = ""
    GROUP_BOX = ""
    BUTTON_PRIMARY = ""
    BUTTON_SECONDARY = ""
    BUTTON_SUCCESS = ""
    BUTTON_DANGER = ""
    BUTTON_GHOST = ""
    BUTTON_ICON = ""
    INPUT_FIELD = ""
    TEXT_EDIT = ""
    COMBO_BOX = ""
    SPIN_BOX = ""
    CHECK_BOX = ""
    RADIO_BUTTON = ""
    PROGRESS_BAR = ""
    SCROLL_AREA = ""
    LIST_WIDGET = ""
    TAB_WIDGET = ""
    LABEL_TITLE = ""
    LABEL_SUBTITLE = ""
    LABEL_MUTED = ""
    LABEL_HINT = ""
    LABEL_BADGE = ""
    CARD = ""
    CARD_HOVER = ""
    CARD_SELECTED = ""
    CARD_ELEVATED = ""
    TOOL_BUTTON = ""
    CHAT_BUBBLE_USER = ""
    CHAT_BUBBLE_AI = ""
    MENU_BAR = ""
    STATUS_BAR = ""
    DIALOG = ""
    THUMBNAIL = ""
    THUMBNAIL_SELECTED = ""
    EMPTY_STATE = ""
    SPLITTER = ""
    SLIDER = ""
    TOOLTIP = ""


def _get_button_background(t: ThemeDesign, base_color: str, hover_color: str) -> tuple:
    """Generate button background based on theme style"""
    if t.BUTTON_STYLE == "gradient":
        # Premium gradient button
        bg = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {_lighten_color(base_color, 10)}, stop:1 {base_color})"
        bg_hover = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {_lighten_color(hover_color, 10)}, stop:1 {hover_color})"
        return bg, bg_hover
    elif t.BUTTON_STYLE == "glass":
        # Glass morphism button
        return f"rgba({_hex_to_rgb(base_color)}, 0.85)", f"rgba({_hex_to_rgb(hover_color)}, 0.9)"
    else:
        # Solid button
        return base_color, hover_color


def _lighten_color(hex_color: str, percent: int) -> str:
    """Lighten a hex color by a percentage"""
    hex_color = hex_color.lstrip('#')
    r = min(255, int(hex_color[0:2], 16) + int(255 * percent / 100))
    g = min(255, int(hex_color[2:4], 16) + int(255 * percent / 100))
    b = min(255, int(hex_color[4:6], 16) + int(255 * percent / 100))
    return f"#{r:02x}{g:02x}{b:02x}"


def _darken_color(hex_color: str, percent: int) -> str:
    """Darken a hex color by a percentage"""
    hex_color = hex_color.lstrip('#')
    r = max(0, int(hex_color[0:2], 16) - int(255 * percent / 100))
    g = max(0, int(hex_color[2:4], 16) - int(255 * percent / 100))
    b = max(0, int(hex_color[4:6], 16) - int(255 * percent / 100))
    return f"#{r:02x}{g:02x}{b:02x}"


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB comma-separated string"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"{r}, {g}, {b}"


def _rebuild_styles():
    """Rebuild all style strings with current theme colors and design tokens"""
    t = _current_theme  # shorthand

    # Icon paths (use forward slashes for Qt)
    arrow_down_path = str(_ICONS_PATH / "arrow_down.svg").replace("\\", "/")
    arrow_up_path = str(_ICONS_PATH / "arrow_up.svg").replace("\\", "/")
    check_icon_path = str(_ICONS_PATH / "check.svg").replace("\\", "/")
    radio_checked_path = str(_ICONS_PATH / "radio_checked.svg").replace("\\", "/")
    radio_unchecked_path = str(_ICONS_PATH / "radio_unchecked.svg").replace("\\", "/")

    # Calculate derived values
    spacing_mult = getattr(t, 'SPACING_RELAXED', 1.0) if hasattr(t, 'SPACING_RELAXED') else 1.0
    base_padding = int(10 * spacing_mult)
    large_padding = int(12 * spacing_mult)

    # Get button backgrounds based on theme style
    btn_bg, btn_bg_hover = _get_button_background(t, t.PRIMARY, t.PRIMARY_HOVER)

    # Determine if we should use glow effects
    glow_focus = ""
    if t.USE_GLOW and t.SHADOW_GLOW:
        glow_focus = f"box-shadow: {t.SHADOW_GLOW};"

    # Background gradient for main window (if theme uses gradients)
    main_bg = t.BG_SECONDARY
    if t.USE_GRADIENT_BG and t.GRADIENT_START and t.GRADIENT_END:
        main_bg = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {t.GRADIENT_START}, stop:1 {t.GRADIENT_END})"

    # ==========================================================================
    # MAIN WINDOW & CONTAINERS
    # ==========================================================================

    Styles.MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {main_bg};
        }}
    """

    Styles.CENTRAL_WIDGET = f"""
        QWidget#centralWidget {{
            background-color: {main_bg};
        }}
    """

    # Card border style based on theme
    card_border = f"1px solid {t.BORDER_LIGHT}"
    if t.CARD_BORDER_STYLE == "none":
        card_border = "none"

    # Clean GroupBox styling with subtle accent
    Styles.GROUP_BOX = f"""
        QGroupBox {{
            font-weight: {t.FONT_WEIGHT_MEDIUM};
            font-size: {Fonts.SIZE_SM};
            color: {t.TEXT_SECONDARY};
            background-color: {t.BG_CARD};
            border: 1px solid {t.BORDER_LIGHT};
            border-top: 2px solid {t.PRIMARY};
            border-radius: {t.RADIUS_MD}px;
            margin-top: 8px;
            padding: 16px;
            padding-top: 28px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            top: 8px;
            padding: 2px 8px;
            background-color: {t.BG_CARD};
            color: {t.PRIMARY};
            font-weight: {t.FONT_WEIGHT_SEMIBOLD};
            font-size: {Fonts.SIZE_SM};
        }}
    """

    # ==========================================================================
    # BUTTONS - Premium styles with theme-specific design
    # ==========================================================================

    # Primary Button
    if t.BUTTON_STYLE == "gradient":
        Styles.BUTTON_PRIMARY = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {_lighten_color(t.PRIMARY, 8)},
                    stop:0.5 {t.PRIMARY},
                    stop:1 {_darken_color(t.PRIMARY, 5)});
                color: {t.TEXT_ON_PRIMARY};
                font-weight: {t.FONT_WEIGHT_MEDIUM};
                font-size: {Fonts.SIZE_SM};
                border: none;
                border-radius: {t.RADIUS_MD}px;
                padding: {base_padding}px {int(20 * spacing_mult)}px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {_lighten_color(t.PRIMARY_HOVER, 8)},
                    stop:0.5 {t.PRIMARY_HOVER},
                    stop:1 {t.PRIMARY});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {t.PRIMARY},
                    stop:1 {t.PRIMARY_DARK});
            }}
            QPushButton:disabled {{
                background-color: {t.BORDER_LIGHT};
                color: {t.TEXT_MUTED};
            }}
        """
    elif t.BUTTON_STYLE == "outline":
        Styles.BUTTON_PRIMARY = f"""
            QPushButton {{
                background-color: transparent;
                color: {t.PRIMARY};
                font-weight: {t.FONT_WEIGHT_MEDIUM};
                font-size: {Fonts.SIZE_SM};
                border: 2px solid {t.PRIMARY};
                border-radius: {t.RADIUS_MD}px;
                padding: {base_padding - 2}px {int(18 * spacing_mult)}px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {t.PRIMARY};
                color: {t.TEXT_ON_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {t.PRIMARY_DARK};
                border-color: {t.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                border-color: {t.BORDER_LIGHT};
                color: {t.TEXT_MUTED};
            }}
        """
    else:  # solid
        Styles.BUTTON_PRIMARY = f"""
            QPushButton {{
                background-color: {t.PRIMARY};
                color: {t.TEXT_ON_PRIMARY};
                font-weight: {t.FONT_WEIGHT_MEDIUM};
                font-size: {Fonts.SIZE_SM};
                border: none;
                border-radius: {t.RADIUS_MD}px;
                padding: {base_padding}px {int(20 * spacing_mult)}px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {t.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {t.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {t.BORDER_LIGHT};
                color: {t.TEXT_MUTED};
            }}
        """

    # Secondary Button
    if t.INPUT_STYLE == "minimal":
        Styles.BUTTON_SECONDARY = f"""
            QPushButton {{
                background-color: transparent;
                color: {t.TEXT_PRIMARY};
                font-weight: {t.FONT_WEIGHT_MEDIUM};
                font-size: {Fonts.SIZE_SM};
                border: none;
                border-radius: {t.RADIUS_MD}px;
                padding: {base_padding}px {int(20 * spacing_mult)}px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {t.BG_TERTIARY};
            }}
            QPushButton:pressed {{
                background-color: {t.BORDER_LIGHT};
            }}
            QPushButton:disabled {{
                color: {t.TEXT_MUTED};
            }}
        """
    else:
        Styles.BUTTON_SECONDARY = f"""
            QPushButton {{
                background-color: {t.BG_INPUT};
                color: {t.TEXT_PRIMARY};
                font-weight: {t.FONT_WEIGHT_MEDIUM};
                font-size: {Fonts.SIZE_SM};
                border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
                border-radius: {t.RADIUS_MD}px;
                padding: {base_padding}px {int(20 * spacing_mult)}px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {t.BG_TERTIARY};
                border-color: {t.BORDER_MEDIUM};
            }}
            QPushButton:pressed {{
                background-color: {t.BORDER_LIGHT};
            }}
            QPushButton:disabled {{
                background-color: {t.BG_INPUT};
                color: {t.TEXT_MUTED};
            }}
        """

    # Success Button (prominent action)
    if t.BUTTON_STYLE == "gradient":
        Styles.BUTTON_SUCCESS = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {_lighten_color(t.ACCENT_GREEN, 10)},
                    stop:0.5 {t.ACCENT_GREEN},
                    stop:1 {_darken_color(t.ACCENT_GREEN, 8)});
                color: {t.TEXT_ON_PRIMARY};
                font-weight: {t.FONT_WEIGHT_SEMIBOLD};
                font-size: {Fonts.SIZE_MD};
                border: none;
                border-radius: {t.RADIUS_MD}px;
                padding: {large_padding}px {int(28 * spacing_mult)}px;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {_lighten_color(t.ACCENT_GREEN, 15)},
                    stop:0.5 {_lighten_color(t.ACCENT_GREEN, 5)},
                    stop:1 {t.ACCENT_GREEN});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {t.ACCENT_GREEN},
                    stop:1 {_darken_color(t.ACCENT_GREEN, 15)});
            }}
            QPushButton:disabled {{
                background-color: {t.BORDER_LIGHT};
                color: {t.TEXT_MUTED};
            }}
        """
    else:
        Styles.BUTTON_SUCCESS = f"""
            QPushButton {{
                background-color: {t.ACCENT_GREEN};
                color: {t.TEXT_ON_PRIMARY};
                font-weight: {t.FONT_WEIGHT_SEMIBOLD};
                font-size: {Fonts.SIZE_MD};
                border: none;
                border-radius: {t.RADIUS_MD}px;
                padding: {large_padding}px {int(28 * spacing_mult)}px;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background-color: {_lighten_color(t.ACCENT_GREEN, 8)};
            }}
            QPushButton:pressed {{
                background-color: {_darken_color(t.ACCENT_GREEN, 10)};
            }}
            QPushButton:disabled {{
                background-color: {t.BORDER_LIGHT};
                color: {t.TEXT_MUTED};
            }}
        """

    Styles.BUTTON_DANGER = f"""
        QPushButton {{
            background-color: {t.ACCENT_RED};
            color: {t.TEXT_ON_PRIMARY};
            font-weight: {t.FONT_WEIGHT_MEDIUM};
            font-size: {Fonts.SIZE_SM};
            border: none;
            border-radius: {t.RADIUS_MD}px;
            padding: {base_padding}px {int(20 * spacing_mult)}px;
        }}
        QPushButton:hover {{
            background-color: {_lighten_color(t.ACCENT_RED, 8)};
        }}
        QPushButton:pressed {{
            background-color: {_darken_color(t.ACCENT_RED, 10)};
        }}
    """

    Styles.BUTTON_GHOST = f"""
        QPushButton {{
            background-color: transparent;
            color: {t.PRIMARY};
            font-weight: {t.FONT_WEIGHT_MEDIUM};
            font-size: {Fonts.SIZE_SM};
            border: none;
            border-radius: {t.RADIUS_MD}px;
            padding: 8px 16px;
        }}
        QPushButton:hover {{
            background-color: {t.PRIMARY_LIGHT};
        }}
        QPushButton:pressed {{
            background-color: {t.BORDER_LIGHT};
        }}
    """

    Styles.BUTTON_ICON = f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: {t.RADIUS_SM}px;
            padding: 8px;
        }}
        QPushButton:hover {{
            background-color: {t.BG_TERTIARY};
        }}
    """

    # ==========================================================================
    # INPUT FIELDS - Theme-specific styles
    # ==========================================================================

    if t.INPUT_STYLE == "minimal":
        # Notion-style minimal inputs
        Styles.INPUT_FIELD = f"""
            QLineEdit {{
                background-color: transparent;
                color: {t.TEXT_PRIMARY};
                border: none;
                border-bottom: 1px solid {t.BORDER_LIGHT};
                border-radius: 0px;
                padding: {base_padding}px 4px;
                font-size: {Fonts.SIZE_SM};
                selection-background-color: {t.PRIMARY};
                selection-color: {t.TEXT_ON_PRIMARY};
            }}
            QLineEdit:hover {{
                border-bottom-color: {t.BORDER_MEDIUM};
            }}
            QLineEdit:focus {{
                border-bottom: 2px solid {t.PRIMARY};
                padding-bottom: {base_padding - 1}px;
            }}
            QLineEdit:disabled {{
                color: {t.TEXT_MUTED};
            }}
            QLineEdit::placeholder {{
                color: {t.TEXT_MUTED};
            }}
        """
    elif t.INPUT_STYLE == "outline":
        # Clean outline style with focus glow
        focus_extra = ""
        if t.USE_GLOW:
            focus_extra = f"/* glow effect */"

        Styles.INPUT_FIELD = f"""
            QLineEdit {{
                background-color: {t.BG_INPUT};
                color: {t.TEXT_PRIMARY};
                border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
                border-radius: {t.RADIUS_MD}px;
                padding: {base_padding}px {int(14 * spacing_mult)}px;
                font-size: {Fonts.SIZE_SM};
                selection-background-color: {t.PRIMARY};
                selection-color: {t.TEXT_ON_PRIMARY};
            }}
            QLineEdit:hover {{
                border-color: {t.BORDER_MEDIUM};
                background-color: {t.BG_CARD};
            }}
            QLineEdit:focus {{
                border: {t.BORDER_WIDTH_FOCUS}px solid {t.PRIMARY};
                padding: {base_padding - 1}px {int(13 * spacing_mult)}px;
                background-color: {t.BG_CARD};
            }}
            QLineEdit:disabled {{
                background-color: {t.BG_TERTIARY};
                color: {t.TEXT_MUTED};
            }}
            QLineEdit::placeholder {{
                color: {t.TEXT_MUTED};
            }}
        """
    else:  # filled
        Styles.INPUT_FIELD = f"""
            QLineEdit {{
                background-color: {t.BG_INPUT};
                color: {t.TEXT_PRIMARY};
                border: {t.BORDER_WIDTH}px solid transparent;
                border-radius: {t.RADIUS_MD}px;
                padding: {base_padding}px {int(14 * spacing_mult)}px;
                font-size: {Fonts.SIZE_SM};
                selection-background-color: {t.PRIMARY};
                selection-color: {t.TEXT_ON_PRIMARY};
            }}
            QLineEdit:hover {{
                background-color: {t.BG_TERTIARY};
            }}
            QLineEdit:focus {{
                border: {t.BORDER_WIDTH_FOCUS}px solid {t.PRIMARY};
                padding: {base_padding - 1}px {int(13 * spacing_mult)}px;
                background-color: {t.BG_CARD};
            }}
            QLineEdit:disabled {{
                background-color: {t.BG_TERTIARY};
                color: {t.TEXT_MUTED};
            }}
            QLineEdit::placeholder {{
                color: {t.TEXT_MUTED};
            }}
        """

    Styles.TEXT_EDIT = f"""
        QTextEdit {{
            background-color: {t.BG_INPUT};
            color: {t.TEXT_PRIMARY};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT if t.INPUT_STYLE != 'filled' else 'transparent'};
            border-radius: {t.RADIUS_MD}px;
            padding: {base_padding}px;
            font-size: {Fonts.SIZE_SM};
            selection-background-color: {t.PRIMARY};
        }}
        QTextEdit:hover {{
            border-color: {t.BORDER_MEDIUM if t.INPUT_STYLE != 'filled' else 'transparent'};
            background-color: {t.BG_TERTIARY if t.INPUT_STYLE == 'filled' else t.BG_INPUT};
        }}
        QTextEdit:focus {{
            border: {t.BORDER_WIDTH_FOCUS}px solid {t.PRIMARY};
            padding: {base_padding - 1}px;
            background-color: {t.BG_CARD};
        }}
    """

    Styles.COMBO_BOX = f"""
        QComboBox {{
            background-color: {t.BG_INPUT};
            color: {t.TEXT_PRIMARY};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
            border-radius: {t.RADIUS_MD}px;
            padding: {base_padding}px {int(14 * spacing_mult)}px;
            padding-right: 32px;
            font-size: {Fonts.SIZE_SM};
            min-width: 100px;
            min-height: 20px;
        }}
        QComboBox:hover {{
            border-color: {t.BORDER_MEDIUM};
            background-color: {t.BG_CARD};
        }}
        QComboBox:focus {{
            border: {t.BORDER_WIDTH_FOCUS}px solid {t.PRIMARY};
            padding: {base_padding - 1}px {int(13 * spacing_mult)}px;
            padding-right: 31px;
        }}
        QComboBox:disabled {{
            background-color: {t.BG_TERTIARY};
            color: {t.TEXT_MUTED};
            border-color: {t.BORDER_LIGHT};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 32px;
            background: transparent;
            subcontrol-position: center right;
            subcontrol-origin: padding;
        }}
        QComboBox::down-arrow {{
            image: url({arrow_down_path});
            width: 12px;
            height: 12px;
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t.BG_ELEVATED};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
            border-radius: {t.RADIUS_MD}px;
            selection-background-color: {t.PRIMARY_LIGHT};
            selection-color: {t.TEXT_PRIMARY};
            padding: 4px;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            min-height: 32px;
            padding: 8px 12px;
            border-radius: {t.RADIUS_SM}px;
            color: {t.TEXT_PRIMARY};
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {t.BG_TERTIARY};
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: {t.PRIMARY_LIGHT};
            color: {t.PRIMARY};
        }}
    """

    Styles.SPIN_BOX = f"""
        QSpinBox, QDoubleSpinBox {{
            background-color: {t.BG_CARD};
            color: {t.TEXT_PRIMARY};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
            border-radius: {t.RADIUS_MD}px;
            padding: {base_padding}px {int(14 * spacing_mult)}px;
            font-size: {Fonts.SIZE_SM};
            min-height: 20px;
        }}
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {t.BORDER_MEDIUM};
            background-color: {t.BG_CARD};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: {t.BORDER_WIDTH_FOCUS}px solid {t.PRIMARY};
            padding: {base_padding - 1}px {int(13 * spacing_mult)}px;
            background-color: {t.BG_CARD};
        }}
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            background-color: transparent;
            border: none;
            width: 24px;
            padding: 4px;
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {t.BG_TERTIARY};
        }}
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
            image: url({arrow_up_path});
            width: 10px;
            height: 10px;
        }}
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
            image: url({arrow_down_path});
            width: 10px;
            height: 10px;
        }}
    """

    Styles.CHECK_BOX = f"""
        QCheckBox {{
            color: {t.TEXT_PRIMARY};
            font-size: {Fonts.SIZE_SM};
            spacing: 10px;
            padding: 4px 0;
        }}
        QCheckBox:disabled {{
            color: {t.TEXT_MUTED};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {t.BORDER_MEDIUM};
            border-radius: {t.RADIUS_SM}px;
            background-color: {t.BG_CARD};
        }}
        QCheckBox::indicator:hover {{
            border-color: {t.PRIMARY};
            background-color: {t.PRIMARY_LIGHT};
        }}
        QCheckBox::indicator:checked {{
            background-color: {t.PRIMARY};
            border-color: {t.PRIMARY};
            image: url({check_icon_path});
        }}
        QCheckBox::indicator:checked:hover {{
            background-color: {t.PRIMARY_HOVER};
            border-color: {t.PRIMARY_HOVER};
        }}
        QCheckBox::indicator:disabled {{
            border-color: {t.BORDER_LIGHT};
            background-color: {t.BG_TERTIARY};
        }}
    """

    Styles.RADIO_BUTTON = f"""
        QRadioButton {{
            color: {t.TEXT_PRIMARY};
            font-size: {Fonts.SIZE_SM};
            spacing: 10px;
            padding: 4px 0;
        }}
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            image: url({radio_unchecked_path});
        }}
        QRadioButton::indicator:checked {{
            image: url({radio_checked_path});
        }}
    """

    # Progress bar with theme-appropriate styling
    if t.BUTTON_STYLE == "gradient":
        progress_chunk = f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.PRIMARY},
                stop:1 {_lighten_color(t.PRIMARY, 15)});
        """
    else:
        progress_chunk = f"background-color: {t.PRIMARY};"

    Styles.PROGRESS_BAR = f"""
        QProgressBar {{
            background-color: {t.BG_TERTIARY};
            border: none;
            border-radius: {t.RADIUS_SM}px;
            text-align: center;
            font-weight: {t.FONT_WEIGHT_MEDIUM};
            font-size: {Fonts.SIZE_SM};
            color: {t.TEXT_PRIMARY};
            min-height: 8px;
            max-height: 8px;
        }}
        QProgressBar::chunk {{
            {progress_chunk}
            border-radius: {t.RADIUS_SM}px;
        }}
    """

    Styles.SCROLL_AREA = f"""
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            background-color: transparent;
            width: 8px;
            margin: 4px 2px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {t.BORDER_MEDIUM};
            border-radius: 4px;
            min-height: 32px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {t.TEXT_MUTED};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
        QScrollBar:horizontal {{
            background-color: transparent;
            height: 8px;
            margin: 2px 4px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {t.BORDER_MEDIUM};
            border-radius: 4px;
            min-width: 32px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {t.TEXT_MUTED};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """

    Styles.LIST_WIDGET = f"""
        QListWidget {{
            background-color: transparent;
            border: none;
            padding: 4px;
            outline: none;
        }}
        QListWidget::item {{
            background-color: {t.BG_CARD};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_SUBTLE};
            border-radius: {t.RADIUS_MD}px;
            padding: {base_padding}px;
            margin: 3px 0;
            color: {t.TEXT_PRIMARY};
        }}
        QListWidget::item:hover {{
            background-color: {t.BG_CARD_HOVER};
            border-color: {t.BORDER_LIGHT};
        }}
        QListWidget::item:selected {{
            background-color: {t.PRIMARY_LIGHT};
            border: {t.BORDER_WIDTH}px solid {t.PRIMARY};
            color: {t.TEXT_PRIMARY};
        }}
    """

    Styles.TAB_WIDGET = f"""
        QTabWidget::pane {{
            background-color: {t.BG_CARD};
            border: 1px solid {t.BORDER_LIGHT};
            border-top: none;
            border-bottom-left-radius: {t.RADIUS_MD}px;
            border-bottom-right-radius: {t.RADIUS_MD}px;
            padding: {int(12 * spacing_mult)}px;
        }}
        QTabBar {{
            background-color: transparent;
        }}
        QTabBar::tab {{
            background-color: {t.BG_TERTIARY};
            color: {t.TEXT_SECONDARY};
            font-weight: {t.FONT_WEIGHT_MEDIUM};
            font-size: {Fonts.SIZE_SM};
            padding: {base_padding}px {int(20 * spacing_mult)}px;
            margin-right: 2px;
            border-top-left-radius: {t.RADIUS_MD}px;
            border-top-right-radius: {t.RADIUS_MD}px;
            border: 1px solid {t.BORDER_LIGHT};
            border-bottom: none;
        }}
        QTabBar::tab:hover {{
            background-color: {t.BG_CARD_HOVER};
            color: {t.TEXT_PRIMARY};
        }}
        QTabBar::tab:selected {{
            background-color: {t.BG_CARD};
            color: {t.PRIMARY};
            font-weight: {t.FONT_WEIGHT_SEMIBOLD};
            border-color: {t.BORDER_LIGHT};
            border-bottom: 1px solid {t.BG_CARD};
            margin-bottom: -1px;
        }}
    """

    # ==========================================================================
    # LABELS
    # ==========================================================================

    Styles.LABEL_TITLE = f"""
        QLabel {{
            font-weight: {t.FONT_WEIGHT_SEMIBOLD};
            font-size: {Fonts.SIZE_XL};
            color: {t.TEXT_PRIMARY};
            padding: 4px 0;
        }}
    """

    Styles.LABEL_SUBTITLE = f"""
        QLabel {{
            font-weight: {t.FONT_WEIGHT_MEDIUM};
            font-size: {Fonts.SIZE_MD};
            color: {t.TEXT_PRIMARY};
        }}
    """

    Styles.LABEL_MUTED = f"""
        QLabel {{
            font-size: {Fonts.SIZE_SM};
            color: {t.TEXT_SECONDARY};
        }}
    """

    Styles.LABEL_HINT = f"""
        QLabel {{
            font-size: {Fonts.SIZE_XS};
            color: {t.TEXT_MUTED};
            padding: 2px 0;
        }}
    """

    # Badge with theme-appropriate style
    if t.BUTTON_STYLE == "gradient":
        badge_bg = f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {t.PRIMARY},
                stop:1 {_lighten_color(t.PRIMARY, 10)});
        """
    else:
        badge_bg = f"background-color: {t.PRIMARY};"

    Styles.LABEL_BADGE = f"""
        QLabel {{
            font-size: {Fonts.SIZE_XS};
            font-weight: {t.FONT_WEIGHT_SEMIBOLD};
            color: {t.TEXT_ON_PRIMARY};
            {badge_bg}
            padding: 4px 10px;
            border-radius: {t.RADIUS_ROUND}px;
        }}
    """

    # ==========================================================================
    # CARDS - Premium elevated design
    # ==========================================================================

    card_shadow = ""
    if t.CARD_ELEVATED:
        card_shadow = f"/* shadow: {t.SHADOW_SM} */"

    Styles.CARD = f"""
        QFrame {{
            background-color: {t.BG_CARD};
            border: {card_border};
            border-radius: {t.RADIUS_LG}px;
        }}
    """

    Styles.CARD_HOVER = f"""
        QFrame {{
            background-color: {t.BG_CARD};
            border: {card_border};
            border-radius: {t.RADIUS_LG}px;
        }}
        QFrame:hover {{
            border-color: {t.BORDER_MEDIUM};
            background-color: {t.BG_CARD_HOVER};
        }}
    """

    Styles.CARD_SELECTED = f"""
        QFrame {{
            background-color: {t.PRIMARY_LIGHT};
            border: {t.BORDER_WIDTH_FOCUS}px solid {t.PRIMARY};
            border-radius: {t.RADIUS_LG}px;
        }}
    """

    Styles.CARD_ELEVATED = f"""
        QFrame {{
            background-color: {t.BG_ELEVATED};
            border: {'none' if t.CARD_ELEVATED else card_border};
            border-radius: {t.RADIUS_LG}px;
        }}
    """

    Styles.TOOL_BUTTON = f"""
        QToolButton {{
            background-color: {t.BG_CARD};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
            border-radius: {t.RADIUS_MD}px;
            padding: 8px;
            font-size: {Fonts.SIZE_SM};
            color: {t.TEXT_PRIMARY};
        }}
        QToolButton:hover {{
            border-color: {t.BORDER_MEDIUM};
            background-color: {t.BG_CARD_HOVER};
        }}
        QToolButton:checked {{
            border: {t.BORDER_WIDTH_FOCUS}px solid {t.PRIMARY};
            background-color: {t.PRIMARY_LIGHT};
            color: {t.PRIMARY};
        }}
    """

    # ==========================================================================
    # CHAT BUBBLES
    # ==========================================================================

    if t.BUTTON_STYLE == "gradient":
        user_bubble_bg = f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {_lighten_color(t.PRIMARY, 5)},
                stop:1 {t.PRIMARY});
        """
    else:
        user_bubble_bg = f"background-color: {t.PRIMARY};"

    Styles.CHAT_BUBBLE_USER = f"""
        QFrame {{
            {user_bubble_bg}
            border: none;
            border-radius: {t.RADIUS_LG}px;
            padding: {large_padding}px;
        }}
    """

    Styles.CHAT_BUBBLE_AI = f"""
        QFrame {{
            background-color: {t.BG_TERTIARY};
            border: none;
            border-radius: {t.RADIUS_LG}px;
            padding: {large_padding}px;
        }}
    """

    # ==========================================================================
    # MENU & STATUS BAR
    # ==========================================================================

    Styles.MENU_BAR = f"""
        QMenuBar {{
            background-color: {t.BG_CARD};
            color: {t.TEXT_PRIMARY};
            font-size: {Fonts.SIZE_SM};
            padding: 6px 8px;
            border-bottom: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
        }}
        QMenuBar::item {{
            padding: 6px 12px;
            border-radius: {t.RADIUS_SM}px;
            margin: 0 2px;
        }}
        QMenuBar::item:selected {{
            background-color: {t.BG_TERTIARY};
        }}
        QMenu {{
            background-color: {t.BG_ELEVATED};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
            border-radius: {t.RADIUS_MD}px;
            padding: 6px;
        }}
        QMenu::item {{
            padding: 8px 20px;
            border-radius: {t.RADIUS_SM}px;
            margin: 2px 4px;
            color: {t.TEXT_PRIMARY};
        }}
        QMenu::item:selected {{
            background-color: {t.PRIMARY_LIGHT};
            color: {t.PRIMARY};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {t.BORDER_LIGHT};
            margin: 6px 12px;
        }}
        QMenu::indicator {{
            width: 16px;
            height: 16px;
            margin-left: 8px;
        }}
        QMenu::indicator:checked {{
            image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNCIgaGVpZ2h0PSIxNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMwMDdBRkYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiI+PC9wb2x5bGluZT48L3N2Zz4=);
        }}
    """

    Styles.STATUS_BAR = f"""
        QStatusBar {{
            background-color: {t.BG_CARD};
            color: {t.TEXT_SECONDARY};
            font-size: {Fonts.SIZE_XS};
            border-top: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
            padding: 6px 12px;
        }}
    """

    Styles.DIALOG = f"""
        QDialog {{
            background-color: {t.BG_SECONDARY};
        }}
    """

    # ==========================================================================
    # THUMBNAILS & IMAGES
    # ==========================================================================

    Styles.THUMBNAIL = f"""
        QLabel {{
            background-color: {t.BG_TERTIARY};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
            border-radius: {t.RADIUS_MD}px;
        }}
    """

    Styles.THUMBNAIL_SELECTED = f"""
        QLabel {{
            background-color: {t.PRIMARY_LIGHT};
            border: {t.BORDER_WIDTH_FOCUS}px solid {t.PRIMARY};
            border-radius: {t.RADIUS_MD}px;
        }}
    """

    Styles.EMPTY_STATE = f"""
        QLabel {{
            background-color: {t.BG_TERTIARY};
            color: {t.TEXT_MUTED};
            border: 2px dashed {t.BORDER_MEDIUM};
            border-radius: {t.RADIUS_LG}px;
            font-size: {Fonts.SIZE_SM};
        }}
    """

    # ==========================================================================
    # MISCELLANEOUS
    # ==========================================================================

    Styles.SPLITTER = f"""
        QSplitter::handle {{
            background-color: {t.BORDER_LIGHT};
            width: 1px;
            margin: 0 6px;
        }}
        QSplitter::handle:hover {{
            background-color: {t.PRIMARY};
        }}
    """

    # Slider with theme-appropriate handle
    if t.BUTTON_STYLE == "gradient":
        slider_handle = f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {_lighten_color(t.PRIMARY, 10)},
                stop:1 {t.PRIMARY});
        """
    else:
        slider_handle = f"background-color: {t.PRIMARY};"

    Styles.SLIDER = f"""
        QSlider::groove:horizontal {{
            background-color: {t.BG_TERTIARY};
            height: 4px;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            {slider_handle}
            border: none;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background-color: {t.PRIMARY_HOVER};
        }}
        QSlider::sub-page:horizontal {{
            background-color: {t.PRIMARY};
            border-radius: 2px;
        }}
    """

    # Tooltip with theme colors
    tooltip_bg = t.TEXT_PRIMARY if t.BG_MAIN.startswith('#F') or t.BG_MAIN.startswith('#f') else t.BG_ELEVATED
    tooltip_text = t.TEXT_WHITE if t.BG_MAIN.startswith('#F') or t.BG_MAIN.startswith('#f') else t.TEXT_PRIMARY

    Styles.TOOLTIP = f"""
        QToolTip {{
            background-color: {tooltip_bg};
            color: {tooltip_text};
            border: {t.BORDER_WIDTH}px solid {t.BORDER_LIGHT};
            border-radius: {t.RADIUS_SM}px;
            padding: 6px 10px;
            font-size: {Fonts.SIZE_XS};
        }}
    """


# Initialize styles on module load
_rebuild_styles()


# =============================================================================
# Compatibility aliases (for existing code using old static values)
# =============================================================================

# These provide backwards compatibility for code expecting static class attributes
class _StaticSpacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48


class _StaticBorderRadius:
    XS = 4
    SM = 6
    MD = 8
    LG = 12
    XL = 16
    XXL = 20
    ROUND = 9999


# =============================================================================
# Utility Functions
# =============================================================================

def apply_global_style(app):
    """Apply global application style"""
    t = _current_theme
    global_style = f"""
        * {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }}
        {Styles.TOOLTIP}
    """
    app.setStyleSheet(global_style)


def get_gradient_css(start_color: str, end_color: str, direction: str = "horizontal") -> str:
    """Generate gradient CSS for use in stylesheets"""
    if direction == "horizontal":
        return f"""qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {start_color}, stop: 1 {end_color})"""
    else:
        return f"""qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {start_color}, stop: 1 {end_color})"""


def get_theme_preview_style(theme_name: str) -> str:
    """Get a preview style string for theme selection UI"""
    theme = get_theme(theme_name)
    return f"""
        background-color: {theme.BG_CARD};
        border: 2px solid {theme.BORDER_LIGHT};
        border-radius: {theme.RADIUS_MD}px;
        color: {theme.TEXT_PRIMARY};
    """
