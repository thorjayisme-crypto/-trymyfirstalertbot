#准备工作
import requests#把requests工具从python里面给我拿出来，后面要用它处理网络请求，是给常用工具。
from web3 import Web3#把web3工具从web3库里给我拿出来，后面要用它连接以太坊主网，是web3编程常用工具。

import json#把json翻译官工具从python里拿出来，用来把python得到的数据翻译成文本文件储存起来，也可以把文本文件翻译成可以让python直接使用的数据。
import os#把os工具从python里拿出来，用来直接和计算机系统交流的工具，在生成数据的时候用于判断存放数据的文件是否存在，判断以后引导后续逻辑操作，这是把关人。
from datetime import datetime, timedelta#把datetime工具从datetime工具箱里拿出来，用来获取实时时间。timedelta是时间差计算工具，配合时间戳查找历史数据。
from openai import OpenAI#把openai工具从openai库里拿出来，后面要用它调用gpt的api接口，是引入gpt到脚本工作的常用工具。

#拿到alchemyapi连接主网
alchemy_url="https://eth-mainnet.g.alchemy.com/v2/lZy8XiMppx5tar2jviA0G"#alchemy_url这个是自己定义命名的变量名称，后面的网址是值相当于具体内容。就相当于我要找alchemy这个代理人中间人给我办事，后面网站就是他给我留下的电话号码，我要打这个电话号码才能找到他帮我办事，现在我要去以太坊主网里面查数据，我叫alchemy去帮我找主网大哥查账目，这小子有路子能直接接触到主网大哥，他办好事然后给我反馈数据就可以了，至于他怎么办的我不在意。
w3=Web3(Web3.HTTPProvider(alchemy_url)) #alchemy_url相当于这个是我们这个中间人的电话号码，就是那串网址，为了方便写我们就给他取了名字叫alchemy_url,现在我们用web3.HTTPProvider给这个电话号码打电话找中间人去以太坊干活，Web3（）表示这个过程电话接通了alchemy这个中间人随时待命，我们给这个状态取名叫w3，到时我要叫中间人去主网干活就发w3，随时调动他帮我去以太坊主网干活。

#在主网链上拿到steth代币的总供应量
STETH_ADDRESS="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"#STETH代币的合约部署地址就是后面的十六进制代码，后面代码里输入STETH_ADDRESS就是调用这个合约地址干活。这串地址是在以太坊主网世界里独一无二的steth的身份证号码，身份识别码，你有他就能到庞大的主网里面找到他
ABI_connect = [
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]#ABI相当于是这个合约开发者给外面的人写的一本说明书，方便外面的人用这个说明书直接和合约对话，因为外面的人是不能直接看懂和读写合约的，所以需要借助这个翻译说明书。ABI指令是官方合约创始人规定好了模板和内容的，我们如果要调用直接就去复制粘贴就能得到你想要的数据。而且erc20协议的代币都用totalsupply这个ABI通用指令来查询总供应量。所以这里我们直接调用就好了
contract=w3.eth.contract(address=STETH_ADDRESS,abi=ABI_connect)#相当于连接abi这个过程定义为contract，到时方便输入contract就可以随时调用这个状态。w3.eth.contract表示我们随时通过alchemy这个中间人进入主网去干事情，（address=STETH_ADDRESS,abi=ABI_connect)表示我们去找到身份证号（合约代码）对应上的这个人，然后用能让他听得懂的指令ABI来拿到我们的信息。整个过程就是去主网找到币的合约拿到总供应量过程
total_supply=contract.functions.totalSupply().call()#连接好abi以后用total_supply功能执行查总供应量任务，也用total_supply定义查总供应量的函数名字。contract属于一个大菜单表示整个智能合约，包含了function整个功能菜单，total_Supply()就是属于功能菜单里面要求调用总供应量的指令，call（）意思是直接执行这个指令拿出结果来，而不只是看结果，而是直接拿结果使用结果。
print(total_supply)#表示直接打印出来这个total_Supply函数执行以后获取的数据结果
total_supply_eth =total_supply/10**18#因为从以太坊上返回的总供应量的数据是按以太坊原生代币的的最小单位wei计数的，因为1eth=10**18wei，所以我们要除以10**18就知道有多少个steth代币，我们把这个结果的名字定义为total_supply_eth ，方便后面引用。
print(total_supply_eth)#输出数据结果的单位就是是用eth计数的eth数量




