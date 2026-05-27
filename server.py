from core.mcp import mcp

import hal_tools.hal_get_portal_distribution_with_files
import hal_tools.hal_get_publication_stats_by_structure
import hal_tools.hal_search_author_publications
import hal_tools.hal_search_authors
import hal_tools.hal_get_lab_publications

# lancer le serveur 
if __name__ == "__main__":
    mcp.run()
