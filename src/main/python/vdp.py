from decimal import *
import yaml
import urllib
import urllib2

def getTxData(node):
    btcaddress = node['crypto'].split('/')[1]
    amount = int(node['amount'])
    return {"address" : btcaddress, "amount": amount}

def isLeaf(node):
    if 'split' in node:
        return False
    else:
        return True

def split(amount, branch, nodes):
    total_shares = Decimal(0)

    for node in branch:
        total_shares += node['shares']

    for node in branch:
        node_ratio = node['shares']/total_shares
        node_amount = amount*node_ratio
        if isLeaf(node):
            new_node = {"id": node['id'], "crypto" : node['crypto'], "amount" : node_amount}
            nodes[node['id']] = new_node
        else:
            split(node_amount, node['split'], nodes)

def getRecipients(amount, url):
    #config = open(file, "r")
    config = urllib2.urlopen(url)
    configitems = yaml.load(config)
    firstbranch = configitems['split']
    nodes = {}
    split(Decimal(amount), firstbranch, nodes)

    recipients = {}
    for node in nodes:
        tx = getTxData(nodes[node])
        recipients[tx['address']] = tx['amount']

    return recipients

def main():
    # test getRecipients
    #recipients = getRecipients(100000, "hackathon-prize.yml")
    recipients = getRecipients(100000, "https://raw.githubusercontent.com/macausource/subsatoshi/hackathon/examples/hackathon-prize.yml")

    print recipients
    print urllib.quote_plus(str(recipients))

if __name__ == '__main__':
    main()
