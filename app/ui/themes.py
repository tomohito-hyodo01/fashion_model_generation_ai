"""
Theme definitions for the Virtual Fashion Try-On application.

Each theme includes not just colors but complete design tokens:
- Colors (backgrounds, text, accents)
- Border radius (sharp to rounded)
- Shadows (flat to elevated)
- Border styles (none to prominent)
- Spacing adjustments
- Visual effects (gradients, glass, glow)

Sources:
- Apple HIG: https://developer.apple.com/design/human-interface-guidelines/
- iOS System Colors: https://noahgilmore.com/blog/dark-mode-uicolor-compatibility
- Notion Colors: https://docs.super.so/notion-colors
- VS Code: https://code.visualstudio.com/api/references/theme-color
- GitHub Primer: https://primer.style/design/foundations/color/
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ThemeDesign:
    """Complete theme design tokens including visual effects"""

    # === Colors ===
    # Primary action color
    PRIMARY: str
    PRIMARY_HOVER: str
    PRIMARY_LIGHT: str
    PRIMARY_DARK: str

    # Secondary action color
    SECONDARY: str
    SECONDARY_HOVER: str
    SECONDARY_LIGHT: str

    # Semantic accent colors
    ACCENT_GREEN: str
    ACCENT_ORANGE: str
    ACCENT_RED: str
    ACCENT_PINK: str

    # Background hierarchy
    BG_MAIN: str
    BG_SECONDARY: str
    BG_TERTIARY: str
    BG_CARD: str
    BG_CARD_HOVER: str
    BG_INPUT: str
    BG_ELEVATED: str

    # Border colors
    BORDER_LIGHT: str
    BORDER_MEDIUM: str
    BORDER_FOCUS: str
    BORDER_SUBTLE: str

    # Text colors
    TEXT_PRIMARY: str
    TEXT_SECONDARY: str
    TEXT_MUTED: str
    TEXT_WHITE: str
    TEXT_ON_PRIMARY: str

    # Status colors
    SUCCESS: str
    SUCCESS_LIGHT: str
    WARNING: str
    WARNING_LIGHT: str
    ERROR: str
    ERROR_LIGHT: str
    INFO: str
    INFO_LIGHT: str

    # === Design Tokens ===
    # Border radius
    RADIUS_SM: int = 6
    RADIUS_MD: int = 10
    RADIUS_LG: int = 14
    RADIUS_XL: int = 20
    RADIUS_ROUND: int = 9999

    # Border width
    BORDER_WIDTH: int = 1
    BORDER_WIDTH_FOCUS: int = 2

    # Shadows (CSS box-shadow format)
    SHADOW_SM: str = "0 1px 2px rgba(0,0,0,0.05)"
    SHADOW_MD: str = "0 4px 12px rgba(0,0,0,0.1)"
    SHADOW_LG: str = "0 8px 24px rgba(0,0,0,0.15)"
    SHADOW_XL: str = "0 16px 48px rgba(0,0,0,0.2)"
    SHADOW_GLOW: str = ""  # Glow effect for dark themes
    SHADOW_INSET: str = ""  # Inset shadow for inputs

    # Spacing multipliers
    SPACING_TIGHT: float = 0.8
    SPACING_NORMAL: float = 1.0
    SPACING_RELAXED: float = 1.2

    # Typography
    FONT_WEIGHT_NORMAL: int = 400
    FONT_WEIGHT_MEDIUM: int = 500
    FONT_WEIGHT_SEMIBOLD: int = 600
    FONT_WEIGHT_BOLD: int = 700

    # Visual effects
    USE_GLASS_EFFECT: bool = False
    GLASS_BLUR: int = 20
    GLASS_OPACITY: float = 0.7

    USE_GRADIENT_BG: bool = False
    GRADIENT_START: str = ""
    GRADIENT_END: str = ""
    GRADIENT_ANGLE: int = 135

    USE_GLOW: bool = False
    GLOW_COLOR: str = ""
    GLOW_SPREAD: int = 20

    # Card style
    CARD_BORDER_STYLE: str = "solid"  # solid, none, gradient
    CARD_ELEVATED: bool = True

    # Button style
    BUTTON_STYLE: str = "solid"  # solid, gradient, outline, glass

    # Input style
    INPUT_STYLE: str = "filled"  # filled, outline, minimal


# =============================================================================
# Theme Definitions - Complete Design Systems
# =============================================================================

THEMES: Dict[str, ThemeDesign] = {

    # =========================================================================
    # macOS Light - Premium Apple-style with Glass Morphism
    # =========================================================================
    "macos_light": ThemeDesign(
        # Colors - Official Apple system colors
        PRIMARY="#007AFF",
        PRIMARY_HOVER="#0066D6",
        PRIMARY_LIGHT="#E5F2FF",
        PRIMARY_DARK="#0055B3",
        SECONDARY="#5856D6",
        SECONDARY_HOVER="#4240B0",
        SECONDARY_LIGHT="#EDEDFC",
        ACCENT_GREEN="#28CD41",
        ACCENT_ORANGE="#FF9500",
        ACCENT_RED="#FF3B30",
        ACCENT_PINK="#FF2D55",

        # Backgrounds - Clean with subtle depth
        BG_MAIN="#F5F5F7",
        BG_SECONDARY="#FFFFFF",
        BG_TERTIARY="#F0F0F2",
        BG_CARD="#FFFFFF",
        BG_CARD_HOVER="#FAFAFA",
        BG_INPUT="#FFFFFF",
        BG_ELEVATED="#FFFFFF",

        # Borders
        BORDER_LIGHT="#E5E5EA",
        BORDER_MEDIUM="#D1D1D6",
        BORDER_FOCUS="#007AFF",
        BORDER_SUBTLE="#F0F0F5",

        # Text
        TEXT_PRIMARY="#1D1D1F",
        TEXT_SECONDARY="#6E6E73",
        TEXT_MUTED="#8E8E93",
        TEXT_WHITE="#FFFFFF",
        TEXT_ON_PRIMARY="#FFFFFF",

        # Status
        SUCCESS="#28CD41",
        SUCCESS_LIGHT="#E5F8E8",
        WARNING="#FF9500",
        WARNING_LIGHT="#FFF4E5",
        ERROR="#FF3B30",
        ERROR_LIGHT="#FFE5E4",
        INFO="#007AFF",
        INFO_LIGHT="#E5F2FF",

        # Design - Elegant, spacious, premium
        RADIUS_SM=8,
        RADIUS_MD=12,
        RADIUS_LG=16,
        RADIUS_XL=24,

        SHADOW_SM="0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)",
        SHADOW_MD="0 4px 6px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        SHADOW_LG="0 10px 25px rgba(0,0,0,0.06), 0 6px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)",
        SHADOW_XL="0 20px 40px rgba(0,0,0,0.08), 0 10px 20px rgba(0,0,0,0.06)",
        SHADOW_INSET="inset 0 1px 2px rgba(0,0,0,0.06)",

        SPACING_RELAXED=1.15,

        USE_GLASS_EFFECT=True,
        GLASS_BLUR=24,
        GLASS_OPACITY=0.85,

        USE_GRADIENT_BG=True,
        GRADIENT_START="#F5F5F7",
        GRADIENT_END="#EAEAEC",
        GRADIENT_ANGLE=180,

        CARD_BORDER_STYLE="solid",
        CARD_ELEVATED=True,
        BUTTON_STYLE="gradient",
        INPUT_STYLE="outline",
    ),

    # =========================================================================
    # macOS Dark - Deep Black with Subtle Glow
    # =========================================================================
    "macos_dark": ThemeDesign(
        # Colors - Apple Dark Mode
        PRIMARY="#0A84FF",
        PRIMARY_HOVER="#409CFF",
        PRIMARY_LIGHT="#1C3D5A",
        PRIMARY_DARK="#0066CC",
        SECONDARY="#5E5CE6",
        SECONDARY_HOVER="#7A78EE",
        SECONDARY_LIGHT="#2A2A4A",
        ACCENT_GREEN="#32D74B",
        ACCENT_ORANGE="#FF9F0A",
        ACCENT_RED="#FF453A",
        ACCENT_PINK="#FF375F",

        # Backgrounds - True black with elevation
        BG_MAIN="#000000",
        BG_SECONDARY="#1C1C1E",
        BG_TERTIARY="#2C2C2E",
        BG_CARD="#1C1C1E",
        BG_CARD_HOVER="#2C2C2E",
        BG_INPUT="#1C1C1E",
        BG_ELEVATED="#2C2C2E",

        # Borders
        BORDER_LIGHT="#38383A",
        BORDER_MEDIUM="#48484A",
        BORDER_FOCUS="#0A84FF",
        BORDER_SUBTLE="#2C2C2E",

        # Text - Softer colors for dark mode (not pure white)
        TEXT_PRIMARY="#E5E5E7",
        TEXT_SECONDARY="#A1A1A6",
        TEXT_MUTED="#6E6E73",
        TEXT_WHITE="#E5E5E7",
        TEXT_ON_PRIMARY="#E5E5E7",

        # Status
        SUCCESS="#32D74B",
        SUCCESS_LIGHT="#0D3B15",
        WARNING="#FF9F0A",
        WARNING_LIGHT="#3D2E08",
        ERROR="#FF453A",
        ERROR_LIGHT="#3D1714",
        INFO="#0A84FF",
        INFO_LIGHT="#0D2847",

        # Design - Deep, glowing, futuristic
        RADIUS_SM=8,
        RADIUS_MD=12,
        RADIUS_LG=16,
        RADIUS_XL=24,

        SHADOW_SM="0 2px 8px rgba(0,0,0,0.4)",
        SHADOW_MD="0 4px 16px rgba(0,0,0,0.5)",
        SHADOW_LG="0 8px 32px rgba(0,0,0,0.6)",
        SHADOW_XL="0 16px 48px rgba(0,0,0,0.7)",
        SHADOW_GLOW="0 0 20px rgba(10,132,255,0.3)",
        SHADOW_INSET="inset 0 1px 0 rgba(255,255,255,0.05)",

        USE_GLASS_EFFECT=True,
        GLASS_BLUR=30,
        GLASS_OPACITY=0.6,

        USE_GLOW=True,
        GLOW_COLOR="#0A84FF",
        GLOW_SPREAD=25,

        CARD_BORDER_STYLE="solid",
        CARD_ELEVATED=True,
        BUTTON_STYLE="gradient",
        INPUT_STYLE="filled",
    ),

    # =========================================================================
    # Notion - Clean Typography-focused Minimalism
    # =========================================================================
    "notion": ThemeDesign(
        # Colors - Notion's warm palette
        PRIMARY="#2383E2",
        PRIMARY_HOVER="#1B6EC2",
        PRIMARY_LIGHT="#E8F4FD",
        PRIMARY_DARK="#1A5BA8",
        SECONDARY="#6940A5",
        SECONDARY_HOVER="#553285",
        SECONDARY_LIGHT="#EAE4F2",
        ACCENT_GREEN="#0F7B6C",
        ACCENT_ORANGE="#D9730D",
        ACCENT_RED="#E03E3E",
        ACCENT_PINK="#AD1A72",

        # Backgrounds - Warm, paper-like
        BG_MAIN="#FFFFFF",
        BG_SECONDARY="#FBFBFA",
        BG_TERTIARY="#F7F6F3",
        BG_CARD="#FFFFFF",
        BG_CARD_HOVER="#F7F6F3",
        BG_INPUT="#FFFFFF",
        BG_ELEVATED="#FFFFFF",

        # Borders - Subtle, warm
        BORDER_LIGHT="#E9E9E7",
        BORDER_MEDIUM="#DFDFDC",
        BORDER_FOCUS="#2383E2",
        BORDER_SUBTLE="#F4F4F2",

        # Text - Warm, readable
        TEXT_PRIMARY="#37352F",
        TEXT_SECONDARY="#6B6B6B",
        TEXT_MUTED="#9B9A97",
        TEXT_WHITE="#FFFFFF",
        TEXT_ON_PRIMARY="#FFFFFF",

        # Status
        SUCCESS="#0F7B6C",
        SUCCESS_LIGHT="#DDEDEA",
        WARNING="#D9730D",
        WARNING_LIGHT="#FAEBDD",
        ERROR="#E03E3E",
        ERROR_LIGHT="#FBE4E4",
        INFO="#2383E2",
        INFO_LIGHT="#DDEBF1",

        # Design - Minimal, content-focused
        RADIUS_SM=4,
        RADIUS_MD=6,
        RADIUS_LG=8,
        RADIUS_XL=12,

        BORDER_WIDTH=1,

        SHADOW_SM="0 1px 2px rgba(0,0,0,0.04)",
        SHADOW_MD="0 2px 8px rgba(55,53,47,0.08)",
        SHADOW_LG="0 4px 16px rgba(55,53,47,0.12)",
        SHADOW_XL="0 8px 32px rgba(55,53,47,0.16)",

        SPACING_NORMAL=1.0,

        USE_GLASS_EFFECT=False,
        USE_GRADIENT_BG=False,

        CARD_BORDER_STYLE="none",
        CARD_ELEVATED=False,
        BUTTON_STYLE="solid",
        INPUT_STYLE="minimal",
    ),

    # =========================================================================
    # VS Code Dark - Developer-focused with Syntax Colors
    # =========================================================================
    "vscode": ThemeDesign(
        # Colors - VS Code Dark+
        PRIMARY="#007ACC",
        PRIMARY_HOVER="#1A8CEB",
        PRIMARY_LIGHT="#264F78",
        PRIMARY_DARK="#005A9E",
        SECONDARY="#C586C0",
        SECONDARY_HOVER="#D59FD6",
        SECONDARY_LIGHT="#3A2A3A",
        ACCENT_GREEN="#4EC9B0",
        ACCENT_ORANGE="#CE9178",
        ACCENT_RED="#F14C4C",
        ACCENT_PINK="#C586C0",

        # Backgrounds - Editor-like
        BG_MAIN="#1E1E1E",
        BG_SECONDARY="#252526",
        BG_TERTIARY="#2D2D2D",
        BG_CARD="#252526",
        BG_CARD_HOVER="#2A2D2E",
        BG_INPUT="#3C3C3C",
        BG_ELEVATED="#333333",

        # Borders
        BORDER_LIGHT="#3C3C3C",
        BORDER_MEDIUM="#4D4D4D",
        BORDER_FOCUS="#007ACC",
        BORDER_SUBTLE="#2D2D2D",

        # Text - Softer colors for dark mode
        TEXT_PRIMARY="#D4D4D4",
        TEXT_SECONDARY="#9D9D9D",
        TEXT_MUTED="#6A6A6A",
        TEXT_WHITE="#D4D4D4",
        TEXT_ON_PRIMARY="#D4D4D4",

        # Status
        SUCCESS="#4EC9B0",
        SUCCESS_LIGHT="#1E3A34",
        WARNING="#CCA700",
        WARNING_LIGHT="#3D3510",
        ERROR="#F14C4C",
        ERROR_LIGHT="#4E1818",
        INFO="#3794FF",
        INFO_LIGHT="#0E3A5E",

        # Design - Functional, dense, efficient
        RADIUS_SM=4,
        RADIUS_MD=6,
        RADIUS_LG=8,
        RADIUS_XL=10,

        SHADOW_SM="0 1px 4px rgba(0,0,0,0.3)",
        SHADOW_MD="0 4px 12px rgba(0,0,0,0.4)",
        SHADOW_LG="0 8px 24px rgba(0,0,0,0.5)",
        SHADOW_XL="0 12px 36px rgba(0,0,0,0.6)",
        SHADOW_INSET="inset 0 0 0 1px rgba(255,255,255,0.05)",

        SPACING_TIGHT=0.9,

        USE_GLASS_EFFECT=False,
        USE_GLOW=True,
        GLOW_COLOR="#007ACC",
        GLOW_SPREAD=15,

        CARD_BORDER_STYLE="solid",
        CARD_ELEVATED=False,
        BUTTON_STYLE="solid",
        INPUT_STYLE="filled",
    ),

    # =========================================================================
    # GitHub Dark - Modern Dark with Green Accents
    # =========================================================================
    "github": ThemeDesign(
        # Colors - GitHub Primer
        PRIMARY="#238636",
        PRIMARY_HOVER="#2EA043",
        PRIMARY_LIGHT="#1B4721",
        PRIMARY_DARK="#196C2E",
        SECONDARY="#58A6FF",
        SECONDARY_HOVER="#79B8FF",
        SECONDARY_LIGHT="#0D2847",
        ACCENT_GREEN="#3FB950",
        ACCENT_ORANGE="#D29922",
        ACCENT_RED="#F85149",
        ACCENT_PINK="#DB61A2",

        # Backgrounds - Blue-tinted dark
        BG_MAIN="#0D1117",
        BG_SECONDARY="#161B22",
        BG_TERTIARY="#21262D",
        BG_CARD="#161B22",
        BG_CARD_HOVER="#1C2128",
        BG_INPUT="#0D1117",
        BG_ELEVATED="#1C2128",

        # Borders
        BORDER_LIGHT="#30363D",
        BORDER_MEDIUM="#484F58",
        BORDER_FOCUS="#238636",
        BORDER_SUBTLE="#21262D",

        # Text - Softer colors for dark mode
        TEXT_PRIMARY="#C9D1D9",
        TEXT_SECONDARY="#8B949E",
        TEXT_MUTED="#6E7681",
        TEXT_WHITE="#C9D1D9",
        TEXT_ON_PRIMARY="#C9D1D9",

        # Status
        SUCCESS="#3FB950",
        SUCCESS_LIGHT="#0B2912",
        WARNING="#D29922",
        WARNING_LIGHT="#3D2E0A",
        ERROR="#F85149",
        ERROR_LIGHT="#4D1B18",
        INFO="#58A6FF",
        INFO_LIGHT="#0D2847",

        # Design - Modern, accessible
        RADIUS_SM=6,
        RADIUS_MD=8,
        RADIUS_LG=12,
        RADIUS_XL=16,

        SHADOW_SM="0 1px 3px rgba(1,4,9,0.5)",
        SHADOW_MD="0 4px 12px rgba(1,4,9,0.6)",
        SHADOW_LG="0 8px 24px rgba(1,4,9,0.7)",
        SHADOW_XL="0 16px 48px rgba(1,4,9,0.8)",
        SHADOW_INSET="inset 0 1px 0 rgba(255,255,255,0.03)",

        USE_GLASS_EFFECT=False,
        USE_GLOW=True,
        GLOW_COLOR="#238636",
        GLOW_SPREAD=20,

        CARD_BORDER_STYLE="solid",
        CARD_ELEVATED=True,
        BUTTON_STYLE="solid",
        INPUT_STYLE="outline",
    ),

    # =========================================================================
    # Luxury Gold - Premium High-end Design
    # =========================================================================
    "luxury": ThemeDesign(
        # Colors - Gold and deep navy
        PRIMARY="#C9A962",
        PRIMARY_HOVER="#D4B978",
        PRIMARY_LIGHT="#F5EED9",
        PRIMARY_DARK="#A68B4B",
        SECONDARY="#1E3A5F",
        SECONDARY_HOVER="#2A4D7A",
        SECONDARY_LIGHT="#E8EDF4",
        ACCENT_GREEN="#6B8E6B",
        ACCENT_ORANGE="#D4A574",
        ACCENT_RED="#B85C5C",
        ACCENT_PINK="#C9A0B0",

        # Backgrounds - Cream and ivory
        BG_MAIN="#FAF9F6",
        BG_SECONDARY="#FFFFFF",
        BG_TERTIARY="#F5F4F1",
        BG_CARD="#FFFFFF",
        BG_CARD_HOVER="#FDFCFA",
        BG_INPUT="#FFFFFF",
        BG_ELEVATED="#FFFFFF",

        # Borders - Elegant gold tints
        BORDER_LIGHT="#E8E4DC",
        BORDER_MEDIUM="#D4CFC4",
        BORDER_FOCUS="#C9A962",
        BORDER_SUBTLE="#F0ECE4",

        # Text - Deep, refined
        TEXT_PRIMARY="#2C2C2C",
        TEXT_SECONDARY="#5C5C5C",
        TEXT_MUTED="#8C8C8C",
        TEXT_WHITE="#FFFFFF",
        TEXT_ON_PRIMARY="#FFFFFF",

        # Status
        SUCCESS="#6B8E6B",
        SUCCESS_LIGHT="#EDF4ED",
        WARNING="#D4A574",
        WARNING_LIGHT="#FDF5ED",
        ERROR="#B85C5C",
        ERROR_LIGHT="#F9EDED",
        INFO="#1E3A5F",
        INFO_LIGHT="#E8EDF4",

        # Design - Luxurious, spacious, refined
        RADIUS_SM=4,
        RADIUS_MD=8,
        RADIUS_LG=12,
        RADIUS_XL=20,

        BORDER_WIDTH=1,

        SHADOW_SM="0 2px 4px rgba(44,44,44,0.04), 0 1px 2px rgba(44,44,44,0.06)",
        SHADOW_MD="0 6px 16px rgba(44,44,44,0.06), 0 3px 8px rgba(44,44,44,0.08)",
        SHADOW_LG="0 12px 32px rgba(44,44,44,0.08), 0 6px 16px rgba(44,44,44,0.1)",
        SHADOW_XL="0 24px 48px rgba(44,44,44,0.1), 0 12px 24px rgba(44,44,44,0.08)",
        SHADOW_GLOW="0 0 40px rgba(201,169,98,0.15)",

        SPACING_RELAXED=1.25,

        USE_GLASS_EFFECT=False,
        USE_GRADIENT_BG=True,
        GRADIENT_START="#FAF9F6",
        GRADIENT_END="#F5F3EE",
        GRADIENT_ANGLE=180,

        CARD_BORDER_STYLE="solid",
        CARD_ELEVATED=True,
        BUTTON_STYLE="gradient",
        INPUT_STYLE="outline",

        FONT_WEIGHT_NORMAL=400,
        FONT_WEIGHT_MEDIUM=500,
    ),
}

# Theme display names for UI
THEME_NAMES = {
    "macos_light": "macOS Light",
    "macos_dark": "macOS Dark",
    "notion": "Notion",
    "vscode": "VS Code",
    "github": "GitHub Dark",
    "luxury": "Luxury Gold",
}

# Default theme
DEFAULT_THEME = "macos_light"


def get_theme(name: str) -> ThemeDesign:
    """Get theme by name, returns default if not found"""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def get_theme_names() -> Dict[str, str]:
    """Get all available theme names"""
    return THEME_NAMES.copy()
