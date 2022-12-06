import datetime
import hashlib


class Pair:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None


class HashTable:

    def __init__(self, capacity=1):
        if capacity < 1:
            return  # cant b negative
        self.capacity = capacity
        self.size = 0  # num vals inserted
        self.bins = self.capacity * [None]
        self.loadFactor = 0.75

    def hash(self, key):
        key = hashlib.sha1(key.encode())
        key = key.hexdigest()
        key = int(key, base=16)
        return key % self.capacity

    def insert(self, key, value):
        hashKey = self.hash(key)

        pair = self.bins[hashKey]

        if pair == None:
            self.bins[hashKey] = Pair(key, value)
        else:
            # bin has val, go to end of list
            curr = pair
            while pair != None:
                # replace if same input key
                curr = pair
                if curr.key == key:
                    curr.val = value
                    return
                pair = pair.next

            curr.next = Pair(key, value)

        self.size += 1
        loadFact = self.size/self.capacity
        
        if loadFact > 0.75:
            self.reHash()

    def find(self, key):
        ind = self.hash(key)
        curr = self.bins[ind]
        while curr != None and curr.key != key:
            curr = curr.next  # curr is at key or none at end of loop
        if curr == None:
            return None
        else:
            return curr.val

    def remove(self, key):
        ind = self.hash(key)
        prev = None
        curr = self.bins[ind]
        while curr != None and curr.key != key:
            prev = curr
            curr = curr.next
        if curr == None:
            return None
        else:
            self.size -= 1
            if prev == None:
                curr = None
            else:
                prev.next = prev.next.next  # deletes curr

    def reHash(self):
        tempSlots = self.bins
        bins = 2 * self.capacity

        self.bins = [None]*bins

        self.size = 0
        self.capacity *= 2

        for i in range(len(tempSlots)):
            curr = tempSlots[i]
            while curr != None:
                self.insert(curr.key, curr.val)
                curr = curr.next

    def printTable(self):
        for i in range(len(self.bins)):
            curr = self.bins[i]
            while curr != None:
                print("key:", curr.key, "value:", curr.val)
                curr = curr.next
        print()


if __name__ == '__main__':
    h = HashTable(1)
    import time
    import datetime
    x = datetime.datetime(2022, 12, 2).date()
    h.insert(x, "hello")
    x = datetime.date(2022, 12, 1)
    h.insert(x, "duh")
    # x = int(time.mktime(x.timetuple()))
    h.printTable()
