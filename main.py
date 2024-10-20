import os
import asyncio
from dotenv import load_dotenv

from rich import print
from rich.traceback import install

import hikari

from web3 import Web3, AsyncWeb3, WebSocketProvider

from eth_abi import decode

from config import market_operators_config, filter_threshold
from abi import main_controller_abi

load_dotenv()
install()

DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']

ARBITRUM_RPC_URL = os.environ['ARBITRUM_RPC_URL']
OPTIMISM_RPC_URL = os.environ['OPTIMISM_RPC_URL']
BASE_RPC_URL = os.environ['BASE_RPC_URL']

MAIN_CONTROLLER = '0x1337F001E280420EcCe9E7B934Fa07D67fdb62CD'

class EventListener:
    """
    Listens for events on the Optimism and Arbitrum blockchains and handles them accordingly.
    
    The `EventListener` class is responsible for subscribing to various events on the Optimism and Arbitrum blockchains, such as CreateLoan, CloseLoan, LiquidateLoan, and AdjustLoan. When these events are detected, the class calls the corresponding event handler methods to process the event data and send a message to a Discord channel.
    
    The `subscribe_to_events` method is the main entry point for the event listener, where it sets up the event filters and starts listening for events. The event handler methods, such as `handle_create_loan_event`, `handle_close_loan_event`, `handle_liquidate_loan_event`, and `handle_adjust_loan_event`, are responsible for decoding the event data, converting the values to appropriate decimal formats, and sending the message to the Discord channel using the `send_message_to_channel` function.
    """

    def __init__(self, chain: str, async_w3):
        self.chain = chain
        self.async_w3 = async_w3
        self.market_operators = market_operators_config[self.chain]
        self.main_controller_contract = self.async_w3.eth.contract(
            address=MAIN_CONTROLLER,
            abi=main_controller_abi
        )

    async def subscribe_to_events(self):
        async for w3 in self.async_w3:
            print(
                f"{self.chain.upper()} Is connected to websocket: {await w3.is_connected()}"
            )

            TOPICS = {
                'CreateLoan': '0xbf2742c8e657897c9f047c065e83679fdea6e8bf1a460402c3c922f800b74bf1',
                'AdjustLoan': '0x79be6dfcb3a3568b21afc806c66bcd67098197716d17923c3189da0c7973f826',
                'LiquidateLoan': '0x9ef0a399defbe09357ef7431cb1cab06dd5ede64767faa82a286b5cbda5eeaf5',
                'CloseLoan': '0xabba776d3d0b8a6980d7277a9d4c2b2d7d9ce50e6d0deac46dd8a52437869ed9'
            }
            create_loan_filter = {
                "address": [MAIN_CONTROLLER],
                "topics": [TOPICS["CreateLoan"]],
            }

            close_loan_filter = {
                "address": [MAIN_CONTROLLER],
                "topics": [TOPICS["CloseLoan"]],
            }

            liquidate_loan_filter = {
                "address": [MAIN_CONTROLLER],
                "topics": [TOPICS["LiquidateLoan"]],
            }

            adjust_loan_filter = {
                "address": [MAIN_CONTROLLER],
                "topics": [TOPICS["AdjustLoan"]],
            }

            await w3.eth.subscribe("logs", create_loan_filter)
            await w3.eth.subscribe("logs", close_loan_filter)
            await w3.eth.subscribe("logs", liquidate_loan_filter)
            await w3.eth.subscribe("logs", adjust_loan_filter)

            async for event in w3.socket.process_subscriptions():
                print(event)
                topic0 = Web3.to_hex(event['result']['topics'][0])

                if topic0 == TOPICS["CreateLoan"]:
                    await self.handle_create_loan_event(event)
                
                elif topic0 == TOPICS["CloseLoan"]:
                    await self.handle_close_loan_event(event)

                elif topic0 == TOPICS["LiquidateLoan"]:
                    await self.handle_liquidate_loan_event(event)

                elif topic0 == TOPICS["AdjustLoan"]:
                    await self.handle_adjust_loan_event(event)

    async def handle_create_loan_event(self, event):
        # Get market operator address from event
        market_operator = decode(['address'], event['result']['topics'][1])[0] # Decode from bytes32
        market_operator = Web3.to_checksum_address(market_operator) # Convert to checksum address
        collateral_name = self.market_operators[market_operator]['collateral_name']
        collateral_address = self.market_operators[market_operator]['collateral_address']

        # Decode data
        coll_amount, debt_amount = decode(['uint256', 'uint256'], event['result']['data'])
        
        # Convert values to decimals
        coll_amount_dec = round(coll_amount / 10 ** self.market_operators[market_operator]['collateral_decimals'], 6)
        debt_amount_dec = round(debt_amount / 10 ** 18, 2) # $MONEY has 18 decimals
        
        coll_value = await self.get_coll_value(collateral_address, coll_amount_dec)

        # Filtering operation: if collateral value or debt amount is greater than filter_threshold, send message to Discord.
        if coll_value > filter_threshold or debt_amount_dec > filter_threshold:
            await send_message_to_channel(f">>> ### New loan created on {self.chain.upper()} \n{collateral_name} deposited: __{coll_amount_dec}__ \n$MONEY minted: __{debt_amount_dec}__")

    async def handle_close_loan_event(self, event):
        # Get market operator address from event
        market_operator = decode(['address'], event['result']['topics'][1])[0] # Decode from bytes32
        market_operator = Web3.to_checksum_address(market_operator) # Convert to checksum address
        collateral_name = self.market_operators[market_operator]['collateral_name']
        collateral_address = self.market_operators[market_operator]['collateral_address']

        # Decode data
        coll_withdrawn, debt_withdrawn, debt_repaid = decode(['uint256', 'uint256', 'uint256'], event['result']['data'])
        
        # Convert values to decimals
        coll_withdrawn_amount_dec = round(coll_withdrawn / 10 ** self.market_operators[market_operator]['collateral_decimals'], 6)
        debt_withdrawn_amount_dec = round(debt_withdrawn / 10 ** 18, 2) # $MONEY has 18 decimals
        debt_repaid_amount_dec = round(debt_repaid / 10 ** 18, 2) # $MONEY has 18 decimals

        coll_value = await self.get_coll_value(collateral_address, coll_withdrawn_amount_dec)
        
        # Filtering operation: if any of the values is greater than filter_threshold, send message to Discord.
        if coll_value > filter_threshold or debt_withdrawn_amount_dec > filter_threshold or debt_repaid_amount_dec > filter_threshold:
            await send_message_to_channel(f">>> ### Loan closed on {self.chain.upper()} \n{collateral_name} withdrawn: __{coll_withdrawn_amount_dec}__ \n$MONEY withdrawn: __{debt_withdrawn_amount_dec}__ \n$MONEY repaid: __{debt_repaid_amount_dec}__")

    async def handle_liquidate_loan_event(self, event):
        # Get market operator address from event
        market_operator = decode(['address'], event['result']['topics'][1])[0] # Decode from bytes32
        market_operator = Web3.to_checksum_address(market_operator) # Convert to checksum address
        collateral_name = self.market_operators[market_operator]['collateral_name']
        collateral_address = self.market_operators[market_operator]['collateral_address']

        # Decode data
        coll_received, debt_received, debt_repaid = decode(['uint256', 'uint256', 'uint256'], event['result']['data'])
        
        # Convert values to decimals
        coll_received_amount_dec = round(coll_received / 10 ** self.market_operators[market_operator]['collateral_decimals'], 6)
        debt_received_amount_dec = round(debt_received / 10 ** 18, 2) # $MONEY has 18 decimals
        debt_repaid_amount_dec = round(debt_repaid / 10 ** 18, 2) # $MONEY has 18 decimals
        
        await send_message_to_channel(f">>> ### Loan liquidated on {self.chain.upper()} \n{collateral_name} received: __{coll_received_amount_dec}__ \n$MONEY received: __{debt_received_amount_dec}__ \n$MONEY repaid: __{debt_repaid_amount_dec}__")

    async def handle_adjust_loan_event(self, event):
        # Get market operator address from event
        market_operator = decode(['address'], event['result']['topics'][1])[0] # Decode from bytes32
        market_operator = Web3.to_checksum_address(market_operator) # Convert to checksum address
        collateral_name = self.market_operators[market_operator]['collateral_name']
        collateral_address = self.market_operators[market_operator]['collateral_address']

        # Decode data
        coll_adjustment, debt_adjustment = decode(['int256', 'int256'], event['result']['data'])
        
        # Convert values to decimals
        coll_adjustment_amount_dec = round(coll_adjustment / 10 ** self.market_operators[market_operator]['collateral_decimals'], 6)
        debt_adjustment_amount_dec = round(debt_adjustment / 10 ** 18, 2) # $MONEY has 18 decimals

        coll_value = await self.get_coll_value(collateral_address, coll_adjustment_amount_dec)

        if coll_adjustment_amount_dec >= 0:
            coll_adjustment_descriptor: str = 'added'
        else:
            coll_adjustment_descriptor: str = 'withdrawn'

        if debt_adjustment_amount_dec >= 0:
            debt_adjustment_descriptor: str = 'minted'
        else:
            debt_adjustment_descriptor: str = 'repaid'
        
        # Filtering operation: if the absolute change of collateral OR debt is greater than filter_threshold, send message to Discord.
        if abs(coll_value) > filter_threshold or abs(debt_adjustment_amount_dec) > filter_threshold:
            await send_message_to_channel(f">>> ### Loan adjustment on {self.chain.upper()} \n{collateral_name} {coll_adjustment_descriptor}: __{coll_adjustment_amount_dec}__ \n$MONEY {debt_adjustment_descriptor}: __{debt_adjustment_amount_dec}__")

    async def get_coll_value(self, collateral_address: str, coll_amount_dec: float):
        coll_oracle_price: int = await self.main_controller_contract.functions.get_oracle_price(
            collateral_address
        ).call()

        coll_oracle_price_dec: float = coll_oracle_price / 10 ** 18

        coll_value: float = coll_oracle_price_dec * coll_amount_dec

        return coll_value

async def send_message_to_channel(message):
    rest = hikari.RESTApp()

    await rest.start()

    # We acquire a client with a given token. This allows one REST app instance
    # with one internal connection pool to be reused.
    async with rest.acquire(DISCORD_BOT_TOKEN, "Bot") as client:
        await client.create_message(CHANNEL_ID, f'{message}\n')

    await rest.close()
    
async def main():
    optimism_async_w3 = AsyncWeb3(WebSocketProvider(OPTIMISM_RPC_URL))
    arbitrum_async_w3 = AsyncWeb3(WebSocketProvider(ARBITRUM_RPC_URL))
    base_async_w3 = AsyncWeb3(WebSocketProvider(BASE_RPC_URL))

    optimism_listener = EventListener('optimism', optimism_async_w3)
    arbitrum_listener = EventListener('arbitrum', arbitrum_async_w3)
    base_listener = EventListener('base', base_async_w3)

    tasks = [
        optimism_listener.subscribe_to_events(),
        arbitrum_listener.subscribe_to_events(),
        base_listener.subscribe_to_events()
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())

        except Exception as e:
            print(f'Error: \n{e}')
            continue