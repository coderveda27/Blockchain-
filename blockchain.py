from __future__ import annotations
from dataclasses import dataclass
import hashlib
from typing import Optional

from python_ta.contracts import check_contracts  

###################################################################################################
# _Transaction and Ledger class definitions
###################################################################################################
@check_contracts
@dataclass
class _Transaction:
    """A transaction in our Titancoin (TC) cryptocurrency system.

    Instance Attributes:
        - sender:
            For a transfer transaction, this is the name of the person sending the money.
            For a mining transaction, this is an empty string.
        - recipient:
            For a transfer transaction, this is the name of the person receiving the money.
            For a mining transaction, this is the name of the person who does the mining
            (and therefore gets the money).
        - amount:
            The number of Titancoins being transferred/mined.
        - next:
            The next transaction in the ledger, or None if this is the most recent
            transaction.
        - prev_digest:
            The digest of the previous transaction in the ledger, or 0 if
            there was no previous transaction.
        - nonce:
            An integer that may be used when computing the transaction digest.

    Representation Invariants:
        - self.recipient != ""
        - self.amount > 0
        - (self.next is None or self.next.prev_digest == 0) or (self.next.prev_digest == digest_from_hash(self))
    """
    sender: str
    recipient: str
    amount: int
    next: Optional[_Transaction] = None
    prev_digest: int = 0  # Default value of 0
    nonce: int = 0  # Default value of 0


