class Badges:
    def __init__(self, binary: int):
        self.data: int = binary

    def _bit(self, index: int) -> bool:
        return (self.data >> index) & 0b1 > 0

    def _set_bit(self, index: int, on: bool) -> None:
        self.data

    def as_int(self) -> int:
        return self.data

    @property
    def programmer(self) -> bool:
        return self._bit(0)

    @property
    def supporter(self) -> bool:
        return self._bit(1)

    # class methods
    @classmethod
    def zero(cls):
        return cls(0)