#在chainlink预言机上拿到eth/usd交易对的最新实时价格
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
}]#这里调用的也是预言机官方给的ABI，使用的latestRoundData这个功能来查询调用eth/usd交易对的现价，这里用usd是使用了法币美元做单位，因为如果选usdt或usdc也可以，但是可能会遇到稳定币可能极端脱钩那种情况，使用直接用法币比较客观。
chainlink = w3.eth.contract(address=CHAINLINK_ADDRESS, abi=ABI_CHAINLINK)#同理和上面调用totalsupply功能一样，这里调用最新价格，固定模板就这样写，因为和上面的定义有很多共同使用的如w3.eth.contract一样的变量都是同一个变量多次使用，所以不用重复定义名字就可以直接拿来使用。
data=chainlink.functions.latestRoundData().call()#直接调用官方提供的查询最新价格功能的latestrounddata函数和上面的totalsupply用法类似我就不赘述了，获得的数据变量取名叫data，方便后面使用，实际上会获得五个数据：轮次ID, 价格, 开始时间, 更新时间, 轮次，但是等下我们只需要价格
print(data)#把运行的data函数获得的结果打印出来，可以看到有五个数据,第二个就是价格
eth_price_chainlink=data[1]/10**8#data[1]表示选择的列表里的第二个数据。因为官方规定，主网上获得的价格需要结果处理，要除以10**8才能拿到平时我们看到的eth价格，主要是以太坊上的数据都是整数，不以小数形式出现，所有都要经过decimal精度换算和前面除以10**18一个原理
print(eth_price_chainlink)#得到了eth/usd交易对在chainlink预言机上的最新实时价格
#计算tvl_chainlink
steth_tvl_chainlink=eth_price_chainlink*total_supply_eth#把上面我们在链上通过alchemy拿到的steth的总锁仓量*预言机上拿到的eth/usd币对的实时最新价格的积就是tvl_chainlink
print(steth_tvl_chainlink)#打印出来tvl_chainlink的结果就是chainlink预言机计算出来的steth的美元价值总额，就是所谓tvl。



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
}]#依然是调用官方给的ABI指令，pyth预言机用getpriceunsafe功能去查询实时价格，但是需要输入eth/usd的feedid，我去官网查了但是官网崩了我直接使用了ai给我的，这一步和chainlink不同，chainlink不用传参数，但是pyth需要输入ETH_USD_ID这个参数才能返回数据拿到价格
ETH_USD_ID = "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"#这个就是ai直接给的ETH_USD_ID地址，等下必须用到
pyth = w3.eth.contract(address=PYTH_ADDRESS, abi=ABI_PYTH)#带上abi用身份证号码找到主网上的合约拿数据，套用上面类似的模板，固定写法，直接调用就好
data = pyth.functions.getPriceUnsafe(ETH_USD_ID).call()#定义拿到返回的数据为data，方便后面引用
print(data)#打印出来pyth合约上eth/usd交易对拿到的没有处理过的数据
eth_price_pyth = data[0] * (10**data[2])#拿到的数据老规矩，[0]就表示列表里面的第一个数据，然后要按他的要求经过精度处理，[2]就是列表里面的第三个数据，表示精度，然后相乘就是拿到处理后的价格
print(eth_price_pyth)#打印出来拿到的价格数据
#计算tvl_pyth
steth_tvl_pyth=eth_price_pyth*total_supply_eth#用pyth预言机拿到的价格乘以我们在主网上拿到的steth锁仓数量的积就是tvl_pyth
print(steth_tvl_pyth)#打印出来tvl_pyth的结果就是pyth预言机计算出来的steth的美元价值总额，就是所谓tvl。




#接下来是查询金库除steth外的其他资产总额获取过程
url_llama = "https://api.llama.fi/protocol/lido"#这是直接调用的defillama的lido金库的api，里面存了金库的详细数据，锁仓有哪些代币，每个代币的余额是多少，每个代币的价格是多少，可以拿到金库的详细数据，方便大家直接调取数据。
response = requests.get(url_llama)#用requests工具调用网址api拿到数据，把数据存起来以response命名，这个过程就是请求过程，response就是拿到的回应表示调取到的数据结果。
data = response.json()#把上面调取到的数据通过json工具转换成json格式让python读取，这个转换好的json格式的数据用data命名变量。
tokens_usd = data["tokensInUsd"][-1]["tokens"]#在返回的转换好的data数据里面找到“tokeninusd”字段关键字，在这个字段里面[-1]表示defillama拉取的最新的一条价格数据，["tokens"]表示在最新的一条数据里取出锁仓代币价值，这一步就是拿到了金库的详细数据。
print(tokens_usd)#打印出来lido金库里面所有锁仓代币分别的价值 ，拿到的数据结构是一个字典，字典里面是很多组一一对应的数据，是这种格式：{'WETH': 168433641.52, 'USDC': 110231981.14, 'USDT': 108325417.26, 'WBTC': 3331058.46, 'WMATIC': 13113611.53, 'DOT': 330385.56, 'KSM': 253242.32, 'SOL': 210154.31}

