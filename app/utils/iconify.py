"""Iconify integration utilities for icon and color management."""

import re
from typing import Dict, List, Optional, Tuple

# Predefined color mappings for popular technologies (hex values)
TECHNOLOGY_COLORS = {
    # Frontend Technologies
    "javascript": "#f7df1e",
    "typescript": "#3178c6",
    "react": "#61dafb",
    "vue": "#4fc08d",
    "angular": "#dd0031",
    "nextjs": "#000000",
    "svelte": "#ff3e00",
    "tailwindcss": "#06b6d4",
    "bootstrap": "#7952b3",
    # Backend Technologies
    "python": "#3776ab",
    "fastapi": "#009688",
    "django": "#092e20",
    "flask": "#000000",
    "nodejs": "#339933",
    "express": "#000000",
    "php": "#777bb4",
    "laravel": "#ff2d20",
    "ruby": "#cc342d",
    "rails": "#cc0000",
    "java": "#ed8b00",
    "spring": "#6db33f",
    "csharp": "#239120",
    "dotnet": "#512bd4",
    "go": "#00add8",
    "rust": "#000000",
    # Databases
    "mysql": "#4479a1",
    "postgresql": "#336791",
    "mongodb": "#47a248",
    "redis": "#dc382d",
    "sqlite": "#003b57",
    "mariadb": "#003545",
    # DevOps & Tools
    "docker": "#2496ed",
    "kubernetes": "#326ce5",
    "git": "#f05032",
    "github": "#181717",
    "gitlab": "#fc6d26",
    "jenkins": "#d33833",
    "terraform": "#623ce4",
    "ansible": "#ee0000",
    "aws": "#ff9900",
    "azure": "#0078d4",
    "gcp": "#4285f4",
    # Operating Systems
    "linux": "#fcc624",
    "ubuntu": "#e95420",
    "debian": "#a81d33",
    "archlinux": "#1793d1",
    "centos": "#262577",
    "windows": "#0078d6",
    "macos": "#000000",
    # Design & Productivity
    "figma": "#f24e1e",
    "adobe": "#ff0000",
    "photoshop": "#31a8ff",
    "illustrator": "#ff9a00",
    "sketch": "#f7b500",
    "canva": "#00c4cc",
    "notion": "#000000",
    "obsidian": "#7c3aed",
    "vscode": "#007acc",
    "vim": "#019733",
    "neovim": "#57a143",
    # Social & Communication
    "linkedin": "#0a66c2",
    "twitter": "#1da1f2",
    "instagram": "#e4405f",
    "facebook": "#1877f2",
    "youtube": "#ff0000",
    "discord": "#5865f2",
    "slack": "#4a154b",
    "telegram": "#26a5e4",
    "whatsapp": "#25d366",
    # Development Tools
    "postman": "#ff6c37",
    "insomnia": "#4000bf",
    "swagger": "#85ea2d",
    "npm": "#cb3837",
    "yarn": "#2c8ebb",
    "webpack": "#8dd6f9",
    "vite": "#646cff",
    "rollup": "#ec4a3f",
    "babel": "#f9dc3e",
    "eslint": "#4b32c3",
    "prettier": "#f7b93e",
}

# Common fallback icons for different contexts
FALLBACK_ICONS = {
    "skill": "code",
    "technology": "code",
    "tool": "settings",
    "social": "link",
    "contact": "mail",
    "project": "folder",
    "education": "graduation-cap",
    "experience": "briefcase",
    "default": "circle",
}

# Popular icon names and their variations
ICON_VARIATIONS = {
    "javascript": ["js", "javascript", "nodejs"],
    "typescript": ["ts", "typescript"],
    "python": ["python", "py"],
    "react": ["react", "reactjs"],
    "vue": ["vue", "vuejs"],
    "angular": ["angular", "angularjs"],
    "docker": ["docker", "container"],
    "github": ["github", "git"],
    "linkedin": ["linkedin", "linkedin-in"],
    "archlinux": ["arch", "archlinux", "arch-linux"],
    "obsidian": ["obsidian", "obsidianmd"],
    "vscode": ["vscode", "visual-studio-code", "code"],
}


def normalize_icon_name(icon_name: str) -> str:
    """
    Normalize icon name by converting to lowercase and replacing separators.

    Args:
        icon_name: Raw icon name

    Returns:
        Normalized icon name
    """
    if not icon_name:
        return ""

    # Convert to lowercase and replace separators
    normalized = re.sub(r"[_\s-]+", "", icon_name.lower())

    # Check for variations
    for canonical, variations in ICON_VARIATIONS.items():
        if normalized in [
            v.lower().replace("-", "").replace("_", "") for v in variations
        ]:
            return canonical

    return normalized


def validate_hex_color(color: str) -> bool:
    """
    Validate if a color is a valid hex color.

    Args:
        color: Color string to validate

    Returns:
        True if valid hex color, False otherwise
    """
    if not color:
        return False

    # Remove # if present
    color = color.lstrip("#")

    # Check if it's a valid hex color (3 or 6 characters)
    return bool(re.match(r"^[0-9a-fA-F]{3}$|^[0-9a-fA-F]{6}$", color))


def format_hex_color(color: str) -> str:
    """
    Format color to proper hex format with # prefix.

    Args:
        color: Color string

    Returns:
        Formatted hex color string
    """
    if not color:
        return ""

    # Remove existing # if present
    color = color.lstrip("#")

    # Validate hex format
    if not validate_hex_color(f"#{color}"):
        return ""

    return f"#{color.upper()}"


