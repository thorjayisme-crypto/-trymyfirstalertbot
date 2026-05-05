#准备工作
import requests
from web3 import Web3
import json
import os
from datetime import datetime
from openai import OpenAI

#拿到alchemyapi连接主网
alchemy_url="https://eth-mainnet.g.alchemy.com/v2/lZy8XiMppx5tar2jviA0G"
w3=Web3(Web3.HTTPProvider(alchemy_url))

#在主网链上拿到steth代币的总供应量
STETH_ADDRESS="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
ABI = [
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]
contract=w3.eth.contract(address=STETH_ADDRESS,abi=ABI)
total_supply=contract.functions.totalSupply().call()
print(total_supply)
total_supply_eth =total_supply/10**18
print(total_supply_eth)

#在chainlink预言机上拿到eth/usd交易对的最新价格
CHAINLINK_ADDRESS="0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"
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
}]
chainlink = w3.eth.contract(address=CHAINLINK_ADDRESS, abi=ABI_CHAINLINK)
data=chainlink.functions.latestRoundData().call()
print(data)
eth_price_chainlink=data[1]/10**8
print(eth_price_chainlink)
tvl_chainlink=eth_price_chainlink*total_supply_eth
print(tvl_chainlink)

#在pyth预言机上拿到eth/usd交易对的最新价格
PYTH_ADDRESS = "0x4305FB66699C3B2702D4d05CF36551390A4c69C6"
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
}]
ETH_USD_ID = "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"
pyth = w3.eth.contract(address=PYTH_ADDRESS, abi=ABI_PYTH)
data = pyth.functions.getPriceUnsafe(ETH_USD_ID).call()
print(data)
eth_price_pyth = data[0] * (10**data[2])
print(eth_price_pyth)
tvl_pyth=eth_price_pyth*total_supply_eth
print(tvl_pyth)

#接下来是查询金库除steth外的其他资产总额
url_llama = "https://api.llama.fi/protocol/lido"
response = requests.get(url_llama)
data = response.json()
tokens_usd = data["tokensInUsd"][-1]["tokens"]
print(tokens_usd)

#计算other_tvl_第一种方法
other_tvl_第一种方法 = 0
for k, v in tokens_usd.items():
    if k != "WETH":
        other_tvl_第一种方法 += v
print(other_tvl_第一种方法)

#计算other_tvl_第二种方法
WMATIC_TVL=tokens_usd["WMATIC"]
DOT_TVL=tokens_usd["DOT"]
KSM_TVL=tokens_usd["KSM"]
SOL_TVL=tokens_usd["SOL"]
OTHER_TVL_第二种方法=WMATIC_TVL+DOT_TVL+KSM_TVL+SOL_TVL
print(OTHER_TVL_第二种方法)

#total_tvl_CHAINLINK结果
total_tvl_CHAINLINK=tvl_chainlink+OTHER_TVL_第二种方法
print(total_tvl_CHAINLINK)

#total_tvl_pyth结果
total_tvl_pyth=tvl_pyth+OTHER_TVL_第二种方法
print(total_tvl_pyth)

#在defillama的api上拿到总锁仓量作为参考对比
url_llama = "https://api.llama.fi/protocol/lido"
response = requests.get(url_llama)
data = response.json()
Defillama_tvl = data["tvl"][-1]["totalLiquidityUSD"]

print("========== 最终结果 ==========")
print(f"ETH价格（Chainlink）: ${eth_price_chainlink}")
print(f"ETH价格（Pyth）: ${eth_price_pyth}")
print(f"stETH TVL（Chainlink）: ${tvl_chainlink:,.2f}")
print(f"stETH TVL（Pyth）: ${tvl_pyth:,.2f}")
print(f"���他代币TVL: ${OTHER_TVL_第二种方法:,.2f}")
print(f"总TVL（Chainlink）: ${total_tvl_CHAINLINK:,.2f}")
print(f"总TVL（Pyth）: ${total_tvl_pyth:,.2f}")
print(f"DefiLlama官方api总TVL: ${Defillama_tvl:,.2f}")

#以下是用于记录生成所需的变量数据的代码
now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

filename = "C:/Users/86554/Desktop/CODING/lido_tvl_history.json"
if os.path.exists(filename):
    with open(filename,"r",encoding="utf-8") as file:
        history=json.load(file)
else:
    history=[]
history.append(record)
with open(filename,"w",encoding="utf-8") as file:
    json.dump(history,file,ensure_ascii=False,indent=2)

print(f"数据已经保存到{filename}文件里面，记录时间:{now}")

#以下是分析修改过的历史数据的过程
with open("C:/Users/86554/Desktop/CODING/lido_tvl_history.json","r",encoding="utf-8") as file:
    history1=json.load(file)

today=history1[-1]

#========== 小时预警 ==========

#预警1：Chainlink vs Pyth 价格对比
价格警戒线 = 0.5
价格偏差 = abs(eth_price_chainlink - eth_price_pyth) / eth_price_chainlink * 100
if 价格偏差 > 价格警戒线:
    print(f"⚠️ 价格预警：Chainlink和Pyth价格偏差{价格偏差:.2f}%，超过{价格警戒线}%警戒线！")
    print(f"Chainlink: ${eth_price_chainlink:.2f}  Pyth: ${eth_price_pyth:.2f}")
else:
    print(f"✅ 价格正常：两源偏差{价格偏差:.2f}%")

#预警2：三个TVL来源对比
tvl警戒线 = 1
tvl最大值 = max(total_tvl_CHAINLINK, total_tvl_pyth, Defillama_tvl)
tvl最小值 = min(total_tvl_CHAINLINK, total_tvl_pyth, Defillama_tvl)
tvl偏差 = (tvl最大值 - tvl最小值) / tvl最小值 * 100
if tvl偏差 > tvl警戒线:
    print(f"⚠️ TVL预警：三个数据源偏差{tvl偏差:.2f}%，超过{tvl警戒线}%警戒线！")
    print(f"Chainlink: ${total_tvl_CHAINLINK:,.2f}  Pyth: ${total_tvl_pyth:,.2f}  DefiLlama: ${Defillama_tvl:,.2f}")
else:
    print(f"✅ TVL正常：三源偏差{tvl偏差:.2f}%")

#调用Lido官方API拿到APR
url_lido_apr="https://eth-api.lido.fi/v1/protocol/steth/apr/last"
response_lido_apr=requests.get(url_lido_apr)
data_lido_apr=response_lido_apr.json()
print(data_lido_apr)
lido_apr=data_lido_apr["data"]["apr"]
print(f"lido官方apr：{lido_apr}%")
apr = lido_apr / 100
apy = ((1 + apr / 365) ** 365 - 1) * 100
print(f"换算后APY：{apy:.4f}%")

#通过链上合约读取APR
w3 = Web3(Web3.HTTPProvider("https://eth-mainnet.g.alchemy.com/v2/lZy8XiMppx5tar2jviA0G"))
lido_address = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
latest_blcok=w3.eth.block_number
event_signature="0x"+w3.keccak(text="TokenRebased(uint256,uint256,uint256,uint256,uint256,uint256,uint256)").hex()
print(event_signature)
flock_block=latest_blcok-50000
logs=w3.eth.get_logs({
    "fromBlock": flock_block,
    "toBlock": latest_blcok,
    "address": lido_address,
    "topics": [event_signature]
})
print(len(logs))
print(logs[0])

from eth_abi import decode
decoded=decode(
    ["uint256","uint256","uint256","uint256","uint256","uint256"],
    logs[0]["data"]
)
print(decoded)
results = []

for log in logs:
    decoded = decode(
        ["uint256","uint256","uint256","uint256","uint256","uint256"],
        log["data"]
    )
    block_timestamp = int(log["blockTimestamp"], 16)
    post_total_ether = decoded[4]
    results.append({
        "timestamp": block_timestamp,
        "tvl_eth": post_total_ether / 1e18
    })

for r in results:
    print(r)

last_log = logs[-1]
data = last_log["data"]
values = [int.from_bytes(data[i:i+32], "big") for i in range(0, len(data), 32)]
timeElapsed      = values[0]
preTotalShares   = values[1]
preTotalEther    = values[2]
postTotalShares  = values[3]
postTotalEther   = values[4]
sharesMintedAsFees = values[5]
pre_share_price  = preTotalEther / preTotalShares
post_share_price = postTotalEther / postTotalShares
apr = (post_share_price - pre_share_price) / pre_share_price * (365 * 24 * 3600 / timeElapsed)
apy = ((1 + apr / 365) ** 365 - 1) * 100

