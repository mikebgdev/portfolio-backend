"""Custom fields for Iconify icons and colors with validation and suggestions."""

import json

from wtforms import StringField
from wtforms.widgets import TextInput

from app.utils.iconify import (
    get_icon_tooltip_info,
    normalize_icon_name,
    validate_hex_color,
)


class IconifyWidget(TextInput):
    """Custom widget for icon field with suggestions and validation."""

    def __call__(self, field, **kwargs):
        # Add custom CSS classes and data attributes
        kwargs.setdefault("class", "form-control iconify-field")
        kwargs.setdefault("data-field-type", "icon")

        # Get tooltip info if field has value
        if field.data:
            tooltip_info = get_icon_tooltip_info(field.data, context="skill")
            kwargs.setdefault("data-tooltip-info", json.dumps(tooltip_info))

            if tooltip_info.get("suggested_color"):
                kwargs.setdefault(
                    "data-suggested-color", tooltip_info["suggested_color"]
                )

        # Add autocomplete suggestions
        popular_icons = [
            "python",
            "javascript",
            "typescript",
            "react",
            "vue",
            "angular",
            "docker",
            "kubernetes",
            "nodejs",
            "code",
            "database",
            "server",
        ]
        kwargs.setdefault("data-suggestions", json.dumps(popular_icons))

        # Add the tooltip content
        tooltip_text = self._generate_tooltip_text()
        kwargs.setdefault("title", tooltip_text)

        return super().__call__(field, **kwargs)

    def _generate_tooltip_text(self) -> str:
        """Generate comprehensive tooltip text for icons."""
        return """🔧 TECNOLOGÍAS POPULARES:
• Frontend: javascript, typescript, react, vue, angular, svelte
• Backend: python, nodejs, php, java, csharp, go, rust
• DevOps: docker, kubernetes, git, jenkins
• Databases: mysql, postgresql, mongodb, redis
• Tools: vscode, figma, notion, obsidian

💻 ICONOS UI COMUNES:
code, database, server, settings, briefcase, graduation-cap, mail, phone

🔍 BÚSQUEDA: Usa /api/v1/iconify/search?q=nombre para buscar
📚 CATEGORÍAS: /api/v1/iconify/categories para ver todas las opciones

ℹ️ Los nombres se normalizan automáticamente (arch-linux → archlinux)"""


class ColorWidget(TextInput):
    """Custom widget for color field with validation and suggestions."""

    def __call__(self, field, **kwargs):
        # Add custom CSS classes and data attributes
        kwargs.setdefault("class", "form-control color-field")
        kwargs.setdefault("data-field-type", "color")

        # Validate color if field has value
        if field.data:
            is_valid = True
            formatted_color = field.data

            if field.data.startswith("#"):
                is_valid = validate_hex_color(field.data)
                if is_valid:
                    formatted_color = field.data.upper()

            kwargs.setdefault("data-is-valid", str(is_valid).lower())
            kwargs.setdefault("data-formatted-color", formatted_color)

        # Add color picker attributes
        if field.data and field.data.startswith("#") and validate_hex_color(field.data):
            kwargs.setdefault("data-color-preview", field.data)

        # Add the tooltip content
        tooltip_text = self._generate_tooltip_text()
        kwargs.setdefault("title", tooltip_text)

        return super().__call__(field, **kwargs)

    def _generate_tooltip_text(self) -> str:
        """Generate comprehensive tooltip text for colors."""
        return """🎨 FORMATOS DE COLOR VÁLIDOS:

🔹 HEX COLORS (Recomendado):
• #FF0000 o #F00 (rojo)
• #61dafb (React blue)
• #f7df1e (JavaScript yellow)
• #3776ab (Python blue)

🔹 TAILWIND CSS:
• text-blue-500, text-red-600
• text-green-500, text-yellow-400

🔹 CSS COLOR NAMES:
• red, blue, green, orange

🌟 COLORES DE TECNOLOGÍAS POPULARES:
JavaScript: #f7df1e | TypeScript: #3178c6 | Python: #3776ab
React: #61dafb | Vue: #4fc08d | Angular: #dd0031
Docker: #2496ed | Node.js: #339933 | PHP: #777bb4

💡 HERRAMIENTAS:
• Sugerencia: /api/v1/iconify/suggest-color?icon_name=python
• Validar: /api/v1/iconify/validate-color?color=%23ff0000"""


