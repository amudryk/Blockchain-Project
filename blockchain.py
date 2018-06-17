import functools 
import hashlib
import json
import collections
import pickle

genesis_block = {'previous_hash': '', 'transactions': [], 'proof': 100 }
blockchain = [genesis_block] 
MINING_REWARD = 10
open_transactions = []
owner = 'Adam'
participants = {'Adam'}

def add_transaction(recipient, sender=owner, amount=1.0):
    #transaction = {'sender':sender, 'recipient': recipient, 'amount': amount}
    transaction = collections.OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True 
    return False

def get_balance(participant):
    sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, sender, 0)
   
    recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, recipient, 0 )
  
    return amount_recieved - amount_sent

def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

def get_transaction_value():
    recipient = input('Enter recipient of the transaction: ')
    amount = float(input('Your transaction amount: '))
    return (recipient, amount)

def get_user_input():
    user_input = input('Your choice: ')
    return user_input

def hash_block(block):
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

def load_data():
    with open ('blockchain.txt', mode='r') as file:
        #comment out pickle(binary) code
        #file_content = pickle.loads(file.read())
        file_content = file.readlines()
        global blockchain
        global open_transactions
        
        #blockchain = file_content['chain']
        #open_transactions = file_content['ot']
        
        blockchain = json.loads(file_content[0][:-1])
        updated_blockchain = []
        for block in blockchain:
            updated_block = {
                'previous_hash': block['previous_hash'],
                'proof': block['proof'],
                'transactions': [collections.OrderedDict(
                    [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
            }
            updated_blockchain.append(updated_block)
        blockchain = updated_blockchain
        
        open_transactions = json.loads(file_content[1])
        updated_transactions = []
        for tx in open_transactions:
            updated_transaction = collections.OrderedDict(
                [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) 
            updated_transactions.append(updated_transaction)
        open_transactions = updated_transactions


load_data()

def mine_block():
    last_block = blockchain[-1]
    previous_hash = hash_block(last_block)
    
    proof = proof_of_work()
    
    #reward_transaction = {'sender':'MINING', 'recipient': owner, 'amount': MINING_REWARD}
    reward_transaction = collections.OrderedDict([('sender','MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {'previous_hash': previous_hash, 'transactions': copied_transactions, 'proof': proof }
    blockchain.append(block)
    save_data()
    return True 

def print_blockchain_elements():
    for block in blockchain:
        print('Outputting block')
        print(block)
    else:
         print('-' * 20)

def save_data():
    with open('blockchain.txt', mode='w') as file:
        file.write(json.dumps(blockchain))
        file.write('\n')
        file.write(json.dumps(open_transactions))
        
        #pickle(binary) code
        #save_data = { 'chain': blockchain, 'ot': open_transactions }
        #file.write(pickle.dumps(save_data))

def valid_proof(transactions, previous_hash, proof):
    guess = (str(transactions) + str(previous_hash) + str(proof)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    print(guess_hash)
    return guess_hash[0:2] == '99'

def proof_of_work():
    last_block = blockchain[-1]
    previous_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, previous_hash, proof):
        proof += 1
    return proof

def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index > 0:
            if block['previous_hash'] != hash_block(blockchain[index - 1]):
                return False
            if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
                print('Proof of work is invalid')
                return False
    return True  

def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']

def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])
      

waiting_for_input = True

while waiting_for_input:
    print('6: Check transaction validity')
    print('5: Ouput Participants')
    print('4: Mine a new block')
    print('3: Add a new transaction')
    print('2: Output Blocks')
    print('1: Manipulate the chain')
    print('0: Quit')
    user_input = get_user_input()
    if user_input == 6:
        if verify_transactions():
            print('All transactions valid')
        else:
            print('There are invalid transactions')    
    
    elif user_input == 5:
        print(participants)
           
    elif user_input == 4:
       if mine_block():
           open_transactions = []
           save_data()

    elif user_input == 3:
        tx_data = get_transaction_value()
        recipient , amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction Failed!')
        print(open_transactions)

    elif user_input == 2:  
        print_blockchain_elements()

    elif user_input == 1:
        if len(blockchain) >= 1:    
            blockchain[0] = {
                'previous_hash': '', 
                'transactions': [{'sender': 'John', 'recipient': 'Adam', 'amount': 100}]
            }

    elif user_input == 0:    
        waiting_for_input = False

    else: 
        print('Input invalid. Please try Again!')
        
    if not verify_chain(): 
       print_blockchain_elements()
       print ('Invalid Blockchain')
       break
    print('Balances: \n{}: {:10.2f}'.format(owner,get_balance('Adam'))) 
    
print('Balances: \n{}: {:10.2f}'.format(owner,get_balance('Adam'))) 
print('Done!')


