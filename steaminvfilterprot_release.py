from aiosteampy.client import SteamClientBase
from aiosteampy.models import (
    EconItem,
    MyMarketListing,
    BuyOrder,
    ItemDescription,
    MarketListingItem,
    MarketHistoryEvent,
    MarketHistoryListing,
    MarketHistoryListingItem,
    PriceHistoryEntry,
    MarketListing,
)
from aiohttp import ClientResponseError
from aiosteampy import EResultError, EResult, LoginError, RateLimitExceeded, SessionExpired, SteamError, SteamPublicClient, ResourceNotModified
from aiosteampy import AppContext, SteamClient, Currency, Language, App
from aiosteampy.utils import get_jsonable_cookies, update_session_cookies
from aiosteampy.helpers import restore_from_cookies
import asyncio, json, jsonpickle, yaml, sys, os, time, re, argparse, random
from pathlib import Path
from functools import partial
from pprint import pprint
# from .utils_s import accelerator, get_encoding
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
# sys.path.append((SCRIPT_DIR))
# from . import utils_s
from utils_s import accelerator, get_encoding
# import utils as utils_s
# from typing import Union
# COOKIE_FILE_PATH = os.path.join(STORAGE_FOLDER, "aiostmcookietest.json")
# print(CONFIG_FILE_PATH)
pyparser=argparse.ArgumentParser()
pyparser.add_argument('--config', type=str, default="")
pyparser.add_argument('--debug', action="store_true")
pyargs=pyparser.parse_args()
if pyargs.config:
	# CONFIG_FILE_PATH = os.path.join(CONFIG_FOLDER, pyargs.config) #wip
	pass
CONFIG_FOLDER = os.path.join(SCRIPT_DIR,"config")
STORAGE_FOLDER = os.path.join(SCRIPT_DIR,"storge")
CONFIG_FILE_PATH = os.path.join(CONFIG_FOLDER, "steam_config.json")
COOKIE_FILE_PATH = os.path.join(STORAGE_FOLDER, "aiostmcookietest.json")
# print(CONFIG_FILE_PATH)
config_file = Path(rf"{CONFIG_FILE_PATH}")
cookie_file = Path(rf"{COOKIE_FILE_PATH}")
# print(str(SCRIPT_DIR))
print(str(sys.path))
print(str(config_file))
print(str(cookie_file))
if cookie_file.is_file():
	print("true")
# sys.exit()
appenum = "CS2"
parrern_num = re.compile(r'[-+]?[\d]+(\.[\d]+)?')
def writeToFile(file_path:str|Path,writeContext):
	with open(file_path, "w", encoding='utf-8') as file:
	    file.write(str(writeContext))
class ForceQuit(Exception):
    """Force quited program."""
class Invilad(Exception):
    """Listing price is too Low."""
class ListingPriceTooLow(Exception):
    """Listing price is too Low."""
def save_steam_session(client: SteamClientBase):
	cookies = get_jsonable_cookies(client.session)
#	writeToFile(cookie_file,cookies)
	with cookie_file.open("w", encoding='utf-8') as f:
		json.dump(cookies, f)
def func_user_input_int_positive(custom_prompt: str = None,custom_func: str = None):
	pattern = re.compile("^check_listing_price_low\\(.+$")
	while True:
		try:
			user_input=input(f"{custom_prompt} Type \"e\" to exit: ")
			if user_input == "e":
				raise ForceQuit
#					sys.exit()
			user_input_int=int(user_input)
			if user_input_int <=0:
				raise
			# print(f"{custom_func}")
			if custom_func!=None:
				# print(f"2")
				if pattern.match(custom_func):
					# print(f"3")
					custom_func2=custom_func.replace("listingprice", user_input)
					# print(f"4")
					eval(custom_func2)
					# print(f"5")
		except ForceQuit:
			print(f"exiting")
			sys.exit()
		except ListingPriceTooLow:
			continue
		except Exception as e:
			# print(f"{e}")
			print("Invalid input")
			continue
		break
	print(f"input value: {user_input_int}")
	return user_input_int
def func_user_input_price(custom_prompt: str = None,custom_func: str = None):
	pattern = re.compile("^check_listing_price_low\\(.+$")
	while True:
		try:
			user_input=input(f"{custom_prompt} Type \"e\" to exit: ")
			if user_input == "e":
				raise ForceQuit
