from .. import db, r
from .models import HistoricalPrice
from datetime import datetime
import json
import requests

def query_table(table, order=None):
  rows = []
  query = table.query.all() if order is None else table.query.order_by(order.asc()).all()
  for row in query:
    row = row.__dict__
    del row['_sa_instance_state']
    rows.append(row)
  return rows

def get_last_id(table):
  id = db.session.query(db.func.max(table.id)).scalar()
  return 0 if not id else id

def get_latest_block_number(table):
  if table is None:
    return 0
  block_number = db.session.query(db.func.max(table.block_number)).scalar()
  return 0 if not block_number else block_number

def get_historical_crypto_price(symbol, timestamp):
  crypto_price = db.session.query(HistoricalPrice).filter_by(timestamp=timestamp).first()
  if crypto_price is not None:
    return crypto_price.eth_price if symbol == 'ETH' else crypto_price.dai_price

  api = 'histominute' if (datetime.now() - timestamp).days < 7 else 'histohour'
  url = 'https://min-api.cryptocompare.com/data/%s?fsym=ETH&tsym=USD&limit=1&toTs=%s' % \
      (api, timestamp.timestamp())
  eth_price = requests.get(url).json()['Data'][-1]['close']
  url = 'https://min-api.cryptocompare.com/data/%s?fsym=DAI&tsym=USDT&limit=1&toTs=%s' % \
      (api, timestamp.timestamp())
  dai_price = requests.get(url).json()['Data'][-1]['close']

  try:
    db.session.add(HistoricalPrice(
      timestamp=timestamp,
      eth_price=eth_price,
      dai_price=dai_price
    ))
    db.session.commit()
  except:
    db.session.rollback()
    crypto_price = db.session.query(HistoricalPrice).filter_by(timestamp=timestamp).first()
    return crypto_price.eth_price if symbol == 'ETH' else crypto_price.dai_price
  return eth_price if symbol == 'ETH' else dai_price

def set_current_crypto_prices():
  url = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms=ETH,DAI&tsyms=USD'
  result = requests.get(url).json()
  r.set('ETH', result['ETH']['USD'])
  r.set('DAI', result['DAI']['USD'])

def json_to_csv(graph):
  data = json.loads(r.get(graph))
  if type(data) is list:
    csv = [list(data[0].keys())]
    for row in data:
      csv.append([row[key] for key in csv[0]])
    return csv
  elif 'USD' in data:
    csv = [[''] + list(data.keys())]
    for key in sorted(list(data[csv[0][1]].keys())):
      csv.append([key, data[csv[0][1]][key], data[csv[0][2]][key]])
    return csv
  else:
    csv = []
    for key in sorted(data.keys()):
      csv.append([key, data[key]])
    return csv

def timestamp_to_mcr(mcrs, timestamp):
  for i in range(len(mcrs)):
    mcr = mcrs[i]
    if mcr['timestamp'] > datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'):
      if i == 0:
        return 7000
      return mcrs[i - 1]['mcr']
  return mcrs[-1]['mcr']

