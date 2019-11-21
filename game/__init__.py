from typing import List


class QuickSortPartition:
    def __init__(self, p1: int, po1: int, p2: int, po2: int):
        self.ps1: int = p1  # 1st partition start
        self.pe1: int = po1 # 1st partition end
        self.ps2: int = p2  # 2nd partition start
        self.pe2: int = po2 # 2nd partition end

    def is_first_one(self):
        return self.ps1 == self.pe1

    def is_second_one(self):
        return self.ps2 == self.pe2


class WordmapWord:
    def __init__(self, word: str):
        self.count: int = 0
        self.word: str = word

    def __ge__(self, other):
        if other is WordmapWord:
            return other.count >= self.count

        return False

    def __le__(self, other):
        if other is WordmapWord:
            return other.count <= self.count

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
        get = self.words[first], self.words[last]

        self.words[last], self.words[first] = get

    def __partition_quick_sort(self, lo: int, hi: int) -> QuickSortPartition:
        pivot_index = hi
        orig_lo = lo

        pivot = self.words[pivot_index]
        hi -= 1

        while True:
            # get a lo value
            while not lo >= hi:
                current_word = self.words[lo]

                if current_word >= pivot:
                    lo += 1
                else:
                    break

            # get a hi value
            while not lo >= hi:
                current_word = self.words[hi]

                if current_word <= pivot:
                    hi -= 1
                else:
                    break

            # if we have reached the middle, swap pivot and middle object
            if lo >= hi:
                self.__swap(pivot_index, lo)

                # return partition info
                return QuickSortPartition(orig_lo, lo - 1, hi + 1, pivot_index)
            else:
                # swap the two resulting values
                self.__swap(lo, hi)

    def quick_sort(self, lo: int, hi: int):
        partition = self.__partition_quick_sort(lo, hi)

        if not partition.is_first_one():
            self.quick_sort(partition.ps1, partition.pe1)
        if not partition.is_second_one():
            self.quick_sort(partition.ps2, partition.pe2)

    def get_words(self, limit: int) -> List[WordmapWord]:
        self.quick_sort(0, len(self.words) - 1)

        return self.words[:-limit]
