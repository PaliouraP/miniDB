'''Using CRC32 algorithm as hash function. 
More about CRC32 here: https://en.wikipedia.org/wiki/Cyclic_redundancy_check#CRC-32_algorithm
More about hash table here: https://en.wikipedia.org/wiki/Hash_table'''


from random import randint
from typing import TypeVar, Callable,  List
from bisect import bisect_left
T = TypeVar('T')

class HashTable:
    def __init__(self):
        # initial table size
        self.table_size: int = 23

        # initializing all table slots to none
        self.table: List[(T, T)] = [None] * self.table_size

        # number of filled slots
        self.filled_count: int = 0

        # table resize threshold
        self.resize_threshold: float = 0.75

        # crc32 hash function
        self.hash_function: Callable = self.crc32_hash

        # crc32 table
        self.crc32_table: List[int] = self.crc32_table()

        #random integer for use when the key is not a string
        self.a: int = randint(1, 2**32)


    def __repr__(self) -> str:
        ''' Returns HashTable's string representation
        ({key1: value1, key2: value2, ..., keyN: valueN})
        '''

        r: str = '{' + ''.join([(f'\'{pair[0]}\'' if isinstance(pair[0], str) else str(pair[0])) + ': ' +
                                (f'\'{pair[1]}\'' if isinstance(
                                    pair[1], str) else str(pair[1])) + ', '
                                for pair in self.table if pair is not None])
        return r[:-2] + '}' if len(r) > 1 else '{}'


    @property
    def load_factor(self) -> float:
        # calculates table's load factor which tells us the percentage of slots filled
        return self.filled_count / self.table_size

    '''Handles encoding of the key supplied to the hash function.'''
    @staticmethod
    def encode(key: T) -> int:
        # function to encode the key (string or integer) using a polynomial hashing sheme        
        if isinstance(key, str):
            hash_value: int = 0
            # p should be a prime number roughly equal to the number of characters in the input alphabet.
            p: int = 97
            # we have 95 printable ASCII characters, so we use 97
            m: int = 115561578124838522881
            # this should be a huge prime number 20th in the OEIS A118839

            p_power: int = 1
            for character in key:
                hash_value = (hash_value + ord(character) * p_power) % m
                p_power = (p_power * p) % m
            return hash_value
        elif isinstance(key, int):
            return key
        else:
            raise Exception(
                f"Cannot encode {type(key)} (Only integers & strings supported)")

    '''Generates a table of values for use with the CRC32 hash method.'''
    @staticmethod
    def crc32_table() -> List[int]:
        # returns a table of values for use with the CRC32 hash
        table: List[int] = []
        for i in range(256):
            k: int = i
            for j in range(8):
                if k & 1:
                    k ^= 0x1db710640 # bitwise xor
                k >>= 1 # bitwise right shift
            table.append(k)
        return table

    '''Hasing method that hashes the key generated by the encode() method.'''
    def crc32_hash(self, key: T) -> int:
        # if the key is a string
        if isinstance(key, str):
            crc32: int = 0xffffffff
            # encode the characters as the function do not accept strings
            for k in key.encode('utf-8'):
                crc32 = (crc32 >> 8) ^ self.crc32_table[(crc32 & 0xff) ^ k]
            crc32 ^= 0xffffffff  # invert all bits
            return crc32 % self.table_size
        else:
            # returns a hash of key using h(k) = (a * key) mod m where m is a prime number.
            return (self.a * self.encode(key)) % self.table_size

    '''Increases the table_size once load factor reaches threshold'''
    def resize(self) -> None:
        '''Using Sieve of Eratosthenes to find the prime number
        More here: https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes'''
        size: int = 2 * self.table_size + 1
        if size > self.primes_table[len(self.primes_table) - 1]:
            self.primes_table = self.primes_below_n(10 * size)
        size: int = self.primes_table[bisect_left(self.primes_table, size)]

        # rehash all entries of the hash table after the increase in table size
        temp: List[(T, T)] = self.table
        self.table_size = size
        self.table = [None] * self.table_size
        self.filled_count = 0

        for pair in temp:
            if pair is not None:
                self.insert(pair[0],pair[1])
    
    '''Handles insert and update'''
    def insert(self, key: T, value: T) -> None:
        # check if load fcator is equal to or greater than the resize threshold
        if self.load_factor >= self.resize_threshold:
            self.resize()

        # get an index location for 'key'
        index: int = self.hash_function(key)

        # index location not occupied
        if self.table[index] is None:
            self.table[index] = (key, value)
            self.filled_count += 1
        else:  # idx location occupied
            if self.table[index][0] == key:  # trying to insert to the same key
                # update 'value' at 'key'
                self.table[index] = (self.table[index][0], value)
