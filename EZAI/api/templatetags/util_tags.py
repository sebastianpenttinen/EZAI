from django import template
from markdownx.utils import markdownify

register = template.Library()

# Template tag to render markdown correctly 
@register.filter
def show_markdown(text): 
  return markdownify(text)