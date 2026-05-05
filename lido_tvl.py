#准备工作
import requests#把requests工具从python里面给我拿出来
from web3 import Web3#把web3工具从web3库里给我拿出来
import json#把json工具从python里面给我拿出来，用来读写json文件，后面要把tvl数据存成历史档案
import os#把os工具从python里面给我拿出来，用来处理文件路径，判断文件是否存在
from datetime import datetime, timezone#从datetime模块拿出来datetime和timezone，前者用来记录时间，后者用来指定UTC时区

#拿到alchemyapi连接主网
alchemy_url="https://eth-mainnet.g.alchemy.com/v2/lZy8XiMppx5tar2jviA0G"#alchemy_url这个是自己定义命名的变量名称，后面的网址是值相当于具体内容。就相当于我要找alchemy这个代理人中间人给我办事，后面网站就是他给我留下的电话号码，我要打这个电话号码才能找到他帮我办事，现在我要去以太坊主网里面查数据，我叫alchemy去帮我找主网大哥查账目，这小子有路子能直接接触到主网大哥，他办好事然后给我反馈数据就可以了，至于他怎么办的我不在意。
w3=Web3(Web3.HTTPProvider(alchemy_url)) #alchemy_url相当于这个是我们这个中间人的电话号码，就是那串网址，为了方便写我们就给他取了名字叫alchemy_url,现在我们用web3.HTTPProvider给这个电话号码打电话找中间人去以太坊干活，Web3（）表示这个过程电话接通了alchemy这个中间人随时待命，我们给这个状态取名叫w3，到时我要叫中间人去主网干活就发w3，随时调动他帮我去以太坊主网干活。

#在主网链上拿到steth代币的总供应量
STETH_ADDRESS="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"#STETH代币的合约部署地址就是后面的十六进制代码，后面代码里输入STETH_ADDRESS就是调用这个合约地址干活。这串地址是在以太坊主网世界里独一无二的steth的身份证号码，身份识别码，你有他就能到庞大的主网里面找到他
ABI = [
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]#ABI相当于是这个合约开发者给外面的人写的一本说明书，方便外面的人用这个说明书直接和合约对话，因为外面的人是不能直接看懂和读写合约的，所以需要借助这个翻译说明书。ABI指令是官方合约创始人规定好了模板和内容的，我们如果要调用直接就去复制粘贴就能得到你想要的数据。而且erc20协议的代币都有totalsupply这个ABI通用指令来查询总供应量。所以这里我们直接调用就好了
contract=w3.eth.contract(address=STETH_ADDRESS,abi=ABI)#等号左边这个contract相当于给这整个状态过程取的名字叫contract，到时方便输入contract就可以随时调用这个状态。w3.eth.contract表示我们随时通过alchemy这个中间人进入主网去干事情，（address=STETH_ADDRESS,abi=ABI)表示我们去找到身份证号（合约代码）对应上的这个人，然后用能让他听得懂的指令ABI来拿到我们的信息。整个过程就是去主网找到币的合约拿到总供应量过程
total_supply=contract.functions.totalSupply().call()#等号左边的total_supply是定义的查总供应量的函数名字，方便后面引用不会看起来很长一坨。contract属于一个大菜单表示整个智能合约，包含了function整个功能菜单，total_Supply()就是属于功能菜单里面要求调用总供应量的指令，call（）意思是直接执行这个指令拿出结果来，而不只是看结果，而是直接拿结果使用结果。
print(total_supply)#表示直接打印出来这个total_Supply函数执行以后获取的数据结果
total_supply_eth =total_supply/10**18#因为从以太坊上返回的总供应量的数据是按以太坊原生代币的的最小单位计数的，他的单位是wei。因为1eth=1018wei，所以我们要除以1018就知道有多少个steth代币，我们把这个结果的名字定义为total_supply_eth 。
print(total_supply_eth)#输出数据结果的单位就是是用eth计数的eth数量




