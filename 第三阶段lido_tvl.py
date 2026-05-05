#准备工作
import requests#把requests工具从python里面给我拿出来，后面要用它处理网络请求，是给常用工具。
from web3 import Web3#把web3工具从web3库里给我拿出来，后面要用它连接以太坊主网，是web3编程常用工具。

import json#把json翻译官工具从python里拿出来，用来把python得到的数据翻译成json格式的文本文件储存起来，也可以把json格式的里的文本文件翻译成可以让python直接使用的数据。
import os#把os工具从python里拿出来，用来直接和计算机系统交流的工具，在生成数据的时候用于判断所需要存放数据的文件是否存在在指定路径，判断以后引导后续逻辑操作。
from datetime import datetime#把datetime工具从datetime工具箱里拿出来，用来获取所需要的实时时间。

from openai import OpenAI#把OpenAi工具从openai库里拿出来，待会儿调用chatgpt相关的功能都需要它。

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
eth_price_chainlink=data[1]/10**8#data[1]表示选择的列表里的第二个数据。因为官方规定，主网上获得的价格需要结果处理，要除以10**8才能拿到平时我们看到的eth价格，主要是以太坊上的数据都是整数，不以小数形式出现，所有都要经过decimal精度换算和前面除以10**18一个原理
print(eth_price_chainlink)#得到了eth/usd交易对在chainlink预言机上的最新实时价格
#计算tvl_chainlink
tvl_chainlink=eth_price_chainlink*total_supply_eth#把上面我们在链上通过alchemy拿到的steth的总锁仓量乘以预言机上拿到的eth/usd币对的实时最新价格的积就是tvl_chainlink
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
Defillama_tvl = data["tvl"][-1]["totalLiquidityUSD"]




#下面的print模板是固定的，print(f"命名"(命名的附加说明)：{拿到的变量数据结果}")   后面的:,表示加千分位逗号     .2f表示保留两位小数     f表示按小数格式输出
print("========== 最终结果 ==========")   
print(f"ETH价格（Chainlink）: ${eth_price_chainlink}")
print(f"ETH价格（Pyth）: ${eth_price_pyth}")
print(f"stETH TVL（Chainlink）: ${tvl_chainlink:,.2f}")
print(f"stETH TVL（Pyth）: ${tvl_pyth:,.2f}")
print(f"其他代币TVL: ${OTHER_TVL_第二种方法:,.2f}")
print(f"总TVL（Chainlink）: ${total_tvl_CHAINLINK:,.2f}")
print(f"总TVL（Pyth）: ${total_tvl_pyth:,.2f}")
print(f"DefiLlama官方api总TVL: ${Defillama_tvl:,.2f}")



#以下是用于记录生成所需的变量数据的代码
now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")#这个相当于时间戳代码，把前面datetime工具拿到的实时时间从数据转化成所需的标准格式的时间文本，再方便记录，用now命名这个变量来方便后面引用。
record={
    "timestamp": now,
    "eth_price_chainlink": eth_price_chainlink,
    "eth_price_pyth": eth_price_pyth,
    "steth_supply_eth": total_supply_eth,
    "steth_tvl_chainlink": tvl_chainlink,
    "steth_tvl_pyth": tvl_pyth,
    "other_tvl": OTHER_TVL_第二种方法,
    "total_tvl_chainlink": total_tvl_CHAINLINK,
    "total_tvl_pyth": total_tvl_pyth,
    "Defillama_tvl": Defillama_tvl
}
#上面的record相当于把需要记录的变量数据按固定格式打包成一个字典，相当于把这次得到的散乱的数据按固定格式整理起来存入字典方便后面引用，尤其要注意的是这里记录的是本次运行获取的数据打包成字典，而不是历史数据打包成字典。