#计算other_tvl_第一种方法，weth就是steth包裹的eth，所以不算，其他代币都算。这种做法就是把字典里面排除weth以后的属于所有代币的价值用for/in循环把剩余所有代币的价值都累加起来。这个办法最开始我没太明白但是后来搞清楚了来龙去脉。
other_tvl_第一种方法 = 0#定义除开了steth以外的其他代币的tvl起始值定义为0，方便后面累加。
for k, v in tokens_usd.items():#用for循环把字典tokens_usd里面一一对应拆开，得到很多组一一对应的key和value。
    if k != "WETH":#如果key不等于WETH，就累加value，因为WETH是steth包裹的，算了就会重复，所以不加。
        other_tvl_第一种方法 += v#累加value，因为value就是代币的价值，所以累加就是累加代币的价值。
print(other_tvl_第一种方法)#打印出来累加的结果

#计算other_tvl_第二种方法，这种做法就是直接在字典里面找到WMATIC、DOT、KSM、SOL代币的价值，然后相加就是除开了steth以外的其他代币的tvl总和。这个办法是最简单最直观的做法，但是缺点是不够智能，如果金库里新增加了代币，这个办法就不行了，需要手动修改代码。
WMATIC_TVL=tokens_usd["WMATIC"]#在锁仓代币价值字典里面找到WMATIC代币的价值，取名叫WMATIC_TVL，方便后面引用。
DOT_TVL=tokens_usd["DOT"]#在锁仓代币价值字典里面找到DOT代币的价值，取名叫DOT_TVL，方便后面引用。
KSM_TVL=tokens_usd["KSM"]#在锁仓代币价值字典里面找到KSM代币的价值，取名叫KSM_TVL，方便后面引用。
SOL_TVL=tokens_usd["SOL"]#在锁仓代币价值字典里面找到SOL代币的价值，取名叫SOL_TVL，方便后面引用。
other_tvl_第二种方法=WMATIC_TVL+DOT_TVL+KSM_TVL+SOL_TVL#除开了steth以外的其他代币的tvl总和
print(other_tvl_第二种方法)#打印出来除开了steth以外的其他代币的tvl总和

#total_tvl_CHAINLINK结果
total_tvl_CHAINLINK=steth_tvl_chainlink+other_tvl_第一种方法#参考预言机为chainlink得出的总锁仓量
print(total_tvl_CHAINLINK)#打印出来的结果

#total_tvl_pyth结果
total_tvl_pyth=steth_tvl_pyth+other_tvl_第一种方法#参考预言机为pyth得出的总锁仓量
print(total_tvl_pyth)#打印出来的结果



#在defillama的api上拿到金库里所有锁仓代币的总锁仓量作为与上面两种方法计算的参考对比 
url_llama = "https://api.llama.fi/protocol/lido"
response = requests.get(url_llama)
data = response.json()
Defillama_tvl = data["tvl"][-1]["totalLiquidityUSD"]




#下面的print模板是固定的，print(f"命名"(命名的附加说明)：{拿到的变量数据结果}")   后面的:,表示加千分位逗号     .2f表示保留两位小数     f表示按小数格式输出
print("========== 最终结果 ==========")   
print(f"ETH价格（Chainlink）: ${eth_price_chainlink}")
print(f"ETH价格（Pyth）: ${eth_price_pyth}")
print(f"stETH TVL（Chainlink）: ${steth_tvl_chainlink:,.2f}")
print(f"stETH TVL（Pyth）: ${steth_tvl_pyth:,.2f}")
print(f"其他代币TVL: ${other_tvl_第一种方法:,.2f}")
print(f"总TVL（Chainlink）: ${total_tvl_CHAINLINK:,.2f}")
print(f"总TVL（Pyth）: ${total_tvl_pyth:,.2f}")
print(f"DefiLlama官方api总TVL: ${Defillama_tvl:,.2f}")



