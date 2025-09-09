"""Enhanced skills field for admin panel with search functionality."""

from typing import Any

from wtforms import SelectMultipleField
from wtforms.widgets import Select

from app.database import SessionLocal
from app.models.skills import Skill, SkillCategory


class EnhancedSkillsWidget(Select):
    """Enhanced widget for skills selection with search."""

    def __init__(self, multiple=True):
        super().__init__(multiple=multiple)

    def __call__(self, field, **kwargs):
        """Render the skills selector with search functionality."""
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("multiple", True)
        kwargs.setdefault("size", "12")
        kwargs.setdefault("class", "form-control")

        # Get field choices and current values
        choices = getattr(field, "choices", [])
        current_data = field.data or []

        # Build options HTML
        options_html = []
        for value, label in choices:
            is_selected = str(value) in [str(v) for v in current_data]
            is_disabled = value == ""  # Category headers

            if is_disabled:
                if "──────" in label:
                    options_html.append(
                        f'<option disabled style="background: #f8f9fa; color: #6c757d; font-size: 11px;">{label}</option>'
                    )
                elif "📁" in label:
                    options_html.append(
                        f'<option disabled style="background: #e7f3ff; font-weight: bold; color: #0066cc; padding: 2px;">{label}</option>'
                    )
            else:
                selected_attr = " selected" if is_selected else ""
                style = 'style="padding-left: 20px;"'
                options_html.append(
                    f'<option value="{value}"{selected_attr} {style}>{label}</option>'
                )

        # Main HTML structure
        html = f"""
        <div class="enhanced-skills-selector" style="border: 1px solid #ced4da; border-radius: 4px; padding: 10px; background: #f8f9fa;">
            <!-- Search input -->
            <div class="mb-2">
                <input type="text" 
                       class="form-control form-control-sm" 
                       id="{field.id}_search" 
                       placeholder="🔍 Buscar skills... (ej: React, Python, Docker)"
                       style="border: 1px solid #007bff;">
                <small class="text-muted mt-1 d-block">
                    💡 Escribe para filtrar • Ctrl+Click para múltiple selección • 
                    <span id="{field.id}_counter">0 seleccionados</span>
                </small>
            </div>
            
            <!-- The select field -->
            <select name="{field.name}" id="{field.id}" multiple size="12" class="form-control" 
                    style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto; font-size: 13px;">
                {"".join(options_html)}
            </select>
            
            <!-- Action buttons -->
            <div class="mt-2">
                <button type="button" class="btn btn-sm btn-outline-primary" id="{field.id}_select_visible">
                    ✓ Seleccionar visibles
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary" id="{field.id}_clear">
                    ✗ Limpiar
                </button>
                <button type="button" class="btn btn-sm btn-outline-info" id="{field.id}_toggle_inactive">
                    👁️ Mostrar inactivos
                </button>
            </div>
        </div>
        
        <script type="text/javascript">
        (function() {{
            const selectEl = document.getElementById('{field.id}');
            const searchEl = document.getElementById('{field.id}_search');
            const counterEl = document.getElementById('{field.id}_counter');
            const selectVisibleBtn = document.getElementById('{field.id}_select_visible');
            const clearBtn = document.getElementById('{field.id}_clear');
            const toggleBtn = document.getElementById('{field.id}_toggle_inactive');
            
            let showInactive = true;
            
            function updateCounter() {{
                const count = Array.from(selectEl.selectedOptions).filter(opt => opt.value !== '').length;
                counterEl.textContent = count + ' seleccionados';
            }}
            
            function filterSkills() {{
                const searchTerm = searchEl.value.toLowerCase();
                let visibleCount = 0;
                
                Array.from(selectEl.options).forEach(option => {{
                    const isHeader = option.disabled;
                    const text = option.textContent.toLowerCase();
                    const isInactive = text.includes('❌');
                    const hasSearchMatch = !searchTerm || text.includes(searchTerm);
                    
                    let show = true;
                    
                    if (isHeader) {{
                        // Always show headers for structure
                        show = true;
                    }} else {{
                        // Filter by search term
                        if (!hasSearchMatch) show = false;
                        // Filter by active status
                        if (!showInactive && isInactive) show = false;
                        
                        if (show) visibleCount++;
                    }}
                    
                    option.style.display = show ? '' : 'none';
                }});
                
                updateCounter();
            }}
            
            // Event listeners
            searchEl.addEventListener('input', filterSkills);
            selectEl.addEventListener('change', updateCounter);
            
            selectVisibleBtn.addEventListener('click', function() {{
                Array.from(selectEl.options).forEach(option => {{
                    if (option.style.display !== 'none' && option.value !== '') {{
                        option.selected = true;
                    }}
                }});
                updateCounter();
            }});
            
            clearBtn.addEventListener('click', function() {{
                Array.from(selectEl.selectedOptions).forEach(option => {{
                    option.selected = false;
                }});
                updateCounter();
            }});
            
            toggleBtn.addEventListener('click', function() {{
                showInactive = !showInactive;
                toggleBtn.innerHTML = showInactive ? '👁️ Ocultar inactivos' : '👁️ Mostrar inactivos';
                toggleBtn.className = showInactive ? 'btn btn-sm btn-outline-info' : 'btn btn-sm btn-secondary';
                filterSkills();
            }});
            
            // Initialize
            updateCounter();
            
            // Enhance search UX
            searchEl.addEventListener('focus', function() {{
                this.style.borderColor = '#007bff';
                this.style.boxShadow = '0 0 0 0.2rem rgba(0,123,255,.25)';
            }});
            
            searchEl.addEventListener('blur', function() {{
                this.style.borderColor = '#ced4da';
                this.style.boxShadow = 'none';
            }});
        }})();
        </script>
        """

        from markupsafe import Markup

        return Markup(html)


