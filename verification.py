import hashlib
from hash import hash_block

def verify_chain(blockchain):
    for (index, block) in enumerate(blockchain):
        if index > 0:
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
    return True  
    
def verify_transaction(transaction, get_balance):
    sender_balance = get_balance()
    return sender_balance >= transaction.amount

def verify_transactions(open_transactions, get_balance):
    return all([verify_transaction(tx, get_balance) for tx in open_transactions])

def valid_proof(transactions, last_hash, proof):
    guess = (str([tx.ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[0:2] == '99'  