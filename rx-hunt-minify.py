_L='User-Agent'
_K='username'
_J='users'
_I='role'
_H='userId'
_G='displayName'
_F=None
_E='rank'
_D=True
_C='description'
_B=False
_A='name'
import asyncio,aiohttp,argparse,os
from dotenv import load_dotenv
from functools import lru_cache
from tqdm import tqdm
from rich.console import Console
from rich.table import Table
from rich import box
import json,csv
from datetime import datetime
import logging
from typing import Dict,List,Optional,Any
import random,time
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)
class Colors:SUCCESS='\x1b[38;5;42m';ERROR='\x1b[38;5;196m';WARNING='\x1b[38;5;214m';INFO='\x1b[38;5;111m';ACCENT='\x1b[38;5;141m';HIGHLIGHT='\x1b[38;5;229m';MUTED='\x1b[38;5;246m';CYAN='\x1b[38;5;87m';BOLD='\x1b[1m';DIM='\x1b[2m';RESET='\x1b[0m';CHECK='✓';CROSS='✗';ARROW='→';DOT='•'
class RichStyles:SUCCESS='bright_green';ERROR='bright_red';WARNING='orange3';INFO='royal_blue1';ACCENT='medium_purple3';HIGHLIGHT='light_yellow';MUTED='grey70';CYAN='cyan1';BOLD='bold'
console=Console()
ASCII_ART=f"""
{Colors.ACCENT}┌────────────────────────────────────────────────────────────┐
│ ██████╗ ██╗  ██╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗ │
│ ██╔══██╗╚██╗██╔╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝ │
│ ██████╔╝ ╚███╔╝     ███████║██║   ██║██╔██╗ ██║   ██║    │
│ ██╔══██╗ ██╔██╗     ██╔══██║██║   ██║██║╚██╗██║   ██║    │
│ ██║  ██║██╔╝ ██╗    ██║  ██║╚██████╔╝██║ ╚████║   ██║    │
│ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝    │
├────────────────────────────────────────────────────────────┤
│              RX Hunt - Advanced Group Recon Tool           │
└────────────────────────────────────────────────────────────┘{Colors.RESET}
"""
class RobloxRecon:
	def __init__(A,group_id,output_dir,use_proxy=_B):A.group_id=group_id;A.output_dir=os.path.expanduser(output_dir);A.session=_F;A.user_cache={};A.use_proxy=use_proxy;A.request_count=0;A.start_time=time.time();A.user_agents=['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'];os.makedirs(A.output_dir,exist_ok=_D)
	def get_random_user_agent(A):'Get a random browser User-Agent';return random.choice(A.user_agents)
	async def __aenter__(A):B={_L:A.get_random_user_agent(),'Accept':'application/json, text/plain, */*','Accept-Language':'en-US,en;q=0.9','Accept-Encoding':'gzip, deflate, br','Connection':'keep-alive'};A.session=aiohttp.ClientSession(headers=B,timeout=aiohttp.ClientTimeout(total=60),connector=aiohttp.TCPConnector(limit=10,ssl=_B));return A
	async def __aexit__(A,exc_type,exc_val,exc_tb):
		if A.session:await A.session.close()
	async def make_request(B,url,max_retries=5):
		'Make API request with exponential backoff retry and rate limiting';F=max_retries;D=url
		if not B.session:raise RuntimeError('Session not initialized')
		B.request_count+=1;I=time.time()-B.start_time
		if B.request_count>=10 and I<60:C=60-I;print(f"{Colors.WARNING}{Colors.CROSS} Rate limit protection: waiting {C:.1f}s{Colors.RESET}");await asyncio.sleep(C);B.request_count=0;B.start_time=time.time()
		for A in range(F):
			try:
				if A>0:J=random.uniform(1,3);await asyncio.sleep(J)
				if random.random()<.3:B.session.headers[_L]=B.get_random_user_agent()
				async with B.session.get(D)as E:
					if E.status==429:C=min(2**A*5,120);print(f"{Colors.WARNING}{Colors.CROSS} Rate limited, waiting {C}s (attempt {A+1}){Colors.RESET}");await asyncio.sleep(C);continue
					if E.status==400:
						H=await E.text();print(f"{Colors.ERROR}{Colors.CROSS} Bad Request (400) for {D}{Colors.RESET}");print(f"{Colors.MUTED}Response: {H[:200]}{Colors.RESET}")
						if'is invalid'in H.lower()or'not found'in H.lower():raise ValueError(f"Invalid Group ID: {B.group_id}")
						else:C=min(2**A*10,60);await asyncio.sleep(C);continue
					if E.status==403:print(f"{Colors.ERROR}{Colors.CROSS} Access forbidden (403) - IP might be blocked{Colors.RESET}");C=min(2**A*15,90);await asyncio.sleep(C);continue
					if E.status==404:raise ValueError(f"Resource not found: {D}")
					E.raise_for_status();await asyncio.sleep(random.uniform(.1,.5));return await E.json()
			except asyncio.TimeoutError:
				print(f"{Colors.WARNING}{Colors.CROSS} Timeout on attempt {A+1} for {D}{Colors.RESET}")
				if A==F-1:raise
				await asyncio.sleep(2**A)
			except aiohttp.ClientError as G:
				print(f"{Colors.WARNING}{Colors.CROSS} Network error on attempt {A+1}: {G}{Colors.RESET}")
				if A==F-1:raise Exception(f"Failed to fetch {D} after {F} attempts: {G}")
				await asyncio.sleep(2**A)
			except Exception as G:
				if A==F-1:raise Exception(f"Failed to fetch {D} after {F} attempts: {G}")
				await asyncio.sleep(2**A)
		raise Exception(f"Max retries exceeded for {D}")
	async def validate_group_id(B):
		'Validate if the group ID exists and is accessible'
		try:
			C=f"https://groups.roblox.com/v1/groups/{B.group_id}";A=await B.make_request(C)
			if A and'id'in A:print(f"{Colors.SUCCESS}{Colors.CHECK} Group found: {Colors.BOLD}{A.get(_A,'Unknown')}{Colors.RESET}");print(f"{Colors.INFO}{Colors.ARROW} Group Description: {Colors.MUTED}{A.get(_C,'No description')}{Colors.RESET}");return _D
			return _B
		except Exception as D:print(f"{Colors.ERROR}{Colors.CROSS} Failed to validate group: {D}{Colors.RESET}");return _B
	async def get_user_info(B,user_id):
		'Get user info with caching and error handling';H='[Unknown]';D='created';A=user_id
		if A in B.user_cache:return B.user_cache[A]
		try:I=f"https://users.roblox.com/v1/users/{A}";C=await B.make_request(I);E={_K:C.get(_A,H),_G:C.get(_G,H),_H:C.get('id',A),D:C.get(D),_C:C.get(_C,'')};B.user_cache[A]=E;return E
		except Exception as F:print(f"{Colors.ERROR}{Colors.CROSS} Failed to fetch user {A}: {F}{Colors.RESET}");G={_K:f"[Error: {str(F)[:50]}]",_G:'[Error]',_H:A,D:_F,_C:''};B.user_cache[A]=G;return G
	async def fetch_users_in_role(E,role,quiet=_B):
		'Fetch all users in a specific role';B=role;H=[];M=f"https://groups.roblox.com/v1/groups/{E.group_id}/roles/{B['id']}/users";C='';print(f"{Colors.INFO}{Colors.ARROW} Processing Rank {B[_E]}: {Colors.BOLD}{B[_A]}{Colors.RESET}")
		try:
			with tqdm(desc=f"{Colors.CYAN}Processing {B[_A]}{Colors.RESET}",unit=' users',bar_format='{l_bar}%s{bar}%s{r_bar}'%(Colors.CYAN,Colors.MUTED))as N:
				while _D:
					I={'limit':100,'sortOrder':'Asc'}
					if C:I['cursor']=C
					O=M+'?'+'&'.join(f"{A}={B}"for(A,B)in I.items())
					try:
						J=await E.make_request(O);D=J.get('data',[])
						if not D:break
						K=5
						for L in range(0,len(D),K):
							P=D[L:L+K];Q=[E.get_user_info(A[_H])for A in P];R=await asyncio.gather(*Q,return_exceptions=_D);F=[]
							for A in R:
								if isinstance(A,Exception):print(f"{Colors.ERROR}{Colors.CROSS} Error fetching user: {A}{Colors.RESET}")
								else:F.append(A)
							H.extend(F)
							if not quiet:
								for A in F:print(f"{Colors.SUCCESS}{Colors.DOT} {A[_K]} ({A[_G]}) {Colors.MUTED}│{Colors.RESET} ID: {Colors.HIGHLIGHT}{A[_H]}{Colors.RESET}")
						N.update(len(D));C=J.get('nextPageCursor')
						if not C:break
						await asyncio.sleep(random.uniform(.5,1.5))
					except Exception as G:print(f"{Colors.ERROR}{Colors.CROSS} Failed to fetch users page for {B[_A]}: {G}{Colors.RESET}");break
		except Exception as G:print(f"{Colors.ERROR}{Colors.CROSS} Critical error processing role {B[_A]}: {G}{Colors.RESET}")
		return H
	async def get_group_roles(B,role_filter=_F):
		'Get all roles in the group';C=role_filter;E=f"https://groups.roblox.com/v1/groups/{B.group_id}/roles"
		try:
			print(f"{Colors.INFO}{Colors.ARROW} Fetching group roles from: {Colors.MUTED}{E}{Colors.RESET}");F=await B.make_request(E);D=F.get('roles',[])
			if not D:print(f"{Colors.WARNING}{Colors.CROSS} No roles found in group {B.group_id}{Colors.RESET}");return[]
			print(f"{Colors.SUCCESS}{Colors.CHECK} Found {len(D)} total roles{Colors.RESET}")
			if C:
				A=[A for A in D if A[_A].lower()==C.lower()]
				if not A:raise ValueError(f"Role '{C}' not found in group {B.group_id}")
				print(f"{Colors.INFO}{Colors.ARROW} Filtered to role: {Colors.BOLD}{C}{Colors.RESET}");return A
			A=[A for A in D if A[_E]>1];print(f"{Colors.INFO}{Colors.ARROW} Filtered to {len(A)} roles (rank > 1){Colors.RESET}");return A
		except Exception as G:print(f"{Colors.ERROR}{Colors.CROSS} Failed to fetch group roles: {G}{Colors.RESET}");raise
	def save_results(E,role_data,save_csv=_B):
		'Save results to JSON and optionally CSV';I='utf-8';A=role_data;B=''.join(A for A in A[_I]if A.isalnum()or A in(' ','-','_')).rstrip();B=B.replace(' ','_');F=datetime.now().strftime('%H%M_%d%m%Y');J=f"{B}_members_{F}.json";G=os.path.join(E.output_dir,J)
		try:
			with open(G,'w',encoding=I)as C:json.dump(A,C,ensure_ascii=_B,indent=2)
			D=_F
			if save_csv:
				K=f"{B}_members_{F}.csv";D=os.path.join(E.output_dir,K)
				with open(D,'w',encoding=I,newline='')as C:
					if A[_J]:L=list(A[_J][0].keys());H=csv.DictWriter(C,fieldnames=L);H.writeheader();H.writerows(A[_J])
			return G,D
		except Exception as M:print(f"{Colors.ERROR}{Colors.CROSS} Failed to save results for {A[_I]}: {M}{Colors.RESET}");raise