#在chainlink预言机上拿到eth/usd交易对的最新价格
CHAINLINK_ADDRESS="0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"#这是eth/usd交易对在chainlink预言机上的合约地址，要调用就需要找到他的这串身份证号
ABI_CHAINLINK = [{
    "inputs": [],
    "name": "latestRoundData",
    "outputs": [
        {"internalType": "uint80", "name": "roundId", "type": "uint80"},
        {"internalType": "int256", "name": "answer", "type": "int256"},
        {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
        {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
        {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
    ],
    "stateMutability": "view",
    "type": "function"
}]#这里调用的也是官方给的ABI，使用的latestRoundData这个功能来查询调用eth/usd交易对的现价，这里用usd是使用了法币美元做单位，因为如果选usdt或usdc也可以，但是可能会遇到极端脱钩那种情况，使用直接用法币比较客观
chainlink = w3.eth.contract(address=CHAINLINK_ADDRESS, abi=ABI_CHAINLINK)#同理和上面调用totalsupply功能一样，这里调用最新价格，固定模板就这样写，因为和上面的定义有很多共同使用的如w3.eth.contract一样的变量都是同一个变量多次使用，所以不用重复定义名字就可以直接拿来使用。
data=chainlink.functions.latestRoundData().call()#直接调用官方提供的查询最新价格功能的latestrounddata函数和上面的totalsupply用法类似我就不赘述了，获得的数据变量取名叫data，方便后面使用，实际上会获得五个数据：轮次ID, 价格, 开始时间, 更新时间, 轮次，但是等下我们只需要价格
print(data)#把运行的data函数获得的结果打印出来，可以看到有五个数据,第二个就是价格
eth_price=data[1]/10**8#data[1]表示选择的列表里的第二个数据。因为官方规定，主网上获得的价格需要结果处理，要除以10**8才能拿到平时我们看到的eth价格，主要是以太坊上的数据都是整数，不以小数形式出现，所有都要经过decimal精度换算和前面除以10**18一个原理
print(eth_price)#得到了eth/usd交易对在chainlink预言机上的最新实时价格
#计算tvl_chainlink
tvl_chainlink=eth_price*total_supply_eth#把上面我们在链上通过alchemy拿到的steth的总锁仓量乘以预言机上拿到的eth/usd币对的实时最新价格的积就是tvl_chainlink
print(tvl_chainlink)#打印出来tvl_chainlink的结果就是chainlink预言机计算出来的steth的美元价值



#在pyth预言机上拿到eth/usd交易对的最新价格
PYTH_ADDRESS = "0x4305FB66699C3B2702D4d05CF36551390A4c69C6"#也在pyth预言机上找到eth的价格在主网的合约地址，找到身份证号码为了找他沟通拿数据，这里是在官方网站找到的
ABI_PYTH = [{
    "inputs": [
        {"internalType": "bytes32", "name": "id", "type": "bytes32"}
    ],
    "name": "getPriceUnsafe",
    "outputs": [
        {"components": [
            {"internalType": "int64", "name": "price", "type": "int64"},
            {"internalType": "uint64", "name": "conf", "type": "uint64"},
            {"internalType": "int32", "name": "expo", "type": "int32"},
            {"internalType": "uint256", "name": "publishTime", "type": "uint256"}
        ],
        "internalType": "struct PythStructs.Price",
        "name": "price",
        "type": "tuple"}
    ],
    "stateMutability": "view",
    "type": "function"
}]#依然是调用官方给的ABI指令，getpriceunsafe功能去查询实时价格，但是需要输入eth/usd的feedid，我去官网查了但是官网崩了我直接使用了ai给我的，这一步和chainlink不同，chainlink不用传参数，但是pyth需要输入ETH_USD_ID这个参数才能返回数据拿到价格
ETH_USD_ID = "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"#这个就是ai直接给的ETH_USD_ID地址，等下必须用到
pyth = w3.eth.contract(address=PYTH_ADDRESS, abi=ABI_PYTH)#带上abi用身份证号码找到主网上的合约拿数据，套用上面类似的模板，固定写法，直接调用就好
data = pyth.functions.getPriceUnsafe(ETH_USD_ID).call()#定义拿到返回的数据为data，方便后面引用
print(data)#打印出来pyth合约上eth/usd交易对拿到的没有处理过的数据
eth_price_pyth = data[0] * (10**data[2])#拿到的数据老规矩，[0]就表示列表里面的第一个数据，然后要按他的要求经过精度处理，[2]就是列表里面的第三个数据，表示精度，然后相乘就是拿到处理后的价格
print(eth_price_pyth)#打印出来拿到的价格数据
#计算tvl_pyth
tvl_pyth=eth_price_pyth*total_supply_eth#用pyth预言机拿到的价格乘以我们在主网上拿到的steth锁仓数量的积就是tvl_pyth
print(tvl_pyth)#打印出来tvl_pyth的结果就是pyth预言机计算出来的steth的美元价值




#接下来是查询金库除steth外的其他资产总额
url_llama = "https://api.llama.fi/protocol/lido"#这是直接调用的defillama的lido金库的api，里面存了金库的详细数据，锁仓有哪些代币，每个代币的余额是多少，每个代币的价格是多少，等等。
response = requests.get(url_llama)#调用api拿到数据，把数据存起来以response命名。
data = response.json()#把数据转换为json格式方便python读取，方便后面使用。
tokens_usd = data["tokensInUsd"][-1]["tokens"]#在返回的data数据里面找到“tokeninusd”字段关键字，在这个字段里面[-1]表示defillama拉取的最新的一条价格数据，["tokens"]表示在最新的一条数据里取出锁仓代币价值
print(tokens_usd)#打印出来锁仓代币价值 "拿到的数据其实就是一个字典，就像excel表格里面一一对应的各种数据"

#计算other_tvl_第一种方法
other_tvl_第一种方法 = 0#定义除开了steth以外的其他代币的tvl起始值定义为0，方便后面累加。
for k, v in tokens_usd.items():#用for循环把字典tokens_usd里面一一对应拆开，得到很多组一一对应的key和value。
    if k != "WETH":#如果key不等于WETH，就累加value，因为WETH是steth包裹的，算了就会重复，所以不加。
        other_tvl_第一种方法 += v#累加value，因为value就是代币的价值，所以累加就是累加代币的价值。
print(other_tvl_第一种方法)#打印出来累加的结果

#计算other_tvl_第二种方法
WMATIC_TVL=tokens_usd["WMATIC"]#在锁仓代币价值字典里面找到WMATIC代币的价值，取名叫WMATIC_TVL，方便后面引用。
DOT_TVL=tokens_usd["DOT"]#在锁仓代币价值字典里面找到DOT代币的价值，取名叫DOT_TVL，方便后面引用。
KSM_TVL=tokens_usd["KSM"]#在锁仓代币价值字典里面找到KSM代币的价值，取名叫KSM_TVL，方便后面引用。
SOL_TVL=tokens_usd["SOL"]#在锁仓代币价值字典里面找到SOL代币的价值，取名叫SOL_TVL，方便后面引用。
OTHER_TVL_第二种方法=WMATIC_TVL+DOT_TVL+KSM_TVL+SOL_TVL#除开了steth以外的其他代币的tvl总和
print(OTHER_TVL_第二种方法)#打印出来除开了steth以外的其他代币的tvl总和

#total_tvl_CHAINLINK结果
total_tvl_CHAINLINK=tvl_chainlink+OTHER_TVL_第二种方法#参考预言机为chainlink得出的总锁仓量
print(total_tvl_CHAINLINK)#打印出来的结果

#total_tvl_pyth结果
total_tvl_pyth=tvl_pyth+OTHER_TVL_第二种方法#参考预言机为pyth得出的总锁仓量
print(total_tvl_pyth)#打印出来的结果



#在defillama的api上拿到总锁仓量作为参考对比 
url_llama = "https://api.llama.fi/protocol/lido"
response = requests.get(url_llama)
data = response.json()
llama_tvl = data["tvl"][-1]["totalLiquidityUSD"]




#下面的print模板是固定的，print(f"命名"(命名的附加说明)：{拿到的变量数据结果}")   后面的:,表示加千分位逗号     .2f表示保留两位小数     f表示按小数格式输出
print("========== 最终结果 ==========")   
print(f"ETH价格（Chainlink）: ${eth_price}")
print(f"ETH价格（Pyth）: ${eth_price_pyth}")
print(f"stETH TVL（Chainlink）: ${tvl_chainlink:,.2f}")
print(f"stETH TVL（Pyth）: ${tvl_pyth:,.2f}")
print(f"其他代币TVL: ${OTHER_TVL_第二种方法:,.2f}")
print(f"总TVL（Chainlink）: ${total_tvl_CHAINLINK:,.2f}")
print(f"总TVL（Pyth）: ${total_tvl_pyth:,.2f}")
print(f"DefiLlama官方api总TVL: ${llama_tvl:,.2f}")



# =====================================================================
# 保存本次运行数据到历史档案文件 tvl_history.json
#
# 这就像每天早上跑完脚本后，把今天的结果抄进日记本里存档。
# 之后可以翻开日记本，对比不同日期的数据，分析趋势变化。
# =====================================================================

# 定义历史档案文件的路径，存放在和本脚本同一个文件夹里
# os.path.dirname(__file__) 表示"当前这个脚本所在的文件夹"
# os.path.join 把文件夹路径和文件名拼在一起，变成完整路径
history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tvl_history.json")

# 获取当前时间，格式化成 "年-月-日 时:分:秒" 的字符串
# datetime.now(timezone.utc) 拿到当前的 UTC 时间（不带时区偏差，全球统一标准时间）
# .strftime("%Y-%m-%d %H:%M:%S") 把时间格式化成人类可读的字符串，比如 "2026-04-15 08:00:00"
current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# 把本次运行的所有关键数据打包成一个字典
# 这样历史文件里的每条记录格式统一，方便后续做 AI 分析或画图
current_record = {
    "timestamp":             current_time,                          # 记录时间（UTC）
    "eth_price_chainlink":   round(eth_price,              2),      # Chainlink ETH 价格，保留2位小数
    "eth_price_pyth":        round(eth_price_pyth,         2),      # Pyth ETH 价格，保留2位小数
    "steth_supply_eth":      round(total_supply_eth,       4),      # stETH 总供应量（ETH单位），保留4位小数
    "steth_tvl_chainlink":   round(tvl_chainlink,          2),      # stETH 的 TVL（Chainlink 版），保留2位小数
    "steth_tvl_pyth":        round(tvl_pyth,               2),      # stETH 的 TVL（Pyth 版），保留2位小数
    "other_tvl":             round(OTHER_TVL_第二种方法,    2),      # 其他代币 TVL，保留2位小数
    "total_tvl_chainlink":   round(total_tvl_CHAINLINK,    2),      # 总 TVL（Chainlink 版），保留2位小数
    "total_tvl_pyth":        round(total_tvl_pyth,         2),      # 总 TVL（Pyth 版），保留2位小数
    "llama_tvl":             round(llama_tvl,              2)       # DefiLlama 官方 TVL，保留2位小数
}

# 检查历史文件是否已经存在
# 如果存在（比如已经运行过好几天了），就把旧数据读出来，追加今天的新数据，再写回去
# 如果不存在（第一次运行），就直接创建文件，把今天的数据存进去
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        all_records = json.load(f)  # 读取已有的全部历史记录，是一个列表
    all_records.append(current_record)  # 把今天的新记录追加到列表末尾，就像把新日记写在最后一页
else:
    all_records = [current_record]  # 文件不存在，新建一个列表，第一条就是今天的记录

# 把更新后的完整记录列表写回文件
# indent=4 让 JSON 文件有漂亮的缩进，打开文件一眼就能看懂结构
# ensure_ascii=False 让中文字符直接保存，而不是被转成 \uXXXX 乱码形式
with open(history_file, "w", encoding="utf-8") as f:
    json.dump(all_records, f, indent=4, ensure_ascii=False)

# 告知用户数据已经成功保存，并告诉他文件在哪里
print(f"\n📁 本次数据已保存到历史档案：{history_file}")
print(f"   当前记录时间：{current_time} UTC")
print(f"   历史档案共有 {len(all_records)} 条记录")