class IconifyField(StringField):
    """Custom field for Iconify icons with enhanced validation and suggestions."""

    widget = IconifyWidget()

    def __init__(self, label=None, validators=None, **kwargs):
        # Add helpful placeholder and description
        kwargs.setdefault("render_kw", {})
        kwargs["render_kw"].setdefault("placeholder", "Ej: python, react, docker, code")
        kwargs.setdefault(
            "description",
            "Nombre del icono de Iconify. Ejemplos: python, javascript, "
            "react, docker, code, settings",
        )

        super().__init__(label, validators, **kwargs)

    def process_data(self, value):
        """Normalize icon name when processing data."""
        if value:
            # Normalize the icon name
            normalized = normalize_icon_name(value)
            self.data = normalized if normalized else value
        else:
            self.data = value


class ColorField(StringField):
    """Custom field for colors with enhanced validation and preview."""

    widget = ColorWidget()

    def __init__(self, label=None, validators=None, **kwargs):
        # Add helpful placeholder and description
        kwargs.setdefault("render_kw", {})
        kwargs["render_kw"].setdefault(
            "placeholder", "Ej: #61dafb, #f7df1e, text-blue-500"
        )
        kwargs.setdefault(
            "description",
            "Color en formato hex (#FF0000), clase Tailwind "
            "(text-blue-500), o nombre CSS (red)",
        )

        super().__init__(label, validators, **kwargs)

    def process_data(self, value):
        """Format color when processing data."""
        if value and value.startswith("#"):
            # Normalize hex color to uppercase
            if validate_hex_color(value):
                self.data = value.upper()
            else:
                self.data = value
        else:
            self.data = value


class SmartIconColorFieldSet:
    """Utility class to create related icon and color fields with smart suggestions."""

    @staticmethod
    def create_fields(icon_field_name="icon_name", color_field_name="color"):
        """Create related icon and color fields with smart integration."""

        # Enhanced icon field with color suggestions
        icon_field = IconifyField(
            label="Icono",
            description="Nombre del icono. Al elegir una tecnología popular, "
            "se sugerirá automáticamente el color oficial.",
            render_kw={
                "placeholder": "Ej: python, react, docker, javascript",
                "data-field-type": "icon",
                "data-related-color-field": color_field_name,
                "class": "form-control iconify-icon-field",
            },
        )

        # Enhanced color field with icon integration
        color_field = ColorField(
            label="Color",
            description="Color del icono. Se sugiere automáticamente para "
            "tecnologías populares.",
            render_kw={
                "placeholder": "Ej: #61dafb, text-blue-500, red",
                "data-field-type": "color",
                "data-related-icon-field": icon_field_name,
                "class": "form-control iconify-color-field",
            },
        )

        return icon_field, color_field