#以下是第二阶段代码

now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")#用now命名获取现在这个时间的变量，用datetime工具拿到的实时时间，拿到的数据我们要求转换为以年月日时分秒格式。
hour = datetime.now().hour#获取当前具体小时，后面进行每个小时数据记录和日环比分析时需要用到。
weekday = datetime.now().weekday()#获取当前具体是星期几，后面进行周报分析需要用到。

record={
    "timestamp": now,
    "eth_price_chainlink": eth_price_chainlink,
    "eth_price_pyth": eth_price_pyth,
    "steth_supply_eth": total_supply_eth,
    "steth_tvl_chainlink": steth_tvl_chainlink,
    "steth_tvl_pyth": steth_tvl_pyth,
    "other_tvl": other_tvl_第一种方法,
    "total_tvl_chainlink": total_tvl_CHAINLINK,
    "total_tvl_pyth": total_tvl_pyth,
    "Defillama_tvl": Defillama_tvl
}#把本次运行的数据按固定格式把所需的变量组合打包形成一个字典，后续需要引用这个字典，字典用record命名。

#下面是记录每小时实时数据数据的代码。先判断有没有已经存储了历史记录数据的文件，然后再根据有无文件的逻辑判断执行不同的写入数据的命令。
filename = "C:/Users/86554/Desktop/CODING/lido_tvl_history.json"#先规定我们名字叫lido_tvl_history.json这个json文件需要在规定的这个文件路径里面，它是用于记录每个小时的实时数据的文本文件。先规定文件在硬盘里储存的位置。
if os.path.exists(filename):#现在开始条件判断，通过os工具找对应路径里是否存在这个文件，如果已经存在了，那么就执行下面的with open命令打开这个文件。现在通过os工具直接去电脑硬盘找这个文件。
    with open(filename,"r",encoding="utf-8") as file:#那么就用r只读的形式，utf-8的编码方式去识别读取这个filename文件里面的数据，然后把都文件这个过程用file命名。现在找到这个文件了，现在用只读的方式读取这个硬盘里面的文件，然后把这个文件里面的数据搬到内存等待加工，把这个搬运的操作称为file。
        history=json.load(file)#现在用json翻译官去执行file里面内容读取翻译任务，因为python不能直接读取json格式文件的数据，需要用json在中间先充当翻译官先翻译，然后把经过json翻译过的，能够直接让python读取的这些数据命名为history变量。现在搬运到内存里面待加工的数据是json格式，python不能直接读取加工，需要用json工具把这些数据翻译成python可以自己读取的列表。
else:#否则（指没有满足if上述条件判断，也就是要求对应的路径里没有这个文件，也意味着我们这个程序没运行过，这次是第一次运行。）
    history=[]#那么现在就定义一个空列表取名叫history，后面的运行数据都放到这个空列表里面。没有在硬盘里找到这个文件，就直接在内存里面创建一个空列表。

history.append(record)#把本次运行形成的数据按照record字典要求的格式写入到history列表里面，append表示放到最后接上。如果已经有这个json文件的存在里面有历史数据，就把这次运行的数据加到被翻译过后的列表里面（现在还是在内存中操作）。如果没有历史数据存在，直接就在内存里这个空列表里写入这次运行的数据。

with open(filename,"w",encoding="utf-8") as file:#用这个命令打开filename位置里的对应文件，命令这个文件是w可写入形式，用file命名这个要写入数据的状态，把改动以后的经过内存里加工后的history文件写进回硬盘里面。现在已经在内存里面加工好了这个列表，现在需要把加工好的列表写入到硬盘里面。
    json.dump(history,file,ensure_ascii=False,indent=2)#现在把上面已经加入了这次运行数据后的history列表用json翻译官翻译过的数据写回到json脚本里面去。ensure_ascii=False表示不使用ascii编码,直接使用中文形式，indent=2表示每个数据之间缩进两个空格，方便阅读。现在把已经加工好的列表用json工具翻译成可以写入到硬盘的json格式，然后写回到硬盘里面 。
print(f"数据已经保存到{filename}文件里面，记录时间:{now}")#提示每个小时整点记录的数据已经保存到对应位置了。


