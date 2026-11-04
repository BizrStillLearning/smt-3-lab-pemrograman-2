from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class Node(Generic[T]):
    __slots__ = ("value", "next") # Membatasi alokasi memori objek (tanpa __dict__)

    def __init__(self, value: T) -> None:
        self.value = value
        self.next: Optional["Node[T]"] = None

class LinkedList(Generic[T]):
    def __init__(self) -> None:
        self._head: Optional[Node[T]] = None
        self._size: int = 0

    def push_front(self, value: T) -> None:
        node = Node(value)
        node.next = self._head
        self._head = node
        self._size += 1

    def contains(self, value: T) -> bool:
        cur = self._head
        while cur is not None:
            if cur.value == value:
                return True
            cur = cur.next
        return False

    def remove(self, value: T) -> bool:
        prev = None
        cur = self._head
        while cur is not None:
            if cur.value == value:
                if prev:
                    prev.next = cur.next
                else:
                    self._head = cur.next
                self._size -= 1
                return True
            prev = cur
            cur = cur.next
        return False

    def __len__(self) -> int:
        return self._size

