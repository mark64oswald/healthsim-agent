"""
Tests for HealthSim Agent UI Theme Module.
"""

import pytest
from rich.theme import Theme

from healthsim_agent.ui.theme import (
    COLORS,
    ICONS,
    HEALTHSIM_THEME,
    BANNER_ART,
    SPINNER_FRAMES,
    get_status_style,
    get_icon,
)


class TestColors:
    """Tests for color palette."""
    
    def test_all_colors_are_hex(self):
        """All colors should be valid hex color codes."""
        for name, color in COLORS.items():
            assert color.startswith("#"), f"{name} should start with #"
            assert len(color) == 7, f"{name} should be 7 chars (#RRGGBB)"
    
    def test_required_colors_exist(self):
        """Required semantic colors should exist."""
        required = ["success", "error", "warning", "text", "muted", "command"]
        for color in required:
            assert color in COLORS, f"Missing required color: {color}"
    
    def test_background_colors_exist(self):
        """Background colors for terminal should exist."""
        assert "background" in COLORS
        assert "surface" in COLORS
        assert "border" in COLORS


class TestIcons:
    """Tests for status icons."""
    
    def test_all_icons_are_single_char(self):
        """Icons should be single characters or short strings."""
        for name, icon in ICONS.items():
            assert len(icon) <= 2, f"{name} icon too long"
    
    def test_required_icons_exist(self):
        """Required status icons should exist."""
        required = ["success", "error", "warning", "arrow", "bullet"]
        for icon in required:
            assert icon in ICONS, f"Missing required icon: {icon}"
    
    def test_success_is_checkmark(self):
        """Success icon should be a checkmark."""
        assert ICONS["success"] == "✓"
    
    def test_error_is_x(self):
        """Error icon should be an X."""
        assert ICONS["error"] == "✗"


class TestTheme:
    """Tests for Rich theme."""
    
    def test_theme_is_rich_theme(self):
        """HEALTHSIM_THEME should be a Rich Theme instance."""
        assert isinstance(HEALTHSIM_THEME, Theme)
    
    def test_theme_has_status_styles(self):
        """Theme should have styles for status types."""
        styles = HEALTHSIM_THEME.styles
        assert "success" in styles
        assert "error" in styles
        assert "warning" in styles
        assert "muted" in styles


class TestBannerArt:
    """Tests for ASCII banner."""
    
    def test_banner_art_exists(self):
        """Banner art should be a non-empty string."""
        assert isinstance(BANNER_ART, str)
        assert len(BANNER_ART) > 0
    
    def test_banner_contains_healthsim(self):
        """Banner should visually represent HEALTHSIM."""
        # The ASCII art should spell out the name
        assert "█" in BANNER_ART  # Uses block characters


class TestSpinnerFrames:
    """Tests for spinner animation."""
    
    def test_spinner_frames_is_list(self):
        """Spinner frames should be a list."""
        assert isinstance(SPINNER_FRAMES, list)
    
    def test_spinner_has_multiple_frames(self):
        """Should have multiple frames for animation."""
        assert len(SPINNER_FRAMES) >= 4
    
    def test_spinner_frames_are_braille(self):
        """Frames should use braille characters."""
        for frame in SPINNER_FRAMES:
            assert len(frame) == 1
            # Braille dots pattern characters
            assert ord(frame) >= 0x2800


class TestGetStatusStyle:
    """Tests for get_status_style helper."""
    
    def test_success_style(self):
        """Success status should return green bold style."""
        style = get_status_style("success")
        assert "bold" in style
        assert COLORS["success"] in style
    
    def test_error_style(self):
        """Error status should return red bold style."""
        style = get_status_style("error")
        assert "bold" in style
        assert COLORS["error"] in style
    
    def test_unknown_status_returns_text(self):
        """Unknown status should return default text color."""
        style = get_status_style("unknown")
        assert style == COLORS["text"]


class TestGetIcon:
    """Tests for get_icon helper."""
    
    def test_known_icon(self):
        """Known icon type should return correct icon."""
        assert get_icon("success") == "✓"
        assert get_icon("error") == "✗"
        assert get_icon("arrow") == "→"
    
    def test_unknown_icon_returns_empty(self):
        """Unknown icon type should return empty string."""
        assert get_icon("unknown") == ""
