import functools 
import hashlib
import json
import collections
import pickle

from hash import hash_block
from block import Block
from transaction import Transaction
import verification

MINING_REWARD = 10

class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block('', [], 100, 0)
        self.chain = [genesis_block]
        self.open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    def add_transaction(self, recipient, hosting_node, amount=1.0):
        #transaction = {'sender':sender, 'recipient': recipient, 'amount': amount}
        transaction = Transaction(hosting_node, recipient, amount)
        if verification.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction) 
            self.save_data()
            return True 
        return False

    def get_balance(self):
        participant = self.hosting_node
    
        sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.chain]
        open_tx_sender = [tx.amount for tx in self.open_transactions if tx.sender == participant]
        sender.append(open_tx_sender)
        amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, sender, 0)
    
        recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.chain]
        amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, recipient, 0 )
    
        return amount_recieved - amount_sent

    def load_data(self):

        try:
            with open ('blockchain.txt', mode='r') as f:
                #file_content = pickle.loads(file.read())
                #blockchain = file_content['chain']
                #open_transactions = file_content['ot']
                
                file_content = f.readlines()
                
                blockchain = json.loads(file_content[0][:-1])
                
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions
        
        except (IOError,IndexError):
            pass

    def mine_block(self):
        last_block = self.chain[-1]
        previous_hash = hash_block(last_block)
        proof = self.proof_of_work()
        
        #reward_transaction = {'sender':'MINING', 'recipient': owner, 'amount': MINING_REWARD}
        reward_transaction = Transaction('MINING', self.hosting_node, MINING_REWARD)
        
        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)
        mined_block = Block(previous_hash, copied_transactions, proof)
        self.chain.append(mined_block)
        self.open_transactions = []
        self.save_data()
        return True 

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_otx = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(saveable_otx))
                
                #pickle(binary) code
                #save_data = { 'chain': blockchain, 'ot': open_transactions }
                #file.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')

    def proof_of_work(self):
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not verification.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof


      