#以下是分析修改过的历史数据的过程，从lido_tvl_history.json文件里面读取包括本次运行以后写入的最新数据。
with open("C:/Users/86554/Desktop/CODING/lido_tvl_history.json","r",encoding="utf-8") as file:#打开路径里面存的这个脚本，以只读方式打开，这个状态称为file文件。到硬盘里面找到刚刚修改过更新过数据的这个文件，然后用只读的方式把里面的数据搬运到内存里。
    history1=json.load(file)#用json翻译官把file文件里读取的数据翻译上传给python使用,python读取到已经更新过的这个文件的过程定义为history1，为了和上面的没修改过数据的history变量区分。把搬运到内存里的数据用json工具把源json格式翻译成python可以直接读取的列表形式，然后等待内存里面加工待用，这里为了和上面区别，命名一个history1。
latest=history1[-1]#用latest定义最新的一条数据，就是本次运行获取的数据，用于下面每小时打印当前实时数据时引用。现在内存里的经过翻译的列表，找到最新的一条数据，用latest命名。

print(f"""
==============================
////Lido 小时数据记录////

时间：{latest["timestamp"]}

$Chainlink数据$
ETH价格：${latest["eth_price_chainlink"]:.2f}
总TVL：${latest["total_tvl_chainlink"]:,.2f}

$Pyth数据$
ETH价格：${latest["eth_price_pyth"]:.2f}
总TVL：${latest["total_tvl_pyth"]:,.2f}

$Defillama数据$
总TVL：${latest["Defillama_tvl"]:,.2f}
==============================
""")#打印反馈的每个小时的最新实时数据，用latest拿到本次运行的最新数据，时间，eth价格，总锁仓量，defillama总锁仓量。


#以下创建以早晨八点为基准的日环比变化数据的变量备用，以change命名，方便后面gpt分析数据时引用。
target_today_8am=datetime.now().replace(hour=8,minute=0,second=0,microsecond=0)#我们现在需要定位一个理想时间点，我们规定为今天早上八点整，因为datetime.now()获取到的时间是年月日带时分秒的，但是实际上我们只想取今天的年月日，所以后面我们用八点整把现在拿到的时间替换了，目的是为了要今天日期的和八点整这两个时间点，因为不能写死了，所以后面用replace工具把现在拿到的时间替换成我们理想的时间点。这个今天的理想时间点用target_today_8am命名。
today_real_8am=min(history1,key=lambda r:abs((datetime.strptime(r["timestamp"],"%Y-%m-%d %H:%M:%S")-target_today_8am).total_seconds()))#因为在实际过程中，可能实际记录不可能每次都正好是在八点整这个时间点记录数据，所以这里面我们使用了min函数，后面表示在history1这个列表里寻找离理想时间点八点整最近的这条记录，用today_8am命名，方便后面日环比分析引用。后面是规定的计算方式，用时间差计算为标准，用abs函数取绝对值，因为时间差可能是正数也可能是负数，我们只关心差值，不关心方向。

target_yesterday_8am=(datetime.now()-timedelta(days=1)).replace(hour=8,minute=0,second=0,microsecond=0)#用datetime.now()获取到现在的日期时间，然后用timedelta往前推一天，然后把时间强制改为八点整，这个昨天的理想时间点用target_yesterday_8am命名。
yesterday_real_8am=min(history1,key=lambda r:abs((datetime.strptime(r["timestamp"],"%Y-%m-%d %H:%M:%S")-target_yesterday_8am).total_seconds()))#找到列表里离昨天理想时间点时间差最少的那条记录，用yesterday_real_8am命名，方便后面日环比分析引用。

#chainlink数据的变化分析
eth_change_chainlink_real_8am=today_real_8am["eth_price_chainlink"]-yesterday_real_8am["eth_price_chainlink"]#用eth_change_chainlink_am定义今天和昨天早上8点的eth价格差。
eth_change_chainlink_percentage_real_8am=eth_change_chainlink_real_8am/yesterday_real_8am["eth_price_chainlink"]*100#用eth_change_chainlink_percentage_am定义今天和昨天早上8点的eth价格差占昨天eth价格变化的百分比。

tvl_change_chainlink_real_8am=today_real_8am["total_tvl_chainlink"]-yesterday_real_8am["total_tvl_chainlink"]#用tvl_change_chainlink定义今天和昨天早上8点的总锁仓量差。
tvl_change_chainlink_percentage_real_8am=tvl_change_chainlink_real_8am/yesterday_real_8am["total_tvl_chainlink"]*100#用tvl_change_chainlink_percentage_am定义今天和昨天早上8点的总锁仓量差占昨天总锁仓量变化的百分比。

