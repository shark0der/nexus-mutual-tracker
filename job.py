from app import db
from app.models import *

utils.set_current_crypto_prices()
parser.parse_etherscan_data()
grapher.cache_graph_data()