#判断有没有已经获取的历史记录数据存储文件，然后执行写入数据的命令。
filename = "C:/Users/86554/Desktop/CODING/lido_tvl_history.json"#创建一个名字叫lido_tvl_history.json的文本文件来储存数据，放到我脚本运行的这个路径里面，这些数据记录文件用filename命名，后面可以方便引用。这个文件是用来记录每次运行脚本获得的数据的。
if os.path.exists(filename):#这里开始条件判断，通过os工具找到如果运行脚本的文件夹已经存在filename这个文件，那么就执行下面一行的with open命令打开这个文件。
    with open(filename,"r",encoding="utf-8") as file:#那么就用r只读的形式，utf-8的编码方式去识别读取这个filename文件里面的数据，然后把读取到的这些数据称为file变量，方便后面引用。
        history=json.load(file)#用json翻译官把file文件里面读取到的文本数据用json翻译上传给python使用，给这些已经翻译过的数据python可以直接用的数据的变量取名叫history，方便后面引用。
else:#否则（指没有满足if上述条件判断，也就是没有这个文件的存在）
    history=[]#指没有这个文件的存在，就相当于没运行过这个脚本，以前没有历史记录。现在就建一个空列表，方便后续数据后面记录进去，这个变量取名叫history，方便后面引用。
history.append(record)#把本次运行形成的record字典打包好的文本文件写入到history这个列表里面。如果已经有数据就接着写入到上一次数据的后面，如果没数据就写入文件当第一个数据。
with open(filename,"w",encoding="utf-8") as file:#用这个命令打开filename文件，命令这个文件是w可写入形式，write可以读取的基础上还可以修改写入数据。现在把这个状态也叫做file，方便后续引用。
    json.dump(history,file,ensure_ascii=False,indent=2)#现在把上面已经修改过的history列表打包好的文件用json翻译官翻译成为json文本文件记录起来写进file文件里面，ensure_ascii=False表示不使用ascii编码,直接使用中文形式，indent=2表示每个数据之间缩进两个空格，方便阅读。

print(f"数据已经保存到{filename}文件里面，记录时间:{now}")#老规矩，格式为f"key"{对应"value"的值}

#以下是分析修改过的历史数据的过程。
with open("C:/Users/86554/Desktop/CODING/lido_tvl_history.json","r",encoding="utf-8") as file:#打开路径里面存的这个脚本，以只读方式打开，这个状态称为file文件
    history1=json.load(file)#用json翻译官把file文件里读取的数据翻译上传给python使用,python读取到已经更新过的这个文件的过程定义为history1，为了和上面的history变量区分。

today=history1[-1]#用today定义最新的一条数据，就是说这次运行获取的数据。-1表示获取的是当前一条最新数据。
yesterday=history1[-2]#用yesterday定义倒数第二条数据就是，上一次运行获取的数据。-2表示获取的是当前倒数第二条数据。

#以下创建数据分析的变量，以change命名，方便后面gpt分析数据时引用。
#chainlink数据的变化分析
eth_change_chainlink=today["eth_price_chainlink"]-yesterday["eth_price_chainlink"]#用eth_change_chainlink定义今天和昨天的eth价格差，方便后面引用。today["eth_price_chainlink"]其实等价于history1[-1]["eth_price_chainlink"]，只是省略简写了。
eth_change_chainlink_percentage=eth_change_chainlink/yesterday["eth_price_chainlink"]*100#用eth_change_chainlink_percentage定义今天和昨天的eth价格差占昨天eth价格的百分比，方便后面引用。

tvl_change_chainlink=today["total_tvl_chainlink"]-yesterday["total_tvl_chainlink"]#用tvl_change_chainlink定义今天和昨天的总锁仓量差，方便后面引用。
tvl_change_chainlink_percentage=tvl_change_chainlink/yesterday["total_tvl_chainlink"]*100#用tvl_change_chainlink_percentage定义今天和昨天的总锁仓量差占昨天总锁仓量的百分比，方便后面引用。

#pyth数据的变化分析
eth_change_pyth=today["eth_price_pyth"]-yesterday["eth_price_pyth"]#用eth_change_pyth定义今天和昨天的eth价格差，方便后面引用。
eth_change_pyth_percentage=eth_change_pyth/yesterday["eth_price_pyth"]*100#用eth_change_pyth_percentage定义今天和昨天的eth价格差占昨天eth价格的百分比，方便后面引用。