def parse_arguments():'Parse command line arguments';B='store_true';A=argparse.ArgumentParser(description='RX Hunt - Advanced Group Reconnaissance Tool',formatter_class=argparse.RawDescriptionHelpFormatter,epilog='\nExamples:\n  • python rx_hunt.py --group-id 12345\n  • python rx_hunt.py --group-id 12345 --role "Admin" --csv\n  • python rx_hunt.py --quiet --output ./intel --proxy\n\nUse environment variable GROUP_ID or --group-id argument\n        ');A.add_argument('--group-id',type=str,help='Roblox Group ID');A.add_argument('--role',type=str,help='Filter by specific role name');A.add_argument('--quiet',action=B,help='Show summary only');A.add_argument('--no-ascii',action=B,help='Disable ASCII art');A.add_argument('--output',type=str,default='~/storage/shared',help='Output directory');A.add_argument('--csv',action=B,help='Save output as CSV');A.add_argument('--verbose',action=B,help='Enable verbose logging');A.add_argument('--fast',action=B,help='Disable colors and ASCII art');A.add_argument('--proxy',action=B,help='Use proxy for requests (configure in .env)');A.add_argument('--validate-only',action=B,help='Only validate group ID and exit');return A.parse_args()
async def main():
	'Main function';P='right';O='memberCount';A=parse_arguments()
	if A.fast:
		for H in dir(Colors):
			if not H.startswith('_')and H.isupper():setattr(Colors,H,'')
	if A.verbose:logging.getLogger().setLevel(logging.DEBUG)
	load_dotenv();E=A.group_id or os.getenv('GROUP_ID')
	if not E:print(f"{Colors.ERROR}{Colors.CROSS} Error: Group ID is required. Set --group-id or GROUP_ID environment variable{Colors.RESET}");print(f"{Colors.INFO}Usage: python rx_hunt.py --group-id 12345{Colors.RESET}");return
	if not E.isdigit():print(f"{Colors.ERROR}{Colors.CROSS} Error: Group ID must be numeric{Colors.RESET}");return
	if not A.no_ascii and not A.fast:print(f"{ASCII_ART}")
	L=datetime.now();print(f"{Colors.INFO}{Colors.BOLD}Starting reconnaissance for Group ID: {Colors.HIGHLIGHT}{E}{Colors.RESET}");print(f"{Colors.MUTED}Started at {L.strftime('%H:%M %d-%m-%Y')}{Colors.RESET}");print(f"{Colors.MUTED}Output directory: {A.output}{Colors.RESET}")
	try:
		async with RobloxRecon(E,A.output,A.proxy)as F:
			print(f"{Colors.INFO}{Colors.ARROW} Validating group ID...{Colors.RESET}");Q=await F.validate_group_id()
			if not Q:print(f"{Colors.ERROR}{Colors.CROSS} Invalid group ID or unable to access group{Colors.RESET}");print(f"{Colors.INFO}Tips:{Colors.RESET}");print(f"  {Colors.DOT} Check if the group ID is correct");print(f"  {Colors.DOT} The group might be private or deleted");print(f"  {Colors.DOT} Try using --proxy flag if IP is blocked");return
			if A.validate_only:print(f"{Colors.SUCCESS}{Colors.CHECK} Group validation successful - exiting{Colors.RESET}");return
			print(f"{Colors.INFO}{Colors.ARROW} Fetching group roles...{Colors.RESET}");I=await F.get_group_roles(A.role)
			if not I:print(f"{Colors.WARNING}{Colors.CROSS} No roles found to process{Colors.RESET}");return
			print(f"{Colors.SUCCESS}{Colors.CHECK} Found {Colors.BOLD}{len(I)}{Colors.RESET}{Colors.SUCCESS} role(s) to process{Colors.RESET}");G=[];M=0
			for C in I:
				try:
					J=await F.fetch_users_in_role(C,A.quiet);M+=len(J);B={_I:C[_A],_E:C[_E],_C:C.get(_C,''),O:len(J),'fetchedAt':datetime.now().isoformat(),_J:J};G.append(B);R,N=F.save_results(B,A.csv);print(f"{Colors.SUCCESS}{Colors.CHECK} {Colors.BOLD}Success:{Colors.RESET} {Colors.HIGHLIGHT}{os.path.basename(R)}{Colors.RESET}")
					if N:print(f"{Colors.SUCCESS}{Colors.CHECK} {Colors.BOLD}Success:{Colors.RESET} {Colors.HIGHLIGHT}{os.path.basename(N)}{Colors.RESET}")
				except Exception as K:print(f"{Colors.ERROR}{Colors.CROSS} Failed to process role {C[_A]}: {K}{Colors.RESET}");continue
			if G:
				print(f"\n{Colors.ACCENT}┌───────────────────── Summary ─────────────────────┐{Colors.RESET}");D=Table(title='Member Distribution',box=box.ROUNDED,title_style=RichStyles.ACCENT,header_style=f"{RichStyles.ACCENT} {RichStyles.BOLD}",show_header=_D);D.add_column('Role',style=RichStyles.CYAN,justify='left');D.add_column('Rank',style=RichStyles.WARNING,justify=P);D.add_column('Members',style=RichStyles.SUCCESS,justify=P)
				for B in G:D.add_row(B[_I],str(B[_E]),str(B[O]))
				console.print(D);S=datetime.now();T=S-L;print(f"{Colors.SUCCESS}{Colors.BOLD}RECON COMPLETE:{Colors.RESET} {Colors.HIGHLIGHT}{M}{Colors.RESET} targets identified from {Colors.HIGHLIGHT}{len(G)}{Colors.RESET} roles in {Colors.INFO}{T}{Colors.RESET}");print(f"{Colors.ACCENT}└────────────────────────────────────────────────────┘{Colors.RESET}")
			else:print(f"{Colors.WARNING}{Colors.CROSS} No data was fetched{Colors.RESET}")
	except KeyboardInterrupt:print(f"{Colors.ERROR}{Colors.CROSS} Operation cancelled by user{Colors.RESET}")
	except Exception as K:print(f"{Colors.ERROR}{Colors.CROSS} Fatal error: {K}{Colors.RESET}");logger.exception('Detailed error information:')
if __name__=='__main__':asyncio.run(main())