@check_contracts
class Ledger:
    """A Titancoin cryptocurrency ledger, storing a sequence of transactions in a linked list.

    Instance Attributes:
        - first: the first transaction in the ledger, or None if there are no transactions
        - last: the last transaction in the ledger, or None if there are no transactions
        - _balance: a mapping from person name to their current balance (i.e., amount of money).
                    This mapping contains a key for every person who has ever been involved with
                    a transaction in this ledger, even if their current balance is 0.

    Representation Invariants:
        - all([amount >= 0 for amount in self._balance.values()])
        - all([names != '' for names in self._balance])
        - (self._balance == {}) ==  (self.first is None and self.last is None)
        - (self.first = None) == (self.last = None)
    """
    first: Optional[_Transaction]
    last: Optional[_Transaction]
    _balance: dict[str, int]

    def __init__(self) -> None:
        """Initialize a new ledger.

        The ledger is created with no transactions and with no people's balances recorded.
        """
        self.first = None
        self.last = None
        self._balance = {}

    ###############################################################################################
    # Part 2(a)
    ###############################################################################################
    def record_transfer(self, sender: str, recipient: str, amount: int) -> None:
        """Record a new transfer transaction with the given sender, recipient, and amount.

        Raise a ValueError if the sender's current balance is less than the given amount,
        or if the sender does not have a balance recorded.

        Preconditions:
        - sender != ''
        - recipient != ''
        - amount > 0

        IMPLEMENTATION NOTES:
        - Use self.last to quickly access the last node in the linked list (much faster than
          iterating through the entire linked list!)
        - Remember to update self.last and self._balance (possibly in addition to self.first)

        >>> ledger = Ledger()
        >>> ledger.record_mining('David', 50)
        >>> ledger.record_mining('Mario', 20)
        >>> ledger._balance
        {'David': 50, 'Mario': 20}
        >>> ledger.record_transfer('David', 'Mario', 10)
        >>> ledger._balance
        {'David': 40, 'Mario': 30}
        >>> new_ledger = Ledger()
        >>> new_ledger.record_mining('David', 5)
        >>> new_ledger.record_transfer('David', 'Mario', 2)
        >>> new_ledger._balance
        {'David': 3, 'Mario': 2}
        """
        new_tansfer = _Transaction(sender, recipient, amount)

        if self._balance[sender] < amount:
            raise ValueError
        elif sender not in self._balance:
            raise ValueError
        else:
            self.last = new_tansfer
            # the sender loses amount so deduct amount from sender's current _balance
            deducted_balance = self._balance[sender] - amount
            self._balance[sender] = deducted_balance

            # add amount to recipient current balance
            if recipient not in self._balance:
                self._balance[recipient] = amount

            else:
                added_balance = self._balance[recipient] + amount
                self._balance[recipient] = added_balance

    def record_mining(self, miner: str, amount: int) -> None:
        """Record a new mining transaction with the given miner (i.e., person who is mining) and amount.

        Preconditions:
        - miner != ''
        - amount > 0

        IMPLEMENTATION NOTES:
        - Use self.last to quickly access the last node in the linked list (much faster than
          iterating through the entire linked list!)
        - Remember to update self.last and self._balance (possibly in addition to self.first)

        >>> ledger = Ledger()
        >>> ledger.record_mining('David', 5)
        >>> ledger.record_mining('Mario', 8)
        >>> ledger._balance
        {'David': 5, 'Mario': 8}
        """
        new_miner = _Transaction(sender='', recipient=miner, amount=amount)

        if self.first is None:
            self.first = new_miner
            self._balance[miner] = amount

        else:
            self.last = new_miner
            self._balance[miner] = amount

    def get_balance(self, person: str) -> int:
        """Return the current balance for the given person.

        Raise ValueError if the given person does not have a balance recorded by this ledger.

        Precondtions:
        - person != ''
        """
        if person not in self._balance:
            raise ValueError
        else:
            current_balance = self._balance[person]
            return current_balance

    def verify_balance(self) -> bool:
        """Return whether this ledger's stored balance is consistent with its transactions.

        This function iterates across all transactions in the ledger and accumulates a
        "balance so far" after each transaction.

        - Return False if you encounter a transaction that is invalid. This occurs when
          a transfer involves a sender who doesn't have a current balance, or whose
          current balance is less than the amount being transferred.
        - Return False if the final balance accumulate does not equal self._balance.
        - Otherwise, return True.
        >>> ledger = Ledger()
        >>> ledger.record_mining('David', 5)
        >>> ledger.record_mining('Mario', 8)
        >>> ledger._balance
        {'David': 5, 'Mario': 8}
        >>> ledger.record_transfer('David', 'Mario', 2)
        >>> ledger._balance
        {'David': 3, 'Mario': 10}
        >>> ledger._balance['David'] += 1000
        >>> ledger.verify_balance()
        False
        """
        balance_so_far = {}
        curr_trans = self.first
        for name in self._balance:
            balance_so_far[name] = 0

        while curr_trans is not None:
            recipient = curr_trans.recipient
            sender = curr_trans.sender
            balance_so_far[recipient] = balance_so_far[recipient] + curr_trans.amount

            if sender != '':
                if self._balance[sender] < curr_trans.amount or self._balance[sender] == 0:
                    return False
                else:
                    balance_so_far[sender] = balance_so_far[sender] - curr_trans.amount
            curr_trans = curr_trans.next
        for name in balance_so_far:
            if balance_so_far[name] != self._balance[name]:
                return False

        return True

    ###############################################################################################
    # Part 2(b)
    ###############################################################################################
    def record_transfer_digest(self, sender: str, recipient: str, amount: int) -> None:
        """Record a new transfer transaction with the given sender, recipient, and amount.

        (NEW) When the transaction is created, it stores the digest of the previous transaction,
        using the digest_from_hash function provided near the bottom of this file. If there are
        no previous transactions, 0 (the default value) is stored instead.

        Raise a ValueError if the sender's current balance is less than the given amount,
        or if the sender does not have a balance recorded.

        Preconditions:
        - sender != ''
        - recipient != ''
        - amount > 0

        IMPLEMENTATION NOTES (NEW):
        - This method should be implemented in a very similar way to Part 2(a).
        """
        new_tansfer = _Transaction(sender, recipient, amount, prev_digest=digest_from_hash(self.last))

        if self._balance[sender] < amount:
            raise ValueError
        elif sender not in self._balance:
            raise ValueError
        else:
            self.last = new_tansfer
            # the sender loses amount so deduct amount from sender's current _balance
            deducted_balance = self._balance[sender] - amount
            self._balance[sender] = deducted_balance

            # add amount to recipient current balance
            if recipient not in self._balance:
                self._balance[recipient] = amount

            else:
                added_balance = self._balance[recipient] + amount
                self._balance[recipient] = added_balance

    def record_mining_digest(self, miner: str, amount: int) -> None:
        """Record a new mining transaction with the given miner (i.e., person who is mining) and amount.

        (NEW) When the transaction is created, it stores the digest of the previous transaction,
        using the digest_from_hash function provided near the bottom of this file. If there are
        no previous transactions, 0 (the default value) is stored instead.

        Preconditions:
        - miner != ''
        - amount > 0

        IMPLEMENTATION NOTES (NEW):
        - This method should be implemented in a very similar way to Part 2(a).
        """
        new_miner = _Transaction(sender='', recipient=miner, amount=amount, prev_digest=digest_from_hash(self.last))

        if self.first is None:
            self.first = new_miner
            self._balance[miner] = amount
            # make prev_digest be 0 since it is the first transaction object in the ledger
            new_miner.prev_digest = 0

        else:
            self.last = new_miner
            self._balance[miner] = amount


###################################################################################################
# Main block
###################################################################################################
if __name__ == '__main__':
    # We have provided the following code to run any doctest examples that you add.
    # (We have not provided any doctest examples in the starter code, but encourage you
    # to add your own.)
    import doctest

    doctest.testmod(verbose=True)

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (In PyCharm, select the lines below and press Ctrl/Cmd + / to toggle comments.)
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['hashlib']
    })