tvl_change_pyth=today["total_tvl_pyth"]-yesterday["total_tvl_pyth"]#用tvl_change_pyth定义今天和昨天的总锁仓量差，方便后面引用。
tvl_change_pyth_percentage=tvl_change_pyth/yesterday["total_tvl_pyth"]*100#用tvl_change_pyth_percentage定义今天和昨天的总锁仓量差占昨天总锁仓量的百分比，方便后面引用。

#defillama数据的变化分析
defillama_change_tvl=today["Defillama_tvl"]-yesterday["Defillama_tvl"]#用defillama_change_tvl定义今天和昨天的总锁仓量差，方便后面引用。
defillama_change_tvl_percentage=defillama_change_tvl/yesterday["Defillama_tvl"]*100#用defillama_change_tvl_percentage定义今天和昨天的总锁仓量差占昨天总锁仓量的百分比，方便后面引用。

#资金异动预警
警戒线=5#可以用中文当变量名字
if abs(tvl_change_chainlink_percentage)>警戒线:#引用前面的现有变量数据作为if判定条件，tvl变化比率涨幅跌幅超过百分之五都报警。
    print(f"⚠️ 警告：TVL单日变化超过{警戒线}%，请注意资金异动风险！")#打印预警信号
    print(f"本次变化幅度：{tvl_change_chainlink_percentage:.2f}%")#打印具体预警涨跌幅
else: print(f"✅ TVL变化正常：{tvl_change_chainlink_percentage:.2f}%")#反馈情况正常

#调用Lido官方API拿到APR
url_lido_apr="https://eth-api.lido.fi/v1/protocol/steth/apr/last"#去官网找到直接调取steth的APY接口
response_lido_apr=requests.get(url_lido_apr)#用requests工具去请求这个接口，请求到的数据称为response_lido_apy，方便后面引用。和查询金库除steth外的其他资产总额异曲同工。
data_lido_apr=response_lido_apr.json()#把api请求得到的返回数据用json格式翻译给python读取，这些被翻译过的数据取名data_lido_apy变量。
print(data_lido_apr)#打印出api返回回来的数据
lido_apr=data_lido_apr["data"]["apr"]#在返回的数据里提取data字段，取出里面的apy对应的值。
print(f"lido官方apr：{lido_apr}%")#打印出来具体apy数据反馈给我们。
apr = lido_apr / 100  # 转成小数
apy = ((1 + apr / 365) ** 365 - 1) * 100
print(f"换算后APY：{apy:.4f}%")

#通过链上合约读取APY
w3 = Web3(Web3.HTTPProvider("https://eth-mainnet.g.alchemy.com/v2/lZy8XiMppx5tar2jviA0G"))#用http协议连接以太坊主网，使用alchemy的api密钥。
lido_address = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"#lido金库合约地址
latest_blcok=w3.eth.block_number#获取现在最新的区块号
event_signature="0x"+w3.keccak(text="TokenRebased(uint256,uint256,uint256,uint256,uint256,uint256,uint256)").hex()#因为steth是每天复利的，这个tokenrebase就是复利操作的记录事件，直接去官方提取的固定格式。这里相当于是去拿rebase复利这个操作的哈希身份证，以太坊只认身份证不认单词。
print(event_signature)#拿到的这个事件的hash身份证为"0xff08c3ef606d198e316ef5b822193c489965899eb4e3c248cea1a4626c3eda50"。
flock_block=latest_blcok-50000#从现在的区块号往前推50000个区块，因为rebase复利操作是每天一次，所以往前推50000个区块大约就是7天时间所生成的所有记录 。
logs=w3.eth.get_logs({#用get_logs函数去获取从flock_block到latest_blcok之间的所有rebase复利操作的记录。
    "fromBlock": flock_block,
    "toBlock": latest_blcok,
    "address": lido_address,
    "topics": [event_signature]
})
print(len(logs))#看拿到了几条rebase复利操作的记录。
print(logs[0])#把里面的第一条打印出来。

from eth_abi import decode#使用eth_abi实现解码功能
decoded=decode(
    ["uint256","uint256","uint256","uint256","uint256","uint256"],
    logs[0]["data"]
)
print(decoded)#打印出按固定格式解码后的内容结果。
results = []#定义一个空列表，后面要把其他数据一起放进来。

