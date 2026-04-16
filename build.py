#!/usr/bin/env python3
"""
html-ppt build script
Usage: python3 build.py [--slides slides_dir] [--output dist/index.html]
"""
import os
import sys
import yaml
import glob
import argparse
from pathlib import Path

# Try to import Jinja2, fall back to simple template replacement
try:
    from jinja2 import Environment, FileSystemLoader, Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False


def load_yaml(path):
    """Load YAML file safely."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_theme(theme_name, themes_dir):
    """Load a theme file from the themes/ directory."""
    theme_path = os.path.join(themes_dir, f'{theme_name}.yaml')
    if not os.path.exists(theme_path):
        print(f"Warning: Theme '{theme_name}' not found at {theme_path}")
        return {}
    return load_yaml(theme_path)


def render_slide(slide_data, template_name, templates_dir, jinja_env):
    """Render a single slide using the appropriate template."""
    if HAS_JINJA2:
        template = jinja_env.get_template(f"{template_name}.html")
        return template.render(**slide_data)
    else:
        # Fallback: load template as string and do simple replacements
        template_path = os.path.join(templates_dir, f"{template_name}.html")
        if not os.path.exists(template_path):
            return f"<!-- Template {template_name}.html not found -->"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Simple placeholder replacement
        result = template_content
        for key, value in slide_data.items():
            if isinstance(value, str):
                result = result.replace(f"{{{{ {key} }}}}", str(value))
            elif isinstance(value, list):
                # Handle simple list replacement (first occurrence only)
                placeholder = f"{{{{ {key} }}}}"
                if placeholder in result:
                    list_content = ""
                    for item in value:
                        if isinstance(item, dict):
                            # Handle dict items - not supported in simple mode
                            pass
                        else:
                            list_content += str(item)
                    result = result.replace(placeholder, list_content, 1)
        return result


def get_template_name(layout):
    """Map layout type to template name."""
    layout_map = {
        'hero': 'hero',
        'problem': 'problem',
        'pain': 'pain',
        'debut': 'debut',
        'definition': 'definition',
        'model': 'model',
        'spage': 'spage',
        'import': 'import',
        'd1': 'd1',
        'd2': 'd2',
        'tax': 'tax',
        'dq': 'dq',
        'sq': 'sq',
        'y': 'y',
        'change': 'change',
        'local': 'local',
        'summary': 'summary',
        'closing': 'closing',
    }
    return layout_map.get(layout, 'section')


def build_presentation(slides_dir, output_path, theme_name=None):
    """Build the complete HTML presentation.
    
    Args:
        slides_dir: Directory containing slide YAML files
        output_path: Output HTML file path
        theme_name: Optional theme name to override _config.yaml theme
    """
    
    # Load global config
    config_path = os.path.join(slides_dir, '_config.yaml')
    if not os.path.exists(config_path):
        print(f"Error: _config.yaml not found in {slides_dir}")
        return False
    
    config = load_yaml(config_path)

    # Load theme - prefer CLI argument over _config.yaml
    themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'themes')
    if not theme_name:
        theme_name = config.pop('theme', None)  # remove 'theme' key after loading
    if theme_name:
        theme_tokens = load_theme(theme_name, themes_dir)
        # Theme values override _config.yaml for design tokens
        config = {**config, **theme_tokens}
    
    # Map theme tokens to base.html CSS variable names
    # Theme files may use different key names than what base.html expects
    token_mapping = {
        'bg_primary': 'bg_white',
        'bg_secondary': 'bg_fafa',
        'bg_tertiary': 'card_bg',
        'border_color': 'border_light',
        'font_primary': 'font_stack',
    }
    for theme_key, css_key in token_mapping.items():
        if theme_key in config:
            # Only map if theme provides this key and it's different from css_key
            config[css_key] = config.pop(theme_key)
    
    # Set up Jinja2 environment
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    
    if HAS_JINJA2:
        jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=False,
            keep_trailing_newline=True,
            lstrip_blocks=True,
            trim_blocks=True
        )
    else:
        jinja_env = None
    
    # Load base template
    base_template_path = os.path.join(templates_dir, 'base.html')
    with open(base_template_path, 'r', encoding='utf-8') as f:
        base_template = f.read()
    
    # Find and load all slide files
    slide_files = sorted(glob.glob(os.path.join(slides_dir, 's*.yaml')))
    
    if not slide_files:
        print(f"Error: No slide files found in {slides_dir}")
        return False
    
    rendered_slides = []
    
    for idx, slide_file in enumerate(slide_files, start=1):
        slide_data = load_yaml(slide_file)
        layout = slide_data.get('layout', 'section')
        template_name = get_template_name(layout)
        
        # Merge config defaults into slide data (for pixel_dog, etc.)
        slide_ctx = {**config, **slide_data, 'slide_index': idx}
        
        # Render the slide
        slide_html = render_slide(slide_ctx, template_name, templates_dir, jinja_env)
        rendered_slides.append(slide_html)
    
    # Combine slides
    slides_content = '\n'.join(rendered_slides)
    
    # Prepare base template context
    context = {
        'title': config.get('title', 'Presentation'),
        'accent': config.get('accent', '#FF5A5F'),
        'accent_light': config.get('accent_light', 'rgba(255, 90, 95, 0.1)'),
        'text_primary': config.get('text_primary', '#222222'),
        'text_secondary': config.get('text_secondary', '#666666'),
        'bg_white': config.get('bg_white', '#FFFFFF'),
        'bg_fafa': config.get('bg_fafa', '#FAFAFA'),
        'card_bg': config.get('card_bg', '#F8F8F8'),
        'border_light': config.get('border_light', '#EEEEEE'),
        'font_stack': config.get('font_stack', '-apple-system, "SF Pro Display", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif'),
        'nav_dots': config.get('nav_dots', True),
        'pixel_dog': config.get('pixel_dog', True),
        'section_count': len(slide_files),
        'content': slides_content,
    }
    
    # Render final HTML
    if HAS_JINJA2:
        from jinja2 import Template
        template = Template(base_template)
        final_html = template.render(**context)
    else:
        # Simple string replacement for base template
        final_html = base_template
        for key, value in context.items():
            if isinstance(value, str):
                final_html = final_html.replace(f"{{{{ {key} }}}}", value)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"✓ Built presentation: {output_path}")
    print(f"  - {len(slide_files)} slides")
    print(f"  - Using {'Jinja2' if HAS_JINJA2 else 'basic template replacement'}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Build HTML presentation from YAML slides')
    parser.add_argument('--slides', default=None, help='Directory containing slide YAML files (relative to skill dir)')
    parser.add_argument('--output', default=None, help='Output HTML file path')
    parser.add_argument('--theme', default=None, help='Theme name to use (overrides _config.yaml theme)')
    
    args = parser.parse_args()
    
    # Resolve paths relative to skill root (parent of scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)  # scripts/ -> skill root
    
    # Default paths relative to skill directory
    slides_dir = args.slides if args.slides else 'slides'
    if not os.path.isabs(slides_dir):
        slides_dir = os.path.join(skill_dir, slides_dir)
    
    output_path = args.output if args.output else 'dist/index.html'
    if not os.path.isabs(output_path):
        output_path = os.path.join(skill_dir, output_path)
    
    success = build_presentation(slides_dir, output_path, theme_name=args.theme)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