#pyth数据的变化分析
eth_change_pyth_real_8am=today_real_8am["eth_price_pyth"]-yesterday_real_8am["eth_price_pyth"]#用eth_change_pyth_am定义今天和昨天早上8点的eth价格差。
eth_change_pyth_percentage_real_8am=eth_change_pyth_real_8am/yesterday_real_8am["eth_price_pyth"]*100#用eth_change_pyth_percentage_am定义今天和昨天早上8点的eth价格差占昨天eth价格变化的百分比。

tvl_change_pyth_real_8am=today_real_8am["total_tvl_pyth"]-yesterday_real_8am["total_tvl_pyth"]#用tvl_change_pyth_am定义今天和昨天早上8点的总锁仓量差。
tvl_change_pyth_percentage_real_8am=tvl_change_pyth_real_8am/yesterday_real_8am["total_tvl_pyth"]*100#用tvl_change_pyth_percentage_am定义今天和昨天早上8点的总锁仓量差占昨天总锁仓量变化的百分比。

#defillama数据的变化分析
defillama_change_tvl_real_8am=today_real_8am["Defillama_tvl"]-yesterday_real_8am["Defillama_tvl"]#用defillama_change_tvl_am定义今天和昨天早上8点的总锁仓量差。
defillama_change_tvl_percentage_real_8am=defillama_change_tvl_real_8am/yesterday_real_8am["Defillama_tvl"]*100#用defillama_change_tvl_percentage_8am定义今天和昨天早上8点的总锁仓量差占昨天总锁仓量变化的百分比。


#以下是AI分析日环比过程的代码
if hour == 8:#如果现在的时间是早上八点整，那么就执行下面的代码。
    print("现在是早上八点，进行日环比分析")
    report_text = f"""
////Lido 日报 - 日环比分析////

参考时间昨天:{yesterday_real_8am["timestamp"]}                                                              
参考时间今天:{today_real_8am["timestamp"]}
$chainlink数据的分析$
ETH价格变化:${yesterday_real_8am["eth_price_chainlink"]:.2f} -> ${today_real_8am["eth_price_chainlink"]:.2f}
价差和百分百变化:{eth_change_chainlink_real_8am} //// ({eth_change_chainlink_percentage_real_8am:.2f}%)
总锁仓量变化:${yesterday_real_8am["total_tvl_chainlink"]:.2f} -> ${today_real_8am["total_tvl_chainlink"]:.2f}
价差和百分百变化:{tvl_change_chainlink_real_8am} //// ({tvl_change_chainlink_percentage_real_8am:.2f}%)

$pyth数据的分析$
ETH价格变化:${yesterday_real_8am["eth_price_pyth"]:.2f} -> ${today_real_8am["eth_price_pyth"]:.2f}
价差和百分百变化:{eth_change_pyth_real_8am} //// ({eth_change_pyth_percentage_real_8am:.2f}%)
总锁仓量变化:${yesterday_real_8am["total_tvl_pyth"]:.2f} -> ${today_real_8am["total_tvl_pyth"]:.2f}
价差和百分百变化:{tvl_change_pyth_real_8am} //// ({tvl_change_pyth_percentage_real_8am:.2f}%)

$defillama数据的分析$
总锁仓量变化:${yesterday_real_8am["Defillama_tvl"]:.2f} -> ${today_real_8am["Defillama_tvl"]:.2f}
价差和百分百变化:{defillama_change_tvl_real_8am} //// ({defillama_change_tvl_percentage_real_8am:.2f}%)
"""
    print(report_text)