for log in logs:#用for/in循环按一下格式解码对于的7条数据。
    decoded = decode(
        ["uint256","uint256","uint256","uint256","uint256","uint256"],
        log["data"]
    )
    
    block_timestamp = int(log["blockTimestamp"], 16)#把时间戳从16进制转换为10进制
    post_total_ether = decoded[4]#取出第5个数字，就是rebase后的ETH总量
    
    results.append({#把解码后的数据存入results列表中。
        "timestamp": block_timestamp,
        "tvl_eth": post_total_ether / 1e18
    })

for r in results:#把results列表中的每一条数据称为r，方便后面引用。
    print(r)#打印每一条数据。
    #解码rebase数据计算APY
last_log = logs[-1]#取出logs列表中的最后一条数据，方便后面引用。

#解码data字段，每32字节一个参数
data = last_log["data"]#等价于last_log[-1]["data"]
values = [int.from_bytes(data[i:i+32], "big") for i in range(0, len(data), 32)]#把data字段中的每32字节转换为10进制，存入values列表中。
#steth的复利以share记，share总量不变，但是share price会变化，因为share price是总ETH量除以总份额。利润就通过share price的变化来计算。
timeElapsed      = values[0]#隔了多少秒进行一次复利操作。
preTotalShares   = values[1]#rebase前的总份额
preTotalEther    = values[2]#rebase前的总ETH量
postTotalShares  = values[3]#rebase后的总份额
postTotalEther   = values[4]#rebase后的总ETH量
sharesMintedAsFees = values[5]#rebase过程中产生的手续费

#计算share price，share就是自动升值的入股份额，share price增加就是分红复利的效果。
pre_share_price  = preTotalEther / preTotalShares#rebase前的share price
post_share_price = postTotalEther / postTotalShares#rebase后的share price

#计算APR然后转APY
apr = (post_share_price - pre_share_price) / pre_share_price * (365 * 24 * 3600 / timeElapsed)#计算APR，公式为（rebase后的share price - rebase前的share price）/ rebase前的share price * (365 * 24 * 3600 / timeElapsed)
apy = ((1 + apr / 365) ** 365 - 1) * 100

print(f"timeElapsed：{timeElapsed}秒")
print(f"pre share price：{pre_share_price}")
print(f"post share price：{post_share_price}")
print(f"APR：{apr*100:.4f}%")
print(f"APY：{apy:.4f}%")



#以下是用gpt分析x上有关lido情绪的推文实现代码
client = OpenAI(#老规矩还是用的中转站的gpt接口
    api_key="sk-4e006feb80254c3bb7023aeb15e7dca5",
    base_url="https://right.codes/codex/v1"
)

# 定义取推文的函数
def fetch_lido_tweets():#定义这个去6551接口取推文过程的函数叫fetch_lido_tweets
    headers = {#这是请求头，相当于先出示我们的通行证，表明我有进6551接口拿数据的权限。
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ29vZ2xlXzEwNjUwMzcwMDgxMzUxOTQ3OTc5OCIsIm5vbmNlIjoiMDAyOWZlMjYtOWIxZS00Nzg1LTllZDUtYTY5ZmViNzU2ZjBkIiwianRpIjoiNjBkYTMxNmItYjAxNi00MmIxLThjZDItMGI2ZGQ1YzA1MDhmIn0.aNfHRE0zr6kdYpMA4zq2fJdiWtwNewwWIJOzxZRnLfw",
        "Content-Type": "application/json"#数据内容我们要求用json文本格式取回。
    }
    response = requests.post(#开始了拿数据这个工作，带着请求头用requests工具去6551的接口url拿，关键字是lido/LDO，取最新的100条推文。
        "https://ai.6551.io/open/twitter_search",
        headers=headers,
        json={
            "keywords": "Lido LDO",
            "maxResults": 100,
            "product": "Latest"
        }
    )
    if response.status_code == 200:#如果拿到的数据里面的返回码是200，表示拿数据成功。
        return response.json().get("data", [])#把拿到的数据用json格式翻译给python读取，然后把拿到的这些数据打包成列表返回，如果拿到的数据里面没有内容，也返回成一个空列表备用，这个拿数据的过程就是调取的fetch_lido_tweets()函数。
    else:
        return []#如果拿到的数据里面的返回码不是200，表示拿数据失败。就返回一个空列表，这个拿数据的过程就是调取的fetch_lido_tweets()函数。

