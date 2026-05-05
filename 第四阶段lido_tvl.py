
from dotenv import load_dotenv
import schedule
import time

import os
import requests
from web3 import Web3

import json

from datetime import datetime, timedelta
from openai import OpenAI

load_dotenv()
data_dir = os.path.dirname(os.getenv("HISTORY_FILE", "data/lido_tvl_history.json"))
os.makedirs(data_dir, exist_ok=True)



def find_closest(history, target_time, max_diff_hours=0.5):
    result = min(history, key=lambda r: abs(
        (datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") - target_time).total_seconds()
    ))
    diff = abs((datetime.strptime(result["timestamp"], "%Y-%m-%d %H:%M:%S") - target_time).total_seconds())
    if diff <= max_diff_hours * 3600:
        return result
    else:
        return None

def send_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token is None or chat_id is None:
        print("⚠️ Telegram配置缺失，跳过发送")
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={
            "chat_id": chat_id,
            "text": text
        })
        print("✅ Telegram发送成功")
    except Exception as e:
        print(f"⚠️ Telegram发送失败：{e}")

def call_gpt(messages, model="gpt-5.5"): 
    api_configs = [
        {
            "api_key": os.getenv("OPENAI_API_KEY_1"),
            "base_url": os.getenv("OPENAI_BASE_URL_1"),
        },
        {
            "api_key": os.getenv("OPENAI_API_KEY_2"),
            "base_url": os.getenv("OPENAI_BASE_URL_2"),
        },
        {
            "api_key": os.getenv("OPENAI_API_KEY_3"),
            "base_url": os.getenv("OPENAI_BASE_URL_3"),
        },
    ]

    new_api_configs = []
    for config in api_configs:
        if config["api_key"] and config["base_url"]:
            new_api_configs.append(config)
    api_configs = new_api_configs
    for config in api_configs:
        try:
            client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            print("✅ GPT调用成功")
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ GPT调用失败：{e}，尝试备用接口...")
    print("❌ 所有GPT接口都失败了，跳过AI分析")
    return None

