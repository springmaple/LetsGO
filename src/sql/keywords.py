def _build_index(text: str):
    text = text.lower()
    index = set()
    text_len = len(text)
    i = text_len
    while i > 0:
        j = 0
        while (j + i) <= text_len:
            index.add(text[j:j + i])
            j += 1
        i -= 1

    return index


class Keywords:
    def __init__(self, *original_texts):
        self._original_texts = original_texts

    def to_index(self):
        index = set()
        for original_text in self._original_texts:
            index = index.union(_build_index(original_text))
        return list(index)