def get_suggested_color(icon_name: str) -> Optional[str]:
    """
    Get suggested color for an icon based on technology mappings.

    Args:
        icon_name: Icon name to get color suggestion for

    Returns:
        Suggested hex color or None if no suggestion available
    """
    normalized_name = normalize_icon_name(icon_name)
    return TECHNOLOGY_COLORS.get(normalized_name)


def get_icon_tooltip_info(
    icon_name: str, color: Optional[str] = None, context: str = "default"
) -> Dict:
    """
    Get comprehensive tooltip information for an icon.

    Args:
        icon_name: Icon name
        color: Optional color value
        context: Context for fallback icon selection

    Returns:
        Dictionary with tooltip information
    """
    normalized_icon = normalize_icon_name(icon_name) if icon_name else ""
    suggested_color = get_suggested_color(normalized_icon) if normalized_icon else None
    fallback_icon = FALLBACK_ICONS.get(context, FALLBACK_ICONS["default"])

    # Validate provided color
    formatted_color = format_hex_color(color) if color else None
    is_valid_color = bool(formatted_color) if color else True

    tooltip_info = {
        "original_name": icon_name,
        "normalized_name": normalized_icon,
        "suggested_color": suggested_color,
        "provided_color": formatted_color,
        "is_valid_color": is_valid_color,
        "fallback_icon": fallback_icon,
        "has_color_suggestion": bool(suggested_color),
        "recommendations": [],
    }

    # Add recommendations
    if not normalized_icon:
        tooltip_info["recommendations"].append(
            f"Consider using '{fallback_icon}' as a fallback icon"
        )

    if suggested_color and not formatted_color:
        tooltip_info["recommendations"].append(f"Suggested color: {suggested_color}")

    if color and not is_valid_color:
        tooltip_info["recommendations"].append(
            "Invalid color format. Use hex format like #FF0000"
        )

    if normalized_icon and normalized_icon in TECHNOLOGY_COLORS:
        tooltip_info["recommendations"].append(
            f"Popular technology icon detected. Recommended color: {TECHNOLOGY_COLORS[normalized_icon]}"
        )

    return tooltip_info


def get_popular_icons_by_category() -> Dict[str, List[Dict[str, str]]]:
    """
    Get popular icons organized by categories.

    Returns:
        Dictionary of categories with icon lists
    """
    categories = {
        "Frontend Technologies": [
            {"name": "javascript", "color": TECHNOLOGY_COLORS["javascript"]},
            {"name": "typescript", "color": TECHNOLOGY_COLORS["typescript"]},
            {"name": "react", "color": TECHNOLOGY_COLORS["react"]},
            {"name": "vue", "color": TECHNOLOGY_COLORS["vue"]},
            {"name": "angular", "color": TECHNOLOGY_COLORS["angular"]},
            {"name": "nextjs", "color": TECHNOLOGY_COLORS["nextjs"]},
        ],
        "Backend Technologies": [
            {"name": "python", "color": TECHNOLOGY_COLORS["python"]},
            {"name": "nodejs", "color": TECHNOLOGY_COLORS["nodejs"]},
            {"name": "fastapi", "color": TECHNOLOGY_COLORS["fastapi"]},
            {"name": "django", "color": TECHNOLOGY_COLORS["django"]},
            {"name": "php", "color": TECHNOLOGY_COLORS["php"]},
            {"name": "java", "color": TECHNOLOGY_COLORS["java"]},
        ],
        "Databases": [
            {"name": "mysql", "color": TECHNOLOGY_COLORS["mysql"]},
            {"name": "postgresql", "color": TECHNOLOGY_COLORS["postgresql"]},
            {"name": "mongodb", "color": TECHNOLOGY_COLORS["mongodb"]},
            {"name": "redis", "color": TECHNOLOGY_COLORS["redis"]},
        ],
        "DevOps & Tools": [
            {"name": "docker", "color": TECHNOLOGY_COLORS["docker"]},
            {"name": "kubernetes", "color": TECHNOLOGY_COLORS["kubernetes"]},
            {"name": "git", "color": TECHNOLOGY_COLORS["git"]},
            {"name": "github", "color": TECHNOLOGY_COLORS["github"]},
        ],
        "Design & Productivity": [
            {"name": "figma", "color": TECHNOLOGY_COLORS["figma"]},
            {"name": "vscode", "color": TECHNOLOGY_COLORS["vscode"]},
            {"name": "notion", "color": TECHNOLOGY_COLORS["notion"]},
            {"name": "obsidian", "color": TECHNOLOGY_COLORS["obsidian"]},
        ],
        "UI Icons": [
            {"name": "code", "color": "#64748b"},
            {"name": "database", "color": "#475569"},
            {"name": "server", "color": "#374151"},
            {"name": "smartphone", "color": "#6b7280"},
            {"name": "briefcase", "color": "#4b5563"},
            {"name": "graduation-cap", "color": "#374151"},
        ],
    }

    return categories


def search_icons(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Search for icons matching a query.

    Args:
        query: Search query
        limit: Maximum number of results

    Returns:
        List of matching icons with colors
    """
    query_lower = query.lower()
    matches = []

    for icon_name, color in TECHNOLOGY_COLORS.items():
        if query_lower in icon_name.lower():
            matches.append({"name": icon_name, "color": color})
            if len(matches) >= limit:
                break

    # Add UI icons if not enough technology matches
    ui_icons = [
        "code",
        "database",
        "server",
        "settings",
        "smartphone",
        "briefcase",
        "graduation-cap",
    ]
    for ui_icon in ui_icons:
        if len(matches) >= limit:
            break
        if query_lower in ui_icon and not any(m["name"] == ui_icon for m in matches):
            matches.append({"name": ui_icon, "color": "#64748b"})

    return matches[:limit]
