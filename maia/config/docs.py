"""
Configuration for docs
"""

from frappe import _

source_link = "https://github.com/DOKOS-IO/maia"
docs_base_url = "https://dokos-io.github.io/maia"
headline = _("Discover Maia")
sub_heading = _("The Midwife's activity management application")

def get_context(context):
	context.brand_html = "Maia"
        context.favicon = 'https://DOKOS-IO.github.io/maia/public/favicon.png'