# JavaScript helper functions to inject into admin templates
ICONIFY_ADMIN_JS = """
<script>
// Iconify admin field helpers
class IconifyAdminHelper {
    constructor() {
        this.initIconFields();
        this.initColorFields();
        this.setupFieldRelationships();
    }

    initIconFields() {
        document.querySelectorAll('.iconify-icon-field').forEach(field => {
            // Add change event listener
            field.addEventListener('change', async (e) => {
                const iconName = e.target.value;
                if (iconName) {
                    await this.updateIconSuggestions(field, iconName);
                }
            });

            // Add suggestions dropdown
            this.addIconSuggestions(field);
        });
    }

    initColorFields() {
        document.querySelectorAll('.iconify-color-field').forEach(field => {
            // Add real-time validation
            field.addEventListener('input', (e) => {
                this.validateColor(field, e.target.value);
            });

            // Add color preview
            this.addColorPreview(field);
        });
    }

    async updateIconSuggestions(iconField, iconName) {
        try {
            // Get tooltip info
            const response = await fetch(
                `/api/v1/iconify/tooltip?icon_name=${iconName}&context=skill`
            );
            const data = await response.json();

            // Update related color field if suggested color exists
            const colorFieldName = iconField.dataset.relatedColorField;
            if (colorFieldName && data.suggested_color) {
                const colorField = document.querySelector(`[name="${colorFieldName}"]`);
                if (colorField && !colorField.value) {
                    colorField.value = data.suggested_color;
                    this.validateColor(colorField, data.suggested_color);
                }
            }

            // Show recommendations in tooltip
            if (data.recommendations?.length > 0) {
                iconField.title = `✅ ${data.recommendations.join('\\n')}`;
            }

        } catch (error) {
            console.warn('Error fetching icon suggestions:', error);
        }
    }

    validateColor(colorField, colorValue) {
        if (!colorValue) {
            colorField.classList.remove('is-valid', 'is-invalid');
            return;
        }

        // Simple hex validation
        const isHex = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/.test(colorValue);
        const isTailwind = /^text-\\w+(-\\d+)?$/.test(colorValue);
        const isCssColor = /^[a-z]+$/i.test(colorValue);

        if (isHex || isTailwind || isCssColor) {
            colorField.classList.remove('is-invalid');
            colorField.classList.add('is-valid');
        } else {
            colorField.classList.remove('is-valid');
            colorField.classList.add('is-invalid');
        }

        // Update color preview
        this.updateColorPreview(colorField, colorValue);
    }

    addColorPreview(colorField) {
        const preview = document.createElement('div');
        preview.className = 'color-preview';
        preview.style.cssText = `
            width: 20px; height: 20px; border: 1px solid #ccc;
            display: inline-block; margin-left: 8px; border-radius: 3px;
            vertical-align: middle;
        `;
        colorField.parentNode.appendChild(preview);

        // Initial preview
        if (colorField.value) {
            this.updateColorPreview(colorField, colorField.value);
        }
    }

    updateColorPreview(colorField, colorValue) {
        const preview = colorField.parentNode.querySelector('.color-preview');
        if (preview && colorValue.startsWith('#')) {
            preview.style.backgroundColor = colorValue;
        }
    }

    addIconSuggestions(iconField) {
        // This would add a suggestions dropdown, but for now we rely on browser autocomplete
        iconField.setAttribute('list', 'icon-suggestions');

        // Create datalist if it doesn't exist
        let datalist = document.getElementById('icon-suggestions');
        if (!datalist) {
            datalist = document.createElement('datalist');
            datalist.id = 'icon-suggestions';

            const suggestions = [
                'python', 'javascript', 'typescript', 'react', 'vue', 'angular',
                'docker', 'kubernetes', 'nodejs', 'code', 'database', 'server',
                'figma', 'vscode', 'notion', 'obsidian', 'github', 'gitlab'
            ];

            suggestions.forEach(suggestion => {
                const option = document.createElement('option');
                option.value = suggestion;
                datalist.appendChild(option);
            });

            document.body.appendChild(datalist);
        }
    }

    setupFieldRelationships() {
        // Additional setup for related fields can go here
        console.log('Iconify admin helper initialized');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new IconifyAdminHelper();
});
</script>

<style>
.iconify-field, .color-field {
    position: relative;
}

.is-valid {
    border-color: #28a745 !important;
}

.is-invalid {
    border-color: #dc3545 !important;
}

.color-preview {
    transition: background-color 0.2s ease;
}

.field-help-text {
    font-size: 0.875rem;
    color: #6c757d;
    margin-top: 0.25rem;
}
</style>
"""