#					sys.exit()
			user_input_float=float(user_input)
			user_input_int=int(user_input_float*100)
			if user_input_int <=0:
				raise
			# print(f"{custom_func}")
			if custom_func!=None:
				# print(f"2")
				if pattern.match(custom_func):
					# print(f"3")
					custom_func2=custom_func.replace("listingprice", user_input)
					# print(f"4")
					eval(custom_func2)
					# print(f"5")
		except ForceQuit:
			print(f"exiting")
			sys.exit()
		except ListingPriceTooLow:
			continue
		except Exception as e:
			# print(f"{e}")
			print("Invalid input")
			continue
		break
	print(f"input value(internal price value): {user_input_int}")
	return user_input_int
def check_listing_price_low(itemname:str,nomalprice:float|int,listingprice:float|int):
	if listingprice<nomalprice*0.98:
		price_ratio="{:.1%}".format(listingprice/nomalprice)
		print(f"Listing price for {itemname} is too Low. Median price: {nomalprice}, Your price: {listingprice}, Ratio: {price_ratio}")
		raise ListingPriceTooLow
	asd=1
async def list_items(item:EconItem | int,items_to_list_price:int,client:SteamClientBase,auto_confirm: bool=False):
	if isinstance(item, EconItem):
		asset_id = item.asset_id
	else:
		asset_id = item
	i=0
	while True:
		i+=1
		if i>4:
			print(f"Failed too many times.")
			sys.exit()
		try:
			listing = await client.place_sell_listing(item, getattr(AppContext, appenum), price=items_to_list_price, confirm=auto_confirm)
		except EResultError as e:
			# items_to_list_amount_failed+=1
			# items_to_list_amount_succeeded-=1
			print(f"Listing {asset_id} failed. Steam returned an error: {e}")
			if re.compile("^You already have a listing.+").match(str(e)):
				break
			else:
				time.sleep(5)
				continue
			# print(f"Error code: {e.result}")
			# print(f"fff: {items_to_list_amount_succeeded}")
		except ClientResponseError as e:
			print(f"Listing {asset_id} failed. Steam returned an error: {e}")
			time.sleep(130) #min120
		except ConnectionResetError as e:
			time.sleep(5)

		else:
			items_to_list_price_show=float(items_to_list_price/100)
			print(f"Created listing: {asset_id}, Price: {items_to_list_price_show}")
			if auto_confirm ==0:
				randsleep=random.uniform(0.45, 0.6)
			else:
				print(f"auto confirming each item is very slow, you should confirm them at once.")
				randsleep=0
				# randsleep=random.uniform(0.1, 0.15)
				# pass
			time.sleep(randsleep)
			break
async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro
    return await asyncio.gather(*(sem_coro(c) for c in coros))

async def main():
	if not os.path.exists(CONFIG_FOLDER):
		os.mkdir(CONFIG_FOLDER)
	if config_file.is_file():
		with open(config_file, "r", encoding=get_encoding(config_file)) as f:
			try:
				CONFIG_FILE_RAW = json.loads(f.read())
			except Exception as e:
				# handle_caught_exception(e, known=True)
				# logger.error("检测到" + STEAM_ACCOUNT_INFO_FILE_PATH + "格式错误, 请检查配置文件格式是否正确! ")
				print(f"failed to load config file Error: {e}")
				sys.exit()
				return None
	else:
		writeToFile(config_file,"writeContext") # wip


	client = SteamClient(
		wallet_currency=, # eg. Currency.CNY
		wallet_country="", # eg. "CN"
		tz_offset="", # eg. "28800,0" (GMT+8) can find at steamcommunity.com cookies.
    	language=Language.ENGLISH,  # optional
		steam_id=,  # steam id(64) or account id(32)
		username="",
		password="",
		shared_secret="",
		identity_secret="",  #requied if listing items on steam market 
#		api_key="your_api_key",  # optional
#		trade_token="your_trade_token",  # optional
		proxy="", # eg. http://127.0.0.1:7890
		user_agent=""  # strongly recommended
	)

	if not os.path.exists(STORAGE_FOLDER):
		os.mkdir(STORAGE_FOLDER)
	if not os.path.exists(cookie_file):
	# if cookie_file.is_file():
		try:
			with cookie_file.open("r", encoding='utf-8') as f:
				cookies = json.load(f)
			await restore_from_cookies(cookies, client)
		except:
			await client.login()
	else:
		await client.login()
	# await client.login()
	print(f"Loaded Steam account: {client.username}")

	# load properties required for all methods to work
	# (currency, country, trade token)
	await client.prepare()
	
	async def get_this_user_inventory(appenum):
		text1=""
		this_user_steam_id=
		inventory, _, _ = await client.get_user_inventory(this_user_steam_id,getattr(AppContext, appenum),count=2000)
		try:
			if this_user_steam_id==client.steam_id:
				username=client.username
				text1=f"username: {username}, "
		except:
			pass
		print(f"Inventory owner: {text1}steam id: {inventory[0].owner_id}, items fetched: {len(inventory)}")
		writeToFile(os.path.join(STORAGE_FOLDER, "inventorycache.txt"),str(inventory))
		return inventory

	inventory=await get_this_user_inventory(appenum)
	# print(inventory[0].marketable, inventory[0].tradable, inventory[0].tradable, )
	# serialized = jsonpickle.encode(inventory[0].description)
	# print(json.dumps(json.loads(serialized), indent=2))
	# print(yaml.dump(yaml.load(serialized), indent=2))
	# print(vars(inventory[0].description))
	# testasfa=inventory[0].description
	# for attr in dir(testasfa):
	# 	print("testasfa.%s = %r" % (attr, getattr(testasfa, attr)))
	# https://stackoverflow.com/questions/192109/is-there-a-built-in-function-to-print-all-the-current-properties-and-values-of-a
	# https://stackoverflow.com/questions/5969806/print-all-properties-of-a-python-class
	# pprint(vars(inventory[0].description))
	# sys.exit()
	# Print price information
#	printcount=0
	def find_item_via_asset_id(n:EconItem,asset_id:int,is_reset: bool = False):
		#print("test")
		global printcount
		global last_asset_id
		try:
			last_asset_id
		except NameError:
#			print("NameError")
			printcount=0
			last_asset_id=asset_id
#			print(f"printcount:{printcount}, last_asset_id:{last_asset_id}")
#		print(f"printcount:{printcount}, last_asset_id:{last_asset_id}")
		if last_asset_id!=asset_id:
			is_reset=True
			print("reseted")
		if is_reset==True:
			printcount=0
			is_reset=False
		if printcount<2:
			print(f"item: {n.asset_id}, asset_id: {asset_id} printcount:{printcount}")
#		sys.exit()
		printcount+=1
		last_asset_id=asset_id
		return n.asset_id == asset_id
	def find_item_via_class_id(n:EconItem,class_id:int,is_reset: bool = False):
		#print("test")
		global printcount
		global last_class_id
		try:
			last_class_id
		except NameError:
#			print("NameError")
			printcount=0
			last_class_id=class_id
#			print(f"printcount:{printcount}, last_class_id:{last_class_id}")
#		print(f"printcount:{printcount}, last_class_id:{last_class_id}")
		if last_class_id!=class_id:
			is_reset=True
			print("reseted")
		if is_reset==True:
			printcount=0
			is_reset=False
		if printcount<2:
			print(f"item: {n.description.class_id}, class_id: {class_id} printcount:{printcount}")
#		sys.exit()
		printcount+=1
		last_class_id=class_id
		return n.description.class_id == class_id
	def find_item_marketable(n:EconItem):
		return n.description.marketable == True
	"""
	for i in inventory:
		find_item_via_asset_id(i,43921900256)
	"""
#	print(inventory[2].asset_id)
#	class_id_found=list(next(filter(partial(find_item_via_asset_id,asset_id=43927976529), inventory)))[0].description.class_id
#	class_id_found=list(next(i for i in inventory if find_item_via_asset_id(n=i,asset_id=43927976529)))[0].description.class_id
#	class_id_found=next(i for i in inventory if find_item_via_asset_id(n=i,asset_id=43927976529)).description.class_id
#	print(class_id_found)
#	sys.exit()
	while True:
		while True:
			try:
				user_input=input("Please enter the asset_id of item. Type \"r\" to refetch the inventory. Type \"e\" to exit: ")
				if user_input == "r":
					inventory=await get_this_user_inventory(appenum)
					continue
				if user_input == "e":
					raise ForceQuit
#					sys.exit()
				asset_id_search=int(user_input)
			except ForceQuit:
				print(f"exiting")
				sys.exit()
			except:
				print("Invalid input")
				continue
			break
	#	asset_id_search=43921900256
		try:
#			class_id_found=list(filter(partial(find_item_via_asset_id,asset_id=asset_id_search), inventory))[0].description.class_id #会导致程序无法用ctrl+c退出，并且无法应用全局变量?还是双层while true造成的？asyncio禁用全局变量
			item_found=next(i for i in inventory if find_item_via_asset_id(n=i,asset_id=asset_id_search))
			class_id_found=item_found.description.class_id
		except:
			print(f"item of asset_id: {asset_id_search} not found!")
#			sys.exit()
#			print(printcount)
#			printcount=0
			# https://stackoverflow.com/questions/68008585/global-variable-not-accessed-inside-poolmultiprocessing-in-python
			continue
		break
#	print(f"ft{printcount}")
#	class_id_found=list(i for i in inventory if find_item_via_asset_id(i,43922278802))[0]
#	class_id_found=list(i for i in inventory if find_item_via_asset_id(i,44100083209))[0].description.class_id
	item_found_neme=item_found.description.market_hash_name
	price_overview = await client.fetch_price_overview(item_found_neme, getattr(App, appenum))
	item_found_normal_price=price_overview['median_price']
	item_found_normal_price_float=re.search(parrern_num, item_found_normal_price).group()
	print(f"Item name: {item_found_neme}, median price on SCM: {item_found_normal_price}, class_id: {class_id_found}")
	items_found=list(i for i in inventory if find_item_via_class_id(n=i,class_id=class_id_found))
	print(f"Items found: {len(items_found)}")
	items_found_marketable=list(i for i in items_found if find_item_marketable(n=i))
	print(f"Marketable items found: {len(items_found_marketable)}")
	items_asset_id=list((i.asset_id for i in items_found_marketable))
	# print(items_asset_id)
	# sys.exit()
	items_to_list_amount=func_user_input_int_positive(f"Please enter the amount of items you want to sell.")
	if items_to_list_amount>len(items_asset_id):
		items_to_list_amount=len(items_asset_id)
	print(f"items_to_list_amount: {items_to_list_amount}")
	# sys.exit
	items_to_list_price=func_user_input_price(f"Please enter the listing price of items you want to sell.",f"check_listing_price_low(\"{item_found_neme}\",{item_found_normal_price_float},listingprice)")
	# price_overview['median_price']
	items_to_list_price_show=float(items_to_list_price/100)
	print(f"items_to_list_price_show(real price): {items_to_list_price_show}")
	items_to_list = items_asset_id[:items_to_list_amount]
	items_to_list_amount_failed=0
	items_to_list_amount_succeeded=items_to_list_amount
	print(f"started listing at {time.strftime('%X')}")
	tasks = []
	for i in items_to_list:
		tasks.append(list_items(i,items_to_list_price,client,True))
	# await asyncio.gather(*tasks)
	await gather_with_concurrency(1, *tasks)
	# await asyncio.wait(*tasks)
	"""
	except EResultError:
		sleep()
		continue
	num++
	"""
	print(f"finished listing at {time.strftime('%X')}")
	print(f"Created listing: {items_found_marketable[0].description.market_hash_name}, Price: {items_to_list_price_show}, Successfully listed:{items_to_list_amount_succeeded}, Failed:{items_to_list_amount_failed}")
	# for i in items_to_list:
		
#	print(list(class_id_found))
#	print(list(class_id_found).description.class_id)
	"""
	def find_asset_id_via_class_id(n,class_id):
		return n.description.class_id == class_id
	newone=list(filter(find_asset_id_via_class_id, inventory))
	newone_asset_id=(o.description.asset_id for o in newone)
	print(list(newone_asset_id))
	"""
	#https://stackoverflow.com/questions/1006169/how-do-i-look-inside-a-python-object
#	print(dir(inventory[0]))
#	print(getattr(inventory)) #needs 2 arguments
#	print(type(inventory))
#	print(type(inventory[0].description))
#	print(f"Created listing name: , listing id: {listing.listing_id}, Price: {listing.price}")
	"""
	#https://stackoverflow.com/questions/1006169/how-do-i-look-inside-a-python-object
	print(dir(inventory[0]))
	print(id(inventory))
	"""
#	print(inventory.__dict__)
	save_steam_session(client)
	await client.session.close()  # close client session
asyncio.run(main())	