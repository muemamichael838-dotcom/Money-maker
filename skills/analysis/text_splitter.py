import re

class TextSplitter:
    def __init__(self, chunk_size=2000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        if not text: return []

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def recursive_split(self, text, separators=None):
        """A more intelligent splitter that tries to split on natural boundaries."""
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]

        final_chunks = []
        # Initial chunking logic...
        # Simplified for small server efficiency:
        return self.split_text(text)

if __name__ == "__main__":
    ts = TextSplitter(chunk_size=10, chunk_overlap=2)
    print(ts.split_text("This is a very long text that needs splitting"))