class EnhancedSkillsField(SelectMultipleField):
    """Enhanced field for skills selection with search and filtering."""

    widget = EnhancedSkillsWidget()

    def __init__(self, label=None, validators=None, **kwargs):
        # Clean kwargs - remove SQLAdmin specific parameters
        clean_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["allow_blank", "blank_text", "query_factory", "get_label"]:
                clean_kwargs[key] = value

        super().__init__(label, validators, coerce=str, **clean_kwargs)
        self.choices = self._load_skills_choices()

    def _load_skills_choices(self):
        """Load all skills organized by categories."""
        db = SessionLocal()
        try:
            # Get skills with categories, ordered properly
            skills = (
                db.query(Skill)
                .join(SkillCategory, Skill.category_id == SkillCategory.id)
                .order_by(
                    SkillCategory.display_order.asc(),
                    SkillCategory.label_en.asc(),
                    Skill.display_order.asc(),
                    Skill.name_en.asc(),
                )
                .all()
            )

            choices = []
            current_category = None

            for skill in skills:
                category_name = (
                    skill.skill_category.label_en
                    if skill.skill_category
                    else "Sin categoría"
                )

                # Add category header when category changes
                if current_category != category_name:
                    current_category = category_name
                    if choices:  # Add separator between categories
                        choices.append(("", "──────────────"))
                    # Add category header
                    choices.append(("", f"📁 {category_name}"))

                # Add the skill option
                status_icon = "✅" if skill.active else "❌"
                skill_name = skill.name_en
                if skill.name_es and skill.name_es != skill.name_en:
                    skill_name += f" / {skill.name_es}"

                skill_label = f"{status_icon} {skill_name}"
                choices.append((str(skill.id), skill_label))

            return choices

        except Exception as e:
            # Fallback in case of error
            print(f"Error loading skills: {e}")
            return [("", "Error cargando skills")]
        finally:
            db.close()

    def process_formdata(self, valuelist):
        """Process form data, filtering out category headers."""
        if valuelist:
            # Filter out empty values (category headers and separators)
            self.data = [v for v in valuelist if v and v.strip()]
        else:
            self.data = []

    def pre_validate(self, form):
        """Skip validation for category headers."""
        if self.data:
            valid_choices = {choice[0] for choice in self.choices if choice[0]}
            for value in self.data:
                if value not in valid_choices:
                    self.data.remove(value)
