import functools 
import hashlib
import json
import collections
import pickle

from block import Block
from transaction import Transaction

blockchain = [] 
open_transactions = []
MINING_REWARD = 10
owner = 'Adam'


def add_transaction(recipient, sender=owner, amount=1.0):
    #transaction = {'sender':sender, 'recipient': recipient, 'amount': amount}
    transaction = Transaction(sender, recipient, amount)
    if verify_transaction(transaction):
        open_transactions.append(transaction) 
        save_data()
        return True 
    return False

def get_balance(participant):
    sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in blockchain]
    open_tx_sender = [tx.amount for tx in open_transactions if tx.sender == participant]
    sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, sender, 0)
   
    recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in blockchain]
    amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, recipient, 0 )
  
    return amount_recieved - amount_sent

def get_transaction():
    recipient = str(input('Enter recipient of the transaction: '))
    amount = float(input('Your transaction amount: '))
    return (recipient, amount)

def hash_block(block):
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.ordered_dict() for tx in hashable_block['transactions']]
    return hashlib.sha256(json.dumps(hashable_block, sort_keys=True).encode()).hexdigest()

def load_data():
    global blockchain
    global open_transactions

    try:
        with open ('blockchain.txt', mode='r') as f:
            #file_content = pickle.loads(file.read())
            #blockchain = file_content['chain']
            #open_transactions = file_content['ot']
            
            file_content = f.readlines()
            
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                updated_block = Block(block['previous_hash'], tx, block['proof'], block['timestamp'])
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions
    
    except (IOError,IndexError):
        print('File not found!')

        genesis_block = Block('', [], 100, 0)
        blockchain = [genesis_block] 
        open_transactions = []

load_data()

def mine_block():
    last_block = blockchain[-1]
    previous_hash = hash_block(last_block)
    proof = proof_of_work()
    
    #reward_transaction = {'sender':'MINING', 'recipient': owner, 'amount': MINING_REWARD}
    reward_transaction = Transaction('MINING', owner, MINING_REWARD)
    
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    mined_block = Block(previous_hash, copied_transactions, proof)
    blockchain.append(mined_block)
    save_data()
    return True 

def print_blockchain_elements():
    for block in blockchain:
        print('Outputting block:')
        print(block)
    else:
         print('-' * 20)

def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:
            saveable_blockchain = [block.__dict__ for block in [Block(block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in blockchain]]
            f.write(json.dumps(saveable_blockchain))
            f.write('\n')
            saveable_otx = [tx.__dict__ for tx in open_transactions]
            f.write(json.dumps(saveable_otx))
            
            #pickle(binary) code
            #save_data = { 'chain': blockchain, 'ot': open_transactions }
            #file.write(pickle.dumps(save_data))
    except IOError:
        print('Saving failed!')

def valid_proof(transactions, last_hash, proof):
    guess = (str([tx.ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[0:2] == '99'

def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof

def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index > 0:
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
    return True  

def verify_transaction(transaction):
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount

def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])
      

waiting_for_input = True

while waiting_for_input:
    print('1: Mine a new block')
    print('2: Add a new transaction')
    print('3: Output Blocks')
    print('4: Check transactions validity')
    print('q: Quit')
    user_input = input('Your choice: ')  
    print('\n')
    
    if user_input == '1':
       if mine_block():
           open_transactions = []
           save_data()

    elif user_input == '2':
        tx_data = get_transaction()
        recipient, amount = tx_data
        if add_transaction(recipient=recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction Failed!')
        print(open_transactions)
    
    elif user_input == '3':  
        print_blockchain_elements()

    elif user_input == '4':
        if verify_transactions():
            print('All transactions valid')
        else:
            print('There are invalid transactions')  

    elif user_input == 'q':    
        waiting_for_input = False

    else: 
        print('Input invalid. Please try Again!')
        
    if not verify_chain(): 
       #print_blockchain_elements()
       print ('Invalid Blockchain')
       break
    print('Balances: \n{}: {:10.2f}'.format(owner,get_balance('Adam'))) 
    

print('Done!')


