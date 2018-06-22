from uuid import uuid4

from blockchain import Blockchain
import verification

class Node:
    def __init__(self):
        #self.id = str(uuid4())
        self.id = 'Adam'
        self.blockchain = Blockchain(self.id)

    def get_transaction(self):
        recipient = (input('Enter recipient of the transaction: '))
        amount = float(input('Your transaction amount: '))
        return (recipient, amount)

    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
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
            print('q: Quit')
            user_input = input('Your choice: ')  
            print('\n')
            
            if user_input == '1':
                self.blockchain.mine_block()
                   
            elif user_input == '2':
                tx_data = self.get_transaction()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction Failed!')
                print(self.blockchain.open_transactions)
            
            elif user_input == '3':  
                self.print_blockchain_elements()

            elif user_input == '4':
                if verification.verify_transactions(self.blockchain.open_transactions, self.blockchain.get_balance):
                    print('All transactions valid')
                else:
                    print('There are invalid transactions')  

            elif user_input == 'q':    
                waiting_for_input = False

            else: 
                print('Input invalid. Please try Again!')
                
            if not verification.verify_chain(self.blockchain.chain): 
                #print_blockchain_elements()
                print ('Invalid Blockchain')
                break
            
            print('Balance of {}: {:6.2f}'.format(self.id, self.blockchain.get_balance())) 
                
            print('Done!')

node = Node()
node.user_interface()