
import os
import sys
# sys.path.append('/mnt/utility/lca_sgtk_apps/tk-lca-version-cache/python/tk_lca_version_cache')
# sys.path.append('U:/lca_sgtk_apps/tk-lca-version-cache/python/tk_lca_version_cache')

import traceback
import tk_lca_version_cache.cache_cmd as cache_cmd
reload(cache_cmd)

proj = sys.argv[1]
version_name = sys.argv[2]
asset_name = sys.argv[3]
cache_path = sys.argv[4]

if not cache_path.endswith('/'):
    cache_path = cache_path + '/'

job = cache_cmd.create_job(proj, version_name, asset_name, cache_path)
if isinstance(job, type({})):
    cache_cmd.submit_jobs( [job] )