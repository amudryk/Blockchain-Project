from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')

@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')

@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {'message': 'Saving keys failed.'}
        return jsonify(response), 500
        
@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance() 
        }
        return jsonify(response), 201
    else:
        response = {'message': 'Loading keys failed.'}
        return jsonify(response), 500

@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500

@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Some data missing.'}
        return jsonify(response), 400
    block = values['block']
    chain = blockchain.get_chain()
    if block['index'] == chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Block added.'}
            return jsonify(response), 201
        else:
            response = {'message': 'Block Invalid.'}
            return jsonify(response), 409
    elif block['index'] > chain[-1].index:
        response = {'message': 'Blockchain differs from local blockchain'}
        blockchain.conflicts = True
        return jsonify(response), 200
    else: 
        response = {'message': 'Blockchain is shorter, block not added'}
        return jsonify(response), 409

@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(element in values for element in required):
        response = {'message': 'Some data missing.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)
    if success:
        response = { 'message': 'Successfully added transaction.'}
        return jsonify(response), 201
    else:
        response = {'message': 'Creating a transaction failed.'}
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {'message': 'No wallet' }
        return jsonify(response), 400

    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    
    required_fields = ['recipient', 'amount']
    
    if not all(field in values for field in required_fields):
        response = {'message': 'Required data is missing.'}
        return jsonify(response), 400

    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {'message': 'Creating a transaction failed.'}
        return jsonify(response), 500

@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.conflicts:
        response = {'message': 'Resolve conflicts first, block not added.'}
        return jsonify(response), 409
    
    mined_block = blockchain.mine_block()
    if mined_block != None:
        dict_block = mined_block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully.',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500

@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced_chain = blockchain.resolve_conflicts()
    if replaced_chain:
        response = {'message': 'Chain replaced.'}
    else:
        response = {'message': 'Local chain kept.'}
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.get_chain()
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200

@app.route('/open-transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200

@app.route('/nodes', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {'message': 'No data attached.'}
        return jsonify(response), 400
    if 'node' not in values:
        response = {'message': 'No node data.'}
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully.',
        'node_list': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201

# input ex./node/localhost:1000
@app.route('/nodes/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {'message': 'No node data'}
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed successfully.',
        'node_list': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200

@app.route('/nodes', methods=['GET'])
def get_node():
    nodes = blockchain.get_peer_nodes()
    response = {'nodes_list': nodes}
    return jsonify(response), 200
    
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default = 9999)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