#日环比分析gpt的调用过程
    client = OpenAI(
    api_key="sk-4e006feb80254c3bb7023aeb15e7dca5",#api密钥
    base_url="https://right.codes/codex/v1"#中转站地址
)
    gpt_response = client.chat.completions.create(#这是去拿gpt回答答案的过程。按照路径一步一步调用gpt5.5的功能，client是与gpt建立对话，chat是要求和它对话，completions是要求gpt对话中执行续写功能，create（）就是带入下面的具体数据，创建一次对话请求，就是请求做一下这个事情，整个过程状态用gpt_response命名，方便后面引用。）
        model="gpt-5.5",
        messages=[#system对应的是你要求gpt成为的角色，给gpt定的角色要求。user是给自己定的角色，表示用户使用者，content里面便是所谓的prompt，引导词ai发的命令
            {"role": "system", 
            "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
            {"role": "user", 
            "content": f"""{report_text}                                    
以下是Lido协议的日环比变化数据，请你分析这些数据，并给出结论：                                    
1. 分析ETH价格和tvl的变化情况
2. ETH价格的涨跌是否带动了TVL同向变化
3. 如果价格涨但TVL跌，或者价格跌但TVL涨，说明了什么
4. 给出资金流动的风险提示
5. 判断变化是正常波动还是异常信号
"""}
        ]
    )#这几个括号就表示又内到外把函数公式一一对应运行关闭，和excel里的嵌套函数是一个原理。
    print(gpt_response.choices[0].message.content)#gpt会返回很多条数据回来，但实际上我们只需要他回答的内容就好。chioces[0]表示这些回答数据的列表字典里取第一个回答，message是选择这个回答要求的字段，content是选择这个回答的完整内容。print出来就是gpt返回的回答内容。
#
# 以下是把通过gpt分析的日环比变化数据存到对应json文件的代码。
    gpt_daily_result = gpt_response.choices[0].message.content#把gpt运行返回的回答用gpt_daily_result命名。
    daily_result_filename = "C:/Users/86554/Desktop/CODING/lido_daily_analysis.json"#规定日环比分析数据记录的文件位置。

    if os.path.exists(daily_result_filename):#这里开始条件判断，通过os工具找到如果运行脚本的文件夹已经存在daily_result_filename这个文件，那么就执行下面一行的with open命令打开这个文件。
        with open(daily_result_filename, "r", encoding="utf-8") as file:#用只读命令把硬盘里这个文件存储的数据搬运到内存里。
            daily_history = json.load(file)#把搬到内存里的数据用json工具翻译成可以让python可以读取的列表。
    else:#否则，指里面没有这个文件，可能是第一次运行。
        daily_history = []#现在就在内存里创建一个叫daily_history的空列表。
    daily_history.append({#把本次运行形成的record字典打包好的文本文件写入到daily_history这个列表里面。如果已经有数据就把本次数据写进翻译过后的列表的后面，如果没有数据，就直接写进空列表当第一个数据。
        "timestamp": today_real_8am["timestamp"],
        "report": report_text,
        "gpt_analysis": gpt_daily_result
    })#指的是在内存里用这个方式写入修改列表里的数据。

    with open(daily_result_filename, "w", encoding="utf-8") as file:#现在用可写方式打开硬盘里这个文件，准备把内存里处理好的数据写回硬盘。
        json.dump(daily_history, file, ensure_ascii=False, indent=2)#现在通过json翻译官把内存里加工好的列表翻译成可以写入到硬盘的json格式，然后写回到硬盘里面 。

    print(f"日环比分析已保存到{daily_result_filename}")#提示我们日环比分析已经成功保存到对应位置了。

#下面是gpt分析的周报过程
if hour == 8 and weekday == 6:#如果当前时间正好是早上八点，并且今天是周天，那么就执行下面命令。
    with open("C:/Users/86554/Desktop/CODING/lido_daily_analysis.json", "r", encoding="utf-8") as file:#用只读命令把日报记录文件里面的数据搬到内存里面等待处理。
        daily_history = json.load(file)#在内存里用json翻译官翻译日报里的数据给python读取使用。
    
    week_daily = daily_history[-7:]#用week_daily定义过去七天的每日每条数据，是包含七条数据的一个列表。

    week_report_text = ""#定义一个空字符串，方便后面累加周报内容。
    for day in week_daily:#把week_daily列表里面的每条数据一条一条拆开，每条数据取名为day。
        week_report_text += f"\n{day['report']}\n"#把取的每条数据day里面的report字段对应的数据取出来一条一条的放进week_report_text这个列表里面，可以避免其他杂乱字段的干扰。

#周报分析gpt的调用过程
    client = OpenAI(
    api_key="sk-4e006feb80254c3bb7023aeb15e7dca5",#api密钥
    base_url="https://right.codes/codex/v1"#中转站地址
)
    gpt_week_response = client.chat.completions.create(#与gpt连接的命令，这是去拿gpt回答答案的过程。按照路径一步一步调用gpt5.4的功能，client是与gpt建立对话，chat是要求和它对话，completions是要求gpt对话中执行续写功能，create（）就是带入下面的具体数据，创建一次对话请求，就是请求做一下这个事情，整个过程状态用gpt_week_response命名，方便后面引用。）
        model="gpt-5.4-high",
        messages=[#system对应的是你要求gpt成为的角色，给gpt定的角色要求。user是给自己定的角色，表示用户使用者，content里面便是所谓的prompt，引导词ai发的命令
            {"role": "system",
            "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
            {"role": "user",
            "content": f"""{week_report_text}
以上是Lido协议过去七天的每日数据，请你：
1. 分析这一周ETH价格的整体走势
2. 分析这一周TVL的整体走势
3. 判断资金是整体流入还是流出Lido
4. 判断用户整体是在质押还是赎回stETH
5. 给出本周市场情绪的综合判断
6. 给出下周需要关注的风险点
"""}
        ]
    )#这几个括号就表示又内到外把函数公式一一对应运行关闭，和excel里的嵌套函数是一个原理。

    gpt_week_result = gpt_week_response.choices[0].message.content#把gpt运行返回的回答用gpt_week_result命名，方便后面引用。
    print(gpt_week_result)#打印出来gpt返回的回答内容。

#下面是把gpt分析的周报存入对应json文本的过程
    week_result_filename = "C:/Users/86554/Desktop/CODING/lido_week_analysis.json"#规定周报分析数据存储在硬盘上的路径。

    if os.path.exists(week_result_filename):#这里开始条件判断，如果程序已经运行过，里面有历史数据了，就执行下面步骤。
        with open(week_result_filename, "r", encoding="utf-8") as file:#用只读方式把硬盘里这个文件里存储的数据放到内存里等待加工。
            week_history = json.load(file)#在内存里用json翻译官把数据翻译成python可读的形式待用。
    else:#指没有找到这个对应文件，可能是第一次运行。
        week_history = []#直接在内存里创建一个空列表待用。

    week_history.append({#在内存里把本次运行的新数据按以下格式加到到翻译过的原数据的后面。还是像上面一样分两种情况。
        "timestamp": today_real_8am["timestamp"],
        "week_report": week_report_text,
        "gpt_analysis": gpt_week_result
    })

    with open(week_result_filename, "w", encoding="utf-8") as file:#用可写方式打开硬盘里面储存的文件。
        json.dump(week_history, file, ensure_ascii=False, indent=2)#现在把内存里加工过的文件用json翻译官翻译回json格式写回到硬盘中去。

    print(f"周报分析已保存到{week_result_filename}")#提示我们周报已经成功保存到对应位置了。 

#以下以周数据为例进行不同引导词的对比测试
    prompts={#创建字典，把引导词名称和具体引导内容打包成一个字典，方便后面引用。
   "严格数据派" : f"""{week_report_text}
以下是Lido协议本周数据，请你：
1. 只基于数据说话，不要主观猜测
2. 找出本周最异常的一天，说明原因
3. 用一句话总结本周最重要的信号
""",
    "风险预警派" : f"""{week_report_text}
以下是Lido协议本周数据，请你扮演一个风控经理：
1. 找出所有潜在的风险信号
2. 判断资金是否在大规模流出
3. TVL下降是否已经达到警戒线
4. 给出1-10分的风险评级，并说明理由
5. 如果你是大户，看到这些数据你会怎么操作
"""
}
    for name,prompt_content in prompts.items():#prompts.items()是把上面我们定义的prompts字典拆开，拆开成为引导词名称（key）对应name变量，引导词内容（value）对应prompt_content变量，这里学了新知识，in后面是两个变量for后面也可以接两个变量，分别对应key和value。
        print(f"\n{'='*30}")#\n表示换行，'='*30表示30个等号，方便后面打印出来分割线。
        print(f"【{name}】的分析结果")#打印出来引导词名称
        print(f"{'='*30}")#打印出来分割线
        gpt_response = client.chat.completions.create(#按照路径一步一步调用gpt5.5的功能，client是建立对话，chat是选择和他对话功能，completions是对话续写功能，create（）就是带入下面的具体数据，创建一次对话请求，就是请求做一下这个事情，整个过程状态用gpt_response命名，方便后面引用。）
            model="gpt-5.5",
            messages=[
                {"role": "system",
                "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
                {"role": "user",
                "content": prompt_content}#这里prompt_content是可以变的变量，区别上面我们定死了引导内容，这里是根据不同的引导词名称，调用不同的引导内容。加了prompt前缀是为了和上面messages字典里的"content"键名区分，避免阅读时混淆。
            ]
        )
        print(gpt_response.choices[0].message.content)#gpt会返回很多条回答数据，chioces[0]表示这些回答数据的列表字典里取第一个回答，message是选择这个回答要求的字段，content是选择这个回答的完整内容。print出来就是gpt返回的回答内容。
