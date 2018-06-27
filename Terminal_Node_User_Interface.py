from uuid import uuid4

from blockchain import Blockchain
import verification
from wallet import Wallet

class Node:
    def __init__(self):
        #self.wallet.public_key = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction(self):
        recipient = (input('Enter recipient of the transaction: '))
        amount = float(input('Your transaction amount: '))
        return (recipient, amount)

    def print_blockchain_elements(self):
        for block in self.blockchain.get_chain():
            print('Outputting block:')
            print(block)
        else:
            print('-' * 20)

    def user_interface(self):
        waiting_for_input = True
        
        while waiting_for_input:
            print('1: Mine a new block')
            print('2: Add a new transaction')
            print('3: Output Blocks')
            print('4: Check transactions validity')
            print('5: Create wallet')
            print('6: Load wallet')
            print('7: Save wallet')
            print('8: Add Node')
            print('9: Remove Node')
            print('q: Quit')
            user_input = input('Your choice: ')  
            print('\n')
            
            if user_input == '1':
                if not self.blockchain.mine_block():
                    print('Mining failed. Do you have a wallet?')
                   
            elif user_input == '2':
                tx_data = self.get_transaction()
                recipient, amount = tx_data
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction Failed!')
                print(self.blockchain.get_open_transactions())
            
            elif user_input == '3':  
                self.print_blockchain_elements()

            elif user_input == '4':
                if verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions valid')
                else:
                    print('There are invalid transactions')  

            elif user_input == '5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_input == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            
            elif user_input == '7':
                self.wallet.save_keys()
            
            #elif user_input == '8':
             #   node = (input('Enter Node URL: '))
              #  self.blockchain.add_peer_node(node)
               # print(self.blockchain.get_peer_nodes())

            #elif user_input == '9':
             #   node = (input('Enter Node URL: '))
              #  self.blockchain.remove_peer_node(node)
               # print(self.blockchain.get_peer_nodes())

            elif user_input == 'q':    
                waiting_for_input = False

            else: 
                print('Input invalid. Please try Again!')
                
            if not verification.verify_chain(self.blockchain.get_chain()): 
                #print_blockchain_elements()
                print ('Invalid Blockchain')
                break
            
            print('Balance of {}: {:6.2f}'.format(self.wallet.public_key, self.blockchain.get_balance())) 
                
            print('Done!')

node = Node()
node.user_interface()
