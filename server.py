from core.mcp import mcp

import hal_tools.get_anr_publications
import hal_tools.get_author_affiliations
import hal_tools.hal_get_lab_publications
import hal_tools.hal_get_publication_stats_by_structure
import hal_tools.hal_search_author_publications
import hal_tools.search_authors
import hal_tools.search_structure

app = mcp.streamable_http_app()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")