print(f"timeElapsed：{timeElapsed}秒")
print(f"pre share price：{pre_share_price}")
print(f"post share price：{post_share_price}")
print(f"APR：{apr*100:.4f}%")
print(f"APY：{apy:.4f}%")

#预警3：官方API和链上计算APR对比
apr警戒线 = 0.5
apr_onchain = apr * 100
apr偏差 = abs(lido_apr - apr_onchain)
if apr偏差 > apr警戒线:
    print(f"⚠️ APR预警：官方API和链上计算偏差{apr偏差:.4f}%，超过{apr警戒线}%警戒线！")
    print(f"官方API APR: {lido_apr:.4f}%  链上计算APR: {apr_onchain:.4f}%")
else:
    print(f"✅ APR正常：两源偏差{apr偏差:.4f}%")

#以下是用gpt分析x上有关lido情绪的推文实现代码
client = OpenAI(
    api_key="sk-4e006feb80254c3bb7023aeb15e7dca5",
    base_url="https://right.codes/codex/v1"
)

def fetch_lido_tweets():
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ29vZ2xlXzEwNjUwMzcwMDgxMzUxOTQ3OTc5OCIsIm5vbmNlIjoiMDAyOWZlMjYtOWIxZS00Nzg1LTllZDUtYTY5ZmViNzU2ZjBkIiwianRpIjoiNjBkYTMxNmItYjAxNi00MmIxLThjZDItMGI2ZGQ1YzA1MDhmIn0.aNfHRE0zr6kdYpMA4zq2fJdiWtwNewwWIJOzxZRnLfw",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://ai.6551.io/open/twitter_search",
        headers=headers,
        json={
            "keywords": "Lido LDO",
            "maxResults": 100,
            "product": "Latest"
        }
    )
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []

def analyze_lido_sentiment():
    tweets = fetch_lido_tweets()
    if tweets == []:
        return "无法获取推文"
    else:
        列表 = []
        for t in tweets:
            line = f"- [{t['userScreenName']}] {t['text'][:500]}"
            列表.append(line)
        tweet_texts = "\n".join(列表)
        response = client.chat.completions.create(
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
        return response.choices[0].message.content

#========== 时间判断，控制日报和周报 ==========
weekday = datetime.now().weekday()
hour = datetime.now().hour

if hour == 8:
    print("现在是早上8点，进行日环比分析")

    yesterday = history1[-2]

    #chainlink数据的变化分析
    eth_change_chainlink = today["eth_price_chainlink"] - yesterday["eth_price_chainlink"]
    eth_change_chainlink_percentage = eth_change_chainlink / yesterday["eth_price_chainlink"] * 100
    tvl_change_chainlink = today["total_tvl_chainlink"] - yesterday["total_tvl_chainlink"]
    tvl_change_chainlink_percentage = tvl_change_chainlink / yesterday["total_tvl_chainlink"] * 100

    #pyth数据的变化分析
    eth_change_pyth = today["eth_price_pyth"] - yesterday["eth_price_pyth"]
    eth_change_pyth_percentage = eth_change_pyth / yesterday["eth_price_pyth"] * 100
    tvl_change_pyth = today["total_tvl_pyth"] - yesterday["total_tvl_pyth"]
    tvl_change_pyth_percentage = tvl_change_pyth / yesterday["total_tvl_pyth"] * 100

    #defillama数据的变化分析
    defillama_change_tvl = today["Defillama_tvl"] - yesterday["Defillama_tvl"]
    defillama_change_tvl_percentage = defillama_change_tvl / yesterday["Defillama_tvl"] * 100

    #推特舆论情绪分析
    result = analyze_lido_sentiment()
    print(result)

    #日报
    report_text = f"""
////Lido 日报 - 日环比分析////

参考时间昨天:{yesterday["timestamp"]}
参考时间今天:{today["timestamp"]}

$chainlink数据的分析$
ETH价格变化:${yesterday["eth_price_chainlink"]:.2f} -> ${today["eth_price_chainlink"]:.2f}
价差和百分比变化:{eth_change_chainlink:.2f} //// ({eth_change_chainlink_percentage:.2f}%)
总锁仓量变化:${yesterday["total_tvl_chainlink"]:,.2f} -> ${today["total_tvl_chainlink"]:,.2f}
价差和百分比变化:{tvl_change_chainlink:,.2f} //// ({tvl_change_chainlink_percentage:.2f}%)

$pyth数据的分析$
ETH价格变化:${yesterday["eth_price_pyth"]:.2f} -> ${today["eth_price_pyth"]:.2f}
价差和百分比变化:{eth_change_pyth:.2f} //// ({eth_change_pyth_percentage:.2f}%)
总锁仓量变化:${yesterday["total_tvl_pyth"]:,.2f} -> ${today["total_tvl_pyth"]:,.2f}
价差和百分比变化:{tvl_change_pyth:,.2f} //// ({tvl_change_pyth_percentage:.2f}%)

$defillama数据的分析$
总锁仓量变化:${yesterday["Defillama_tvl"]:,.2f} -> ${today["Defillama_tvl"]:,.2f}
价差和百分比��化:{defillama_change_tvl:,.2f} //// ({defillama_change_tvl_percentage:.2f}%)
"""
    print(report_text)

    gpt_response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {"role": "system", "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
            {"role": "user", "content": f"""{report_text}
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
"""}
        ]
    )
    print(gpt_response.choices[0].message.content)

    if weekday == 6:
        print("今天是周天，进行周报总结")
        week_data = history1[-7*24:]
        week_report = ""
        for day in week_data:
            week_report += f"""
日期：{day["timestamp"]}
ETH价格（Chainlink）：${day["eth_price_chainlink"]:.2f}
ETH价格（Pyth）：${day["eth_price_pyth"]:.2f}
总锁仓量（Chainlink）：${day["total_tvl_chainlink"]:,.2f}
总锁仓量（Pyth）：${day["total_tvl_pyth"]:,.2f}
DefiLlama总锁仓量：${day["Defillama_tvl"]:,.2f}
"""
        print(week_report)

        gpt_response = client.chat.completions.create(
            model="gpt-5.5",
            messages=[
                {"role": "system", "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
                {"role": "user", "content": f"""{week_report}
以下是Lido协议本周数据，请你：
1. 分析本周ETH价格和总锁仓量的整体趋势
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
        )
        print(gpt_response.choices[0].message.content)

        prompts = {
            "严格数据派": f"""{week_report}
以下是Lido协议本周数据，请你：
1. 只基于数据说话，不要主观猜测
2. 找出本周最异常的一天，说明原因
3. 计算本周TVL平均值和波动幅度
4. ETH价格和TVL的相关性分析
5. 用一句话总结本周最重要的信号
""",
            "风险预警派": f"""{week_report}
以下是Lido协议本周数据，请你扮演一个风控经理：
1. 找出所有潜在的风险信号
2. 判断资金是否在大规模流出
3. TVL下降是否已经达到警戒线
4. 给出1-10分的风险评级，并说明理由
5. 如果你是大户，看到这些数据你会怎么操作
""",
            "交易员派": f"""{week_report}
以下是Lido协议本周数据，请你扮演一个链上数据交易员：
1. 判断目前是积累阶段还是派发阶段
2. 大资金是在进场还是在离场
3. 下周ETH价格的支撑位和压力位在哪里
4. 现在是应该质押还是赎回stETH
5. 给出明确的操作建议，不要模糊回答
""",
            "简洁总结派": f"""{week_report}
以下是Lido协议本周数据，请用最简洁的方式：
1. 用三个关键词概括本周行情
2. 本周最重要的一件事是什么
3. 下周最需要关注的一个指标是什么
4. 一句话给出操作建议
"""
        }
        for 名字, 内容 in prompts.items():
            print(f"\n{'='*30}")
            print(f"【{名字}】的分析结果")
            print(f"{'='*30}")
            gpt_response = client.chat.completions.create(
                model="gpt-5.4-high",
                messages=[
                    {"role": "system", "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
                    {"role": "user", "content": 内容}
                ]
            )
            print(gpt_response.choices[0].message.content)

else:
    print("现在不是8点，只统计数据")