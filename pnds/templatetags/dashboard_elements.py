from django import template

register = template.Library()

@register.inclusion_tag("pnds/dashboard-snippets/scorecard.html")
def scorecard(heading, value, id = None, grid = 'c'):
    
    grid = 'col' if grid == 'c' else 'row' if grid == 'r' else None
    return {'heading': heading, 'value': value, 'id': id, 'grid': grid}