def address_to_contract_name(address):
  names = {
    '080bf510fcbf18b91105470639e9561022937712': '0x',
    '12459c951127e0c374ff9105dda097662a027093': '0x',
    'b27f1db0a7e473304a5a06e54bdf035f671400c0': '0x',
    '11111254369792b2ca5d084ab5eea397ca8fa48b': '1inch.exchange',
    '3dfd23a6c5e8bbcfc9581d2e864a68feb6a076d3': 'Aave',
    'c1d2819ce78f3e15ee69c6738eb1b400a26e632a': 'Aave',
    '398ec7346dcd622edc5ae82352f02be94c62d119': 'Aave',
    'd36132e0c1141b26e62733e018f12eb38a7b7678': 'Ampleforth',
    'b1dd690cc9af7bb1a906a9b5a94f94191cc553ce': 'Argent',
    '9424b1412450d0f8fc2255faf6046b98213b76bd': 'Balancer',
    'b1cd6e4153b2a390cf00a6556b0fc1458c4a5533': 'Bancor',
    '2f9ec37d6ccfff1cab21733bdadede11c823ccb0': 'Bancor',
    '1f573d6fb3f13d689ff844b4ce37794d79a7ff1c': 'Bancor',
    'd5d2b9e9bcd172d5fc8521afd2c98dd239f5b607': 'Band Protocol',
    '8b3d70d628ebd30d4a2ea82db95ba2e906c71633': 'bZx',
    '514910771af9ca656af840dff83e8264ecf986ca': 'ChainLink',
    '3d9819210a31b4961b30ef54be2aed79b9c9cd3b': 'Compound',
    '4ddc2d193948926d02f9b1fe9e1daa0718270ed5': 'Compound',
    '3fda67f7583380e67ef93072294a7fac882fd7e7': 'Compound',
    'f5dce57282a584d2746faf1593d3121fcac444dc': 'Compound',
    '5d3a536e4d6dbd6114cc1ead35777bab948e3643': 'Compound',
    '6c8c6b02e7b2be14d4fa6022dfd6d75921d90e4e': 'Compound',
    '7fc77b5c7614e1533320ea6ddc2eb61fa00a9714': 'Curve BTC Pools',
    '45f783cce6b7ff23b2ab2d70e416cdb7d6055f51': 'Curve Stablecoin Pools',
    '79a8c46dea5ada233abaffd40f3a0a2b1e5a4f27': 'Curve Stablecoin Pools',
    'df5e0e81dff6faf3a7e52ba697820c5e32d806a8': 'Curve Stablecoin Pools',
    'a5407eae9ba41422680e2e00537571bcc53efbfd': 'Curve Stablecoin Pools',
    '06012c8cf97bead5deae237070f9587f8e7a266d': 'CryptoKitties',
    '241e82c79452f51fbfc89fac6d912e021db1a3b7': 'DDEX',
    '5d22045daceab03b158031ecb7d9d06fad24609b': 'DeversiFi',
    '02285acaafeb533e03a7306c55ec031297df9224': 'dForce',
    '8ef1351941d0cd8da09d5a4c74f2d64503031a18': 'Dharma',
    '4e0f2b97307ad60b741f993c052733acc1ea5811': 'Dharma',
    'f7b3fc555c458c46d288ffd049ddbfb09f706df7': 'Dharma',
    '519b70055af55a007110b4ff99b0ea33071c720a': 'DXdao',
    '1e0447b19bb6ecfdae1e4ae1694b0c3659614e4e': 'dYdX',
    '364508a5ca0538d8119d3bf40a284635686c98c4': 'dYdX',
    'fec6f679e32d45e22736ad09dfdf6e3368704e31': 'Edgeware',
    '1b75b90e60070d37cfa9d87affd124bb345bf70a': 'Edgeware',
    '3f8a2f7bcd70e7f7bdd3fbb079c11d073588dea2': 'Fireball',
    '12f208476f64de6e6f933e55069ba9596d818e08': 'Flexa',
    '4a57e687b9126435a9b19e4a802113e266adebde': 'Flexa',
    'b3775fb83f7d12a36e0475abdd1fca35c091efbe': 'Fomo3D',
    '6e95c8e8557abc08b46f3c347ba06f8dc012763f': 'Gnosis Multisig',
    'ff1a8eda5eacdb6aaf729905492bdc6376dbe2dd': 'Gnosis Multisig',
    '34cfac646f301356faa8b21e94227e3583fe3f5f': 'Gnosis Safe',
    '2b591e99afe9f32eaa6214f7b7629768c40eeb39': 'HEX',
    '2a0c0dbecc7e4d658f48e01e3fa353f44050c208': 'IDEX',
    '10ec0d497824e342bcb0edce00959142aaa766dd': 'Idle',
    '78751b12da02728f467a44eac40f5cbc16bd7934': 'Idle',
    '498b3bfabe9f73db90d252bcd4fa9548cd0fd981': 'InstaDApp',
    '3a306a399085f3460bbcb5b77015ab33806a10d5': 'InstaDApp',
    '3361aa92e426e052141daf9e41a09d36e994ba23': 'Kickback',
    '63825c174ab367968ec60f061753d3bbd36a0d8f': 'Kyber Network',
    '9aab3f75489902f3a48495025729a0af77d4b11e': 'Kyber Network',
    '8573f2f5a3bd960eee3d998473e50c75cdbe6828': 'Livepeer',
    '448a5065aebb8e423f0896e6c5d525c040f59af3': 'MakerDAO',
    '9f8f72aa9304c8b593d555f12ef6589cc3a579a2': 'MakerDAO',
    'bda109309f9fafa6dd6a9cb9f1df4085b27ee8ef': 'MakerDAO',
    '9b0f70df76165442ca6092939132bbaea77f2d7a': 'MakerDAO',
    'f53ad2c6851052a81b42133467480961b2321c09': 'MakerDAO',
    '35d1b3f3d7966a1dfe207aa4514c12a259a0492b': 'MakerDAO',
    '89d24a6b4ccb1b6faa2625fe562bdd9a23260359': 'MakerDAO',
    '6b175474e89094c44da98b954eedeac495271d0f': 'MakerDAO',
    'ba23485a04b897c957918fde2dabd4867838140b': 'Market Protocol',
    '6217d5392f6b7b6b3a9b2512a2b0ec4cbb14c448': 'Market Protocol',
    '94772cc6e33b186bfdd0719a287f12d3ca816657': 'Market Protocol',
    '3457905deea11ddc085bc7bfaa8813aab26b2ded': 'Market Protocol',
    '0d580ae50b58fe08514deab4e38c0dfdb0d30adc': 'Melon',
    'ec67005c4e498ec7f55e092bd1d35cbc47c91892': 'Melon',
    '5f9ae054c7f0489888b1ea46824b4b9618f8a711': 'Melon',
    '58c5ad890fd9b25145f05f5afee11cb5b8f616de': 'MetaMoneyMarket',
    '1fd169a4f5c59acf79d0fd5d91d1201ef1bce9f1': 'MolochDAO',
    '85bb8a852c29d8f100cb97ecdf4589086d1be2dd': 'Monolith',
    'afce80b19a8ce13dec0739a1aab7a028d6845eb3': 'mStable',
    '08c3a887865684f30351a0ba6d683aa9b539829a': 'Nexus Mutual',
    '802275979b020f0ec871c5ec1db6e412b72ff20b': 'Nuo Network',
    'd26114cd6ee289accf82350c8d8487fedb8a0c07': 'OmiseGO',
    'b529964f86fbf99a6aa67f72a27e59fa3fa4feac': 'Opyn',
    '132030497cbc19d10cb2690ecf9690803519b5de': 'ParaSwap',
    '6b158039b9678b7452f311deb12dd08c579dad26': 'ParaSwap',
    '72338b82800400f5488eca2b5a37270ba3b7a111': 'ParaSwap',
    'f92c1ad75005e6436b4ee84e88cb23ed8a290988': 'ParaSwap',
    'd0181C718009031F1D5c342AB91ea58D75A2522f': 'ParaSwap',
    '86969d29f5fd327e1009ba66072be22db6017cc6': 'ParaSwap',
    '458dabf1eff8fcdfbf0896a6bd1f457c01e2ffd6': 'Plasm Network',
    '4aa42145aa6ebf72e164c9bbc74fbd3788045016': 'POA Network',
    'e1579debdd2df16ebdb9db8694391fa74eea201e': 'POA Network',
    'b7896fce748396ecfc240f5a0d3cc92ca42d7d84': 'PoolTogether',
    '29fe7d60ddf151e5b52e5fab4f1325da6b2bd958': 'PoolTogether',
    '932773ae4b661029704e731722cf8129e1b32494': 'PoolTogether',
    'e80d347df1209a76dd9d2319d62912ba98c54ddd': 'Ren',
    '408e41876cccdc0f92210600ef50372656052a38': 'Ren',
    'af350211414c5dc176421ea05423f0cc494261fb': 'Saturn Network',
    '5b67871c3a857de81a1ca0f9f7945e5670d986dc': 'Set Protocol',
    'f55186cc537e7067ea616f2aae007b4427a120c8': 'Set Protocol',
    '882d80d3a191859d64477eb78cca46599307ec1c': 'Set Protocol',
    '7ee7ca6e75de79e618e88bdf80d0b1db136b22d0': 'Switcheo',
    'c011a72400e58ecd99ee497cf89e3775d4bd732f': 'Synthetix',
    'ffc91f7088bf40f0419b451fb9d85718d8903628': 'Synthetix',
    'c011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f': 'Synthetix',
    '94a1b5cdb22c43faab4abeb5c74999895464ddaf': 'Tornado.cash',
    '12d66f87a04a9e220743712ce6d9bb1b5616b8fc': 'Tornado.cash',
    'cd2053679de3bcf2b7e2c2efb6b499c57701222c': 'Totle',
    '77208a6000691e440026bed1b178ef4661d37426': 'Totle',
    '3e532e6222afe9bcf02dcb87216802c75d5113ae': 'UMA',
    'c0a47dfe034b400b47bdad5fecda2621de6c4d95': 'Uniswap',
    '2c4bd064b998838076fa341a83d007fc2fa50957': 'Uniswap',
    '09cabec1ead1c0ba254b09efb3ee13841712be14': 'Uniswap',
    '22d8432cc7aa4f8712a655fc4cdfb1baec29fca9': 'Uniswap',
    'f173214c720f58e03e194085b1db28b50acdeead': 'Uniswap',
    '2157a7894439191e520825fe9399ab8655e0f708': 'Uniswap',
    '5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f': 'Uniswap',
    'c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': 'Wrapped ETH',
    '0e2298e3b3390e3b945a5456fbf59ecc3f55da16': 'Yam Finance',
    '9d25057e62939d3408406975ad75ffe834da4cdd': 'yearn.finance',
    '16de59092dae5ccf4a1e6439d611fd0653f0bd01': 'yearn.finance'
  }
  return names[address.lower()] if address.lower() in names else 'Other'
