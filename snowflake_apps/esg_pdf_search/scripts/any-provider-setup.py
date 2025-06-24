-- Any script that should be run as the provider, such as creating and populating database objects that need to be shared with the application package.
-- This script must be idempotent.

import snowflake.permissions as permissions
session = get_active_session()


def get_ref(ref_name: str) -> str:
    if local_dev:
        docs_stage_ref = {
            "database": "CC_QUICKSTART_CORTEX_SEARCH_DOCS",
            "schema": "DATA",
            "name": "docs"
        }
    else:
        ref = (permissions.get_detailed_reference_associations(ref_name))[-1]
    if ref is None:
        raise ValueError(f'Reference {ref} is not available. Please check your permissions.')
    logger.debug(f"Ref {ref} (type {type(ref)}): {ref}")
    return f'{ref["database"]}.{ref["schema"]}.{ref["name"]}'