# 定义分析推文的函数
def analyze_lido_sentiment():#定义用gpt分析推文情绪的过程的函数。
    tweets = fetch_lido_tweets()#tweets代表上面fetch_lido_tweets()函数拿到的数据，然后用tweets命名这个变量。是一个列表。
    if tweets == []:#如果这个函数拿到的数据没有内容，列表是空的。
        return "无法获取推文"#就打印反馈这个信息
    else:
        列表 = []#定义一个新的空列表，方便后面把推文内容放进来。
        for t in tweets:#指的是函数获取的列表有内容的有数据的列表情况下，我们用for/in循环把列表里面的每条推文数据定义为t，下面针对列表里的每个t轮流进行操作，实行相同程序步骤。
            line = f"- [{t['userScreenName']}] {t['text'][:500]}"#把每条推文t里面的数据处理成[用户名][具体内容][推文前500个字]的形式。
            列表.append(line)#把处理的推文一条一条加的我们前面新建的这个空列表里面
        tweet_texts = "\n".join(列表)#把列表按每一条自动换行的形式排列起来，存入tweet_texts变量，方便后面引用。

        response = client.chat.completions.create(#这是去拿gpt回答答案的过程。按照路径一步一步调用gpt5.4的功能，client是与gpt建立对话，chat是要求和它对话，completions是要求gpt对话中执行续写功能，create（）就是带入下面的具体数据，创建一次对话请求，就是请求做一下这个事情，整个过程状态用response命名，方便后面引用。）
            model="gpt-5.5",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个DeFi市场分析师，专门分析Lido协议的市场情绪。"
                },
                {
                    "role": "user",
                    "content": f"""以下是最新的Lido/LDO相关推文，请分析：

{tweet_texts}

请给出：
1. 整体情绪（看涨/看跌/中性）
2. 主要讨论话题
3. 值得关注的信号
4. 综合评分（1-10）"""
                }
            ]
        )
        return response.choices[0].message.content#gpt会返回很多条回答数据，chioces[0]表示这些回答数据的列表字典里取第一个回答，message是选择这个回答要求的字段，content是选择这个回答的完整内容。return出来就是gpt返回的回答内容。这里用return是因为这个函数最后要返回这个回答内容，方便后面引用。

# 启动程序
result = analyze_lido_sentiment()#result代表上面analyze_lido_sentiment()函数拿到的数据，然后用result命名这个变量。
print(result)#打印出来这个result变量，也就是gpt返回的回答内容。

#引入openai分析
weekday=datetime.now().weekday()#用datetime工具获取今天是星期几，获取到的结果定义为weekday，方便后面引用。
client = OpenAI(
    api_key="sk-4e006feb80254c3bb7023aeb15e7dca5",#api密钥
    base_url="https://right.codes/codex/v1"#中转站地址
)

if weekday==0:#==表示逻辑判断，0表示判断现在是不是周一
    print("今天是周一，只统计数据，不进行分析")#输出的通知内容