def main():

    rpc_list=[
        os.getenv("RPC_URL_1"),
        os.getenv("RPC_URL_2"),
        os.getenv("RPC_URL_3"),
        ]
    new_rpc_list = []
    for rpc in rpc_list:
        if rpc:
            new_rpc_list.append(rpc)
    rpc_list = new_rpc_list
    w3 = None
    for rpc in rpc_list:
        try:
            w3_temp = Web3(Web3.HTTPProvider(rpc))
            if w3_temp.is_connected():
                w3 = w3_temp
                print(f"✅ 主网连接成功：{rpc}")
                break
        except Exception as e:
            print(f"⚠️ 连接失败：{rpc}，原因：{e}，尝试下一个...")
    if w3 is None:
        print("❌ 所有主网节点连接失败，程序停止")
        return

    
    STETH_ADDRESS="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
    ABI_connect = [
        {
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    total_supply_eth=None
    try:
        contract=w3.eth.contract(address=STETH_ADDRESS,abi=ABI_connect)
        total_supply=contract.functions.totalSupply().call()
        total_supply_eth =total_supply/10**18
        print(f"✅ stETH总供应量：{total_supply_eth:.2f} ETH")
    except Exception as e:
        print(f"⚠️ 获取总供应量失败：{e}，尝试下一个...")
        return



    
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
    eth_price_chainlink = None
    try:
        chainlink = w3.eth.contract(address=CHAINLINK_ADDRESS, abi=ABI_CHAINLINK)
        data=chainlink.functions.latestRoundData().call()
        eth_price_chainlink=data[1]/10**8
        print(f"✅ Chainlink ETH价格：${eth_price_chainlink:.2f}")
    except Exception as e:
        print(f"⚠️ 获取Chainlink价格失败：{e}，尝试下一个...")

    
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
    eth_price_pyth=None
    try:
        pyth = w3.eth.contract(address=PYTH_ADDRESS, abi=ABI_PYTH)
        data = pyth.functions.getPriceUnsafe(ETH_USD_ID).call()
        eth_price_pyth = data[0] * (10**data[2])
        print(f"✅ Pyth ETH价格：${eth_price_pyth}")
    except Exception as e:
        print(f"⚠️ Pyth获取失败：{e}")
    
    if eth_price_chainlink is None and eth_price_pyth is None:
        print("❌ 两个预言机都挂了，程序停止")
        return
    elif eth_price_chainlink is None:
        eth_price_chainlink = eth_price_pyth
        print("⚠️ Chainlink不可用，用Pyth价格替代")
    elif eth_price_pyth is None:
        eth_price_pyth = eth_price_chainlink
        print("⚠️ Pyth不可用，用Chainlink价格替代")

    
    steth_tvl_chainlink=eth_price_chainlink*total_supply_eth
    print(steth_tvl_chainlink)

    
    steth_tvl_pyth=eth_price_pyth*total_supply_eth
    print(steth_tvl_pyth)




    
    url_llama = "https://api.llama.fi/protocol/lido"
    response = requests.get(url_llama,timeout=10)
    data = response.json()
    tokens_usd = data["tokensInUsd"][-1]["tokens"]
    print(tokens_usd)

    
    other_tvl_第一种方法 = 0
    for k, v in tokens_usd.items():
        if k != "WETH":
            other_tvl_第一种方法 += v
    print(other_tvl_第一种方法)

    
    WMATIC_TVL=tokens_usd["WMATIC"]
    DOT_TVL=tokens_usd["DOT"]
    KSM_TVL=tokens_usd["KSM"]
    SOL_TVL=tokens_usd["SOL"]
    other_tvl_第二种方法=WMATIC_TVL+DOT_TVL+KSM_TVL+SOL_TVL
    print(other_tvl_第二种方法)

    
    total_tvl_CHAINLINK=steth_tvl_chainlink+other_tvl_第一种方法
    print(total_tvl_CHAINLINK)

    
    total_tvl_pyth=steth_tvl_pyth+other_tvl_第一种方法
    print(total_tvl_pyth)

    
    url_llama = "https://api.llama.fi/protocol/lido"
    response = requests.get(url_llama,timeout=10)
    data = response.json()
    Defillama_tvl = data["tvl"][-1]["totalLiquidityUSD"]


    
    
    hour = datetime.now().hour
    lido_apr = None
    apr_onchain = None

    if hour == 8:
        url_lido_apr = "https://eth-api.lido.fi/v1/protocol/steth/apr/last"
        response_lido_apr = requests.get(url_lido_apr,timeout=10)
        data_lido_apr = response_lido_apr.json()
        lido_apr = data_lido_apr["data"]["apr"]
        print(f"Lido官方API APR：{lido_apr:.4f}%")

    
        latest_block = w3.eth.block_number
        event_signature = "0x" + w3.keccak(text="TokenRebased(uint256,uint256,uint256,uint256,uint256,uint256,uint256)").hex()
        flock_block = latest_block - 20000

        logs = w3.eth.get_logs({
            "fromBlock": flock_block,
            "toBlock": latest_block,
            "address": STETH_ADDRESS,
            "topics": [event_signature]
        })

        log = logs[-1]
        data = log["data"]
        values = [int.from_bytes(data[i:i+32], "big") for i in range(0, len(data), 32)]

        timeElapsed     = values[0]
        preTotalShares  = values[1]
        preTotalEther   = values[2]
        postTotalShares = values[3]
        postTotalEther  = values[4]

        pre_share_price  = preTotalEther / preTotalShares
        post_share_price = postTotalEther / postTotalShares

        apr_onchain = (post_share_price - pre_share_price) / pre_share_price * (365 * 24 * 3600 / timeElapsed)
        
        print(f"链上最近1次rebase APR：{apr_onchain*100:.4f}%")

        apr_diff = abs(lido_apr - apr_onchain * 100)

        if apr_diff > 1:
            print(f"🔴 红色预警：官方APR {lido_apr:.4f}% vs 链上APR {apr_onchain*100:.4f}%，差距 {apr_diff:.4f}%，官方数据疑似造假！以链上数据为准。")
        elif apr_diff > 0.5:
            print(f"🟡 黄色预警：官方APR {lido_apr:.4f}% vs 链上APR {apr_onchain*100:.4f}%，差距 {apr_diff:.4f}%，需要关注。")
        else:
            print(f"✅ APR数据正常，官方与链上差距 {apr_diff:.4f}%，情况正常该吃吃该喝喝。")



    
    print("========== 最终结果 ==========")   
    print(f"ETH价格（Chainlink）: ${eth_price_chainlink}")
    print(f"ETH价格（Pyth）: ${eth_price_pyth}")
    print(f"stETH TVL（Chainlink）: ${steth_tvl_chainlink:,.2f}")
    print(f"stETH TVL（Pyth）: ${steth_tvl_pyth:,.2f}")
    print(f"其他代币TVL: ${other_tvl_第一种方法:,.2f}")
    print(f"总TVL（Chainlink）: ${total_tvl_CHAINLINK:,.2f}")
    print(f"总TVL（Pyth）: ${total_tvl_pyth:,.2f}")
    print(f"DefiLlama官方api总TVL: ${Defillama_tvl:,.2f}")



    


    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hour = datetime.now().hour
    weekday = datetime.now().weekday()

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
        "Defillama_tvl": Defillama_tvl,
        "lido_apr": lido_apr,
        "apr_onchain": apr_onchain,
    }

    
    filename = os.getenv("HISTORY_FILE", "data/lido_tvl_history.json")
    if os.path.exists(filename):
        with open(filename,"r",encoding="utf-8") as file:
            history=json.load(file)
    else:
        history=[]

    history.append(record)

    with open(filename,"w",encoding="utf-8") as file:
        json.dump(history,file,ensure_ascii=False,indent=2)
    print(f"数据已经保存到{filename}文件里面，记录时间:{now}")


    
    with open(filename, "r", encoding="utf-8") as file:
        history1=json.load(file)
    latest=history1[-1]

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
    """)

    if len(history1)<2:
        print("历史数据不足，跳过小时预警分析")
    else:
        previous=history1[-2]
        latest=history1[-1]
        tvl_hourly_change=latest["total_tvl_chainlink"]-previous["total_tvl_chainlink"]
        tvl_hourly_change_percentage=tvl_hourly_change/previous["total_tvl_chainlink"]*100
        print(f"TVL变化额：${tvl_hourly_change:,.2f}")
        print(f"TVL变化幅度：{tvl_hourly_change_percentage:.2f}%")
        if tvl_hourly_change_percentage<-0.5:
            print(f"链上总锁仓量在过去1小时内减少了{abs(tvl_hourly_change_percentage):.4f}%，🔴大户都在跑路了，快跑！")
        elif tvl_hourly_change_percentage<-0.1:
            print(f"链上总锁仓量在过去1小时内减少了{abs(tvl_hourly_change_percentage):.4f}%，🟡可能存在风险，需要注意了。")
        else:
            print(f"链上总锁仓量在过去1小时内变化不大，✅数据正常，该吃吃该喝喝。")


    
    target_today_8am=datetime.now().replace(hour=8,minute=0,second=0,microsecond=0)
    today_real_8am=find_closest(history1, target_today_8am)

    target_yesterday_8am=(datetime.now()-timedelta(days=1)).replace(hour=8,minute=0,second=0,microsecond=0)
    yesterday_real_8am=find_closest(history1, target_yesterday_8am)

    if today_real_8am is None or yesterday_real_8am is None:
        print("⚠️ 历史数据不足，跳过日环比分析")
    else:

        
        eth_change_chainlink_real_8am=today_real_8am["eth_price_chainlink"]-yesterday_real_8am["eth_price_chainlink"]
        eth_change_chainlink_percentage_real_8am=eth_change_chainlink_real_8am/yesterday_real_8am["eth_price_chainlink"]*100

        tvl_change_chainlink_real_8am=today_real_8am["total_tvl_chainlink"]-yesterday_real_8am["total_tvl_chainlink"]
        tvl_change_chainlink_percentage_real_8am=tvl_change_chainlink_real_8am/yesterday_real_8am["total_tvl_chainlink"]*100

        
        eth_change_pyth_real_8am=today_real_8am["eth_price_pyth"]-yesterday_real_8am["eth_price_pyth"]
        eth_change_pyth_percentage_real_8am=eth_change_pyth_real_8am/yesterday_real_8am["eth_price_pyth"]*100

        tvl_change_pyth_real_8am=today_real_8am["total_tvl_pyth"]-yesterday_real_8am["total_tvl_pyth"]
        tvl_change_pyth_percentage_real_8am=tvl_change_pyth_real_8am/yesterday_real_8am["total_tvl_pyth"]*100

        
        defillama_change_tvl_real_8am=today_real_8am["Defillama_tvl"]-yesterday_real_8am["Defillama_tvl"]
        defillama_change_tvl_percentage_real_8am=defillama_change_tvl_real_8am/yesterday_real_8am["Defillama_tvl"]*100

        
        if tvl_change_chainlink_percentage_real_8am < -10:
            print(f"链上总锁仓量在过去1天内减少了{abs(tvl_change_chainlink_percentage_real_8am):.4f}%，🔴大户都在跑路了，快跑！")
        elif tvl_change_chainlink_percentage_real_8am < -5:
            print(f"链上总锁仓量在过去1天内减少了{abs(tvl_change_chainlink_percentage_real_8am):.4f}%，🟡可能存在风险，需要注意了。")
        else:
            print(f"链上总锁仓量在过去1天内变化不大，✅数据正常，该吃吃该喝喝。")

        
        if today_real_8am.get("apr_onchain") is not None and yesterday_real_8am.get("apr_onchain") is not None:
            apr_onchain_today = today_real_8am.get("apr_onchain")
            apr_onchain_yesterday = yesterday_real_8am.get("apr_onchain")
            apr_onchain_change_pct = (apr_onchain_today - apr_onchain_yesterday) / apr_onchain_yesterday * 100

            print(f"链上APR变化：{apr_onchain_yesterday*100:.4f}% -> {apr_onchain_today*100:.4f}%，日环比：{apr_onchain_change_pct:.2f}%")

            if apr_onchain_change_pct < -20:
                print(f"🔴 红色预警：链上APR日环比下降 {abs(apr_onchain_change_pct):.2f}%，收益率暴跌！")
            elif apr_onchain_change_pct < -10:
                print(f"🟡 黄色预警：链上APR日环比下降 {abs(apr_onchain_change_pct):.2f}%，需要关注。")
            elif apr_onchain_change_pct > 20:
                print(f"🔴 红色预警：链上APR日环比上涨 {apr_onchain_change_pct:.2f}%，异常暴涨疑似刷数据！")
            elif apr_onchain_change_pct > 10:
                print(f"🟡 黄色预警：链上APR日环比上涨 {apr_onchain_change_pct:.2f}%，需要关注。")
            else:
                print(f"✅ 链上APR正常，日环比变化 {apr_onchain_change_pct:.2f}%，无需预警。")
        else:
            print("APR历史数据不足，跳过日环比预警")

        
        if hour == 8:
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

            
            gpt_daily_result = call_gpt(messages=[
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
                ],
                model="gpt-5.5"
            )
            if gpt_daily_result is not None:
                print(gpt_daily_result)

            
            daily_result_filename = os.getenv("DAILY_FILE", "data/lido_daily_analysis.json")

            if os.path.exists(daily_result_filename):
                with open(daily_result_filename, "r", encoding="utf-8") as file:
                    daily_history = json.load(file)
            else:
                daily_history = []
            daily_history.append({
                "timestamp": today_real_8am["timestamp"],
                "report": report_text,
                "gpt_analysis": gpt_daily_result
            })

            with open(daily_result_filename, "w", encoding="utf-8") as file:
                json.dump(daily_history, file, ensure_ascii=False, indent=2)

            print(f"日环比分析已保存到{daily_result_filename}")
            send_telegram(f"📊 Lido日报分析完成：\n{daily_history}")
    
    daily_result_filename = os.getenv("DAILY_FILE", "data/lido_daily_analysis.json")
    if hour == 8 and weekday == 6:
        with open(daily_result_filename, "r", encoding="utf-8") as file:
            daily_history = json.load(file)
        
        week_daily = daily_history[-7:]

        week_report_text = ""
        for day in week_daily:
            week_report_text += f"\n{day['report']}\n"

    
        gpt_week_result = call_gpt(messages=[
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
            ],
            model="gpt-5.5"
        )
        if gpt_week_result is not None:
            print(gpt_week_result)

    
        week_result_filename = os.getenv("WEEK_FILE", "data/lido_week_analysis.json")

        if os.path.exists(week_result_filename):
            with open(week_result_filename, "r", encoding="utf-8") as file:
                week_history = json.load(file)
        else:
            week_history = []

        week_history.append({
            "timestamp": today_real_8am["timestamp"],
            "week_report": week_report_text,
            "gpt_analysis": gpt_week_result
        })

        with open(week_result_filename, "w", encoding="utf-8") as file:
            json.dump(week_history, file, ensure_ascii=False, indent=2)

        print(f"周报分析已保存到{week_result_filename}")
        send_telegram(f"📈 Lido周报分析完成：\n{week_history}")
    
        prompts={
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
        for name,prompt_content in prompts.items():
            print(f"\n{'='*30}")
            print(f"【{name}】的分析结果")
            print(f"{'='*30}")
        
            gpt_result = call_gpt(messages=[
                    {"role": "system",
                    "content": "你是一个专业的DeFi数据分析师，擅长分析Lido协议的TVL和ETH价格走势。"},
                    {"role": "user",
                    "content": prompt_content}
                ],
                model="gpt-5.5"
            )
            if gpt_result is not None:
                print(gpt_result)


schedule.every().hour.do(main)

print("✅ 定时任务已启动，每小时执行一次...")
main()  
while True:
    schedule.run_pending()
    time.sleep(60)