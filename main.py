#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from asyncio import sleep as asleep

import discord
import requests
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.realpath(__file__))
if not os.path.isfile(os.path.join(current_dir, ".env")):
    print(
        "No .env file found, make sure to copy .env.example to .env and fill in the values"
    )
    exit(1)

load_dotenv()
guildID = int(os.getenv("DAODAO_TREASURY_GUILD_ID", 0))
memberID = int(os.getenv("DAODAO_TREASURY_MEMBER_ID", 0))
BOT_TOKEN = os.getenv("DAODAO_TREASURY_BOT_TOKEN", "")
DAODAO_NAME = os.getenv("DAODAO_NAME", "DAO")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

REST_API = os.getenv("DAODAO_JUNOD_NODE", "https://api.juno.strange.love")
DAO = os.getenv("DAODAO_TREASURY_DAO", "")

headers = {"Content-Type": "application/json"}


def getDAOAssets() -> dict:
    assets = {}
    print("Getting assets")
    a = requests.get(f"{REST_API}/cosmos/bank/v1beta1/balances/{DAO}", timeout=20)
    if a.status_code == 200:
        for i in a.json()["balances"]:
            assets[i["denom"]] = i["amount"]
    return assets


def getPrices() -> dict:
    prices = {}
    print("Getting prices")
    a = requests.get(
        "https://api.wynddao.com/assets/prices",
        headers=headers,
        timeout=20,
    )

    if a.status_code == 200:
        for i in a.json():
            prices[i["asset"]] = i["priceInUsd"]

    return prices


def getDAOWorth() -> float:
    prices = getPrices()
    assets = getDAOAssets()

    totalUSD = 0.0
    for coin in assets:
        if coin not in prices:
            continue

        totalUSD += (float(assets[coin]) / 10**6) * float(prices[coin])

    return totalUSD


@client.event
async def on_ready():
    print(f"You have logged in as {client}")
    guild = client.get_guild(guildID)
    member = guild.get_member(memberID)    

    last_time = 0
    USD = getDAOWorth()

    await member.edit(nick=f"{DAODAO_NAME}")            

    while True:
        try:        
            if last_time >= 60:
                last_time = 0
                USD = getDAOWorth()
            
            await client.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"${USD:,.0f}",
                )
            )
            print("Updated status, waiting 30 seconds")            
            await asleep(30)
            last_time += 30
        except:            
            continue


client.run(BOT_TOKEN)