elif weekday==6:#elif表示否则如果，表示现在不是周一，而是周六。
    week_data=history1[-7:]#取出来history1列表里面的倒数第一到倒数第七条数据，存入week_data变量，方便后面引用。
    print(f"今天是周天，进行周报总结")#输出的通知内容
    week_report = ""#定义一个空字符串，方便后面累加周报内容。
    for day in week_data:#for循环遍历week_data列表里面的每一条数据，把每一条数据称为day，方便后面引用。
        week_report += f"""
日期：{day["timestamp"]}
ETH价格（Chainlink）：${day["eth_price_chainlink"]:.2f}
总锁仓量（Chainlink）：${day["total_tvl_chainlink"]:,.2f}
DefiLlama总锁仓量：${day["Defillama_tvl"]:,.2f}
"""
#上面是把一周七天的数据以固定格式用for/in循环一条一条累加起来，存入week_report变量。
    print(week_report)#打印出来一周七天的所有数据，这是给我看运行生成的数据，也是要发给gpt分析的数据内容。
    gpt_response = client.chat.completions.create(#这是去拿gpt回答答案的过程。按照路径一步一步调用gpt5.4的功能，client是与gpt建立对话，chat是要求和它对话，completions是要求gpt对话中执行续写功能，create（）就是带入下面的具体数据，创建一次对话请求，就是请求做一下这个事情，整个过程状态用gpt_response命名，方便后面引用。）
           model="gpt-5.5",
        messages=[##system对应的是你要求gpt成为的角色，给gpt定的角色要求。user是给自己定的角色，表示用户使用者，content里面便是所谓的prompt，引导词ai发的命令。
            {"role": "system",
            "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
            {"role": "user",
            "content": f"""{week_report}
以下是Lido协议本周数据，请你：
1. 分析本��ETH价格和总锁仓量的整体趋势
2. 判断是否有异常信号
3. 预测下周行情
4. 分析TVL的增减是否意味着有大量资金在流入或流出Lido
5. 判断现在用户是在质押还是在赎回stETH
6. 给出资金流动的风险提示
7. ETH价格的涨跌是否带动了TVL同向变化
8. 如果价格涨但TVL跌，或者价格跌但TVL涨，说明了什么
9. 给出目前市场情绪的判断
"""}
        ]
    )#这几个括号就表示又内到外把函数公式一一对应运行关闭，和excel里的嵌套函数是一个原理。
    print(gpt_response.choices[0].message.content)#gpt会返回很多条回答数据，chioces[0]表示这些回答数据的列表字典里取第一个回答，message是选择这个回答要求的字段，content是选择这个回答的完整内容。print出来就是gpt返回的回答内容。

#以下以周数据为例进行不同引导词的对比测试
    prompts={#创建字典，把引导词名称和具体引导内容打包成一个字典，方便后面引用。
   "严格数据派" : f"""{week_report}
以下是Lido协议本周数据，请你：
1. 只基于数据说话，不要主观猜测
2. 找出本周最异常的一天，说明原因
3. 计算本周TVL平均值和波动幅度
4. ETH价格和TVL的相关性分析
5. 用一句话总结本周最重要的信号
""",
    "风险预警派" : f"""{week_report}
以下是Lido协议本周数据，请你扮演一个风控经理：
1. 找出所有潜在的风险信号
2. 判断资金是否在大规模流出
3. TVL下降是否已经达到警戒线
4. 给出1-10分的风险评级，并说明理由
5. 如果你是大户，看到这些数据你会怎么操作
""",
    "交易员派" : f"""{week_report}
以下是Lido协议本周数据，请你扮演一个链上数据交易员：
1. 判断目前是积累阶段还是派发阶段
2. 大资金是在进场还是在离场
3. 下周ETH价格的支撑位和压力位在哪里
4. 现在是应该质押还是赎回stETH
5. 给出明确的操作建议，不要模糊回答
""",
    "简洁总结派" : f"""{week_report}
以下是Lido协议本周数据，请用最简洁的方式：
1. 用三个关键词概括本周行情
2. 本周最重要的一件事是什么
3. 下周最需要关注的一个指标是什么
4. 一句话给出操作建议
"""
}
    for 名字,内容 in prompts.items():#prompts.items()是把上面我们定义的prompts字典拆开，拆开成为引导词名称（key）和引导词内容（value），这里学了新知识，in后面是两个变量for后面也可以接两个变量，分别对应key和value。
        print(f"\n{'='*30}")#\n表示换行，'='*30表示30个等号，方便后面打印出来分割线。
        print(f"【{名字}】的分析结果")#打印出来引导词名称
        print(f"{'='*30}")#打印出来分割线
        gpt_response = client.chat.completions.create(#按照路径一步一步调用gpt5.4的功能，client是建立对话，chat是选择和他对话功能，completions是对话续写功能，create（）就是带入下面的具体数据，创建一次对话请求，就是请求做一下这个事情，整个过程状态用gpt_response命名，方便后面引用。）
            model="gpt-5.4-high",
            messages=[
                {"role": "system",
                "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
                {"role": "user",
                "content": 内容}#这里内容是可以变的变量，区别上面我们定死了引导内容，这里是根据不同的引导词名称，调用不同的引导内容。
            ]
        )
    print(gpt_response.choices[0].message.content)#gpt会返回很多条回答数据，chioces[0]表示这些回答数据的列表字典里取第一个回答，message是选择这个回答要求的字段，content是选择这个回答的完整内容。print出来就是gpt返回的回答内容。

else:#指的是即便不是周一也不是周六，而是周二到周五的任意一天的情况。
    print("今天是工作日，进行日环比分析")#输出的通知内容
    report_text = f"""
////Lido 日报 - 日环比分析////

参考时间昨天:{yesterday["timestamp"]}                                                              
参考时间今天:{today["timestamp"]}
$chainlink数据的分析$
ETH价格变化:${yesterday["eth_price_chainlink"]:.2f} -> ${today["eth_price_chainlink"]:.2f}
价差和百分百变化:{eth_change_chainlink} //// ({eth_change_chainlink_percentage:.2f}%)
总锁仓量变化:${yesterday["total_tvl_chainlink"]:.2f} -> ${today["total_tvl_chainlink"]:.2f}
价差和百分百变化:{tvl_change_chainlink} //// ({tvl_change_chainlink_percentage:.2f}%)

$pyth数据的分析$
ETH价格变化:${yesterday["eth_price_pyth"]:.2f} -> ${today["eth_price_pyth"]:.2f}
价差和百分百变化:{eth_change_pyth} //// ({eth_change_pyth_percentage:.2f}%)
总锁仓量变化:${yesterday["total_tvl_pyth"]:.2f} -> ${today["total_tvl_pyth"]:.2f}
价差和百分百变化:{tvl_change_pyth} //// ({tvl_change_pyth_percentage:.2f}%)

$defillama数据的分析$
总锁仓量变化:${yesterday["Defillama_tvl"]:.2f} -> ${today["Defillama_tvl"]:.2f}
价差和百分百变化:{defillama_change_tvl} //// ({defillama_change_tvl_percentage:.2f}%)
"""
#用以上格式和对应数据生成的结果。
    print(report_text)#打印出当天的数据通知给我看。

    gpt_response = client.chat.completions.create(#按照路径一步一步调用gpt5.4的功能，client是建立对话，chat是选择和他对话功能，completions是对话续写功能，create（）就是带入下面的具体数据，创建一次对话请求，就是请求做一下这个事情，整个过程状态用gpt_response命名，方便后面引用。
        model="gpt-5.5",#选用的模型型号
        messages=[#system对应的是你要求gpt成为的角色，给gpt定的角色要求。user是给自己定的角色，表示用户使用者。
        {"role": "system", 
        "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
        {"role": "user", 
        "content": f"""{report_text}                                    
    以下是Lido协议的日环比数据，请你：                                    
1. 分析ETH价格和总锁仓量的变化情况
2. 判断变化是正常波动还是异常信号
3. 给出简短的市场解读
4. 分析TVL的增减是否意味着有大量资金在流入或流出Lido
5. 判断现在用户是在质押还是在赎回stETH
6. 给出资金流动的风险提示
7. ETH价格的涨跌是否带动了TVL同向变化
8. 如果价格涨但TVL跌，或者价格跌但TVL涨，说明了什么
9. 给出目前市场情绪的判断
"""         }
        ]
    )#这几个括号就表示又内到外把函数公式一一对应运行关闭，和excel里的嵌套函数是一个原理。
    print(gpt_response.choices[0].message.content)#gpt会返回很多条回答数据，chioces[0]表示这些回答数据的列表字典里取第一个回答，message是选择这个回答要求的字段，content是选择这个回答的完整内容。print出来就是gpt返回的回答内容。

