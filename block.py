from time import time

class Block:
    def __init__(self, previous_hash, transactions, proof, timestamp=None):
        self.previous_hash = previous_hash
        self.timestamp = time() if timestamp is None else timestamp
        self.transactions = transactions
        self.proof = proof
    
    def __repr__(self):
        return 'Previous Hash: {}, Proof: {}, Transactions: {} '.format(self.previous_hash, self.proof, self.transactions)