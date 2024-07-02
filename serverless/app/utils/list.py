def merge_by_key(originals, merges, key, new_key):
    merge_map = {merge[key]: merge for merge in merges}
    
    for original in originals:
        if original[key] in merge_map:
            original[new_key] = merge_map[original[key]]
    
    return originals

