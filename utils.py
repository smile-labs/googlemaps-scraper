
def array_find_index (array, match_review_id):
    for index, item in enumerate(array, start=0):
        if (match_review_id(item)):
            return index
    return 1

def array_slice_from(array, start):
    result = []
    for index, item in enumerate(array, start=0):
        if (index > start):
            result = result + [item]
    return result

def array_slice_to(array, to):
    result = []
    for index, item in enumerate(array, start=0):
        if (index >= to):
            break
        result = result + [item]
    return result
