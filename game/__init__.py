from typing import List


class WordmapWord:
    def __init__(self, word: str):
        self.count: int = 0
        self.word: str = word

    def __str__(self):
        return self.word

    def __gt__(self, other):
        if isinstance(other, WordmapWord):
            return self.count > other.count

        return False

    def __lt__(self, other):
        if isinstance(other, WordmapWord):
            return self.count < other.count

        return False

    def inc(self):
        self.count += 1


class Wordmap:
    def __init__(self):
        self.words: List[WordmapWord] = []

    def inc_word(self, word_str: str):
        w = None

        for word in self.words:
            if word.word == word_str:
                w = word

        if w is None:
            # create a word
            w = WordmapWord(word_str)
            self.words.append(w)

        w.inc()

    def __swap(self, first: int, last: int):
        self.words[last], self.words[first] = self.words[first], self.words[last]

    def __partition_quick_sort(self, lo: int, hi: int) -> int:
        pivot = self.words[hi]
        i = lo  # index of smaller element

        for j in range(lo, hi):
            # is the current element smaller than pivot?
            if self.words[j] > pivot:
                # increment index of smaller element
                self.__swap(i, j)
                i += 1

        self.__swap(i, hi)
        return i

    def quick_sort(self, lo: int, hi: int):
        partition = self.__partition_quick_sort(lo, hi)

        if not partition == lo:
            self.quick_sort(lo, partition - 1)
        if not partition == hi:
            self.quick_sort(partition + 1, hi)

    def get_words(self, limit: int) -> List[WordmapWord]:
        self.quick_sort(0, len(self.words) - 1)

        return self.words[:limit]
