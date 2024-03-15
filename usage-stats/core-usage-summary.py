#!/usr/bin/env python

import numpy as np
import pandas as pd
import argparse
import re
import os

pd.options.display.float_format = '{:,.2f}'.format


def init_parser():
	parser = argparse.ArgumentParser(
		description='Parses SLURM core hour usage, mam account and mam organization information to create Rivanna usage stats')
	parser.add_argument('-a', '--allocations', required=True, help='file with allocation information')
	parser.add_argument('-u', '--usage', required=True, help='file with core hour usage')
	parser.add_argument('-c', '--capacity', required=False, help='file with core and GPU device counts for each partition')
	parser.add_argument('-x', '--organizations', required=True, help='file with mam organization info')
	parser.add_argument('-o', '--output', required=True, help='output file')
	parser.add_argument('-g', '--groups', required=False, default='School')
	parser.add_argument('-d', '--days', required=True, help='reporting period in days')
	parser.add_argument('-l', '--labels', required=False, default='Allocation,Total CPU hours', help='comma separated list of core usage columns')
	parser.add_argument('-f', '--filter', required=True, help='filter')
	parser.add_argument('-p', '--path', required=False, help='file path')
	return parser


def calc_gpu_hours(row):
	if row['alloccpus'] != 0:
		return row['GPU devices'] * row['Total CPU hours'] / row['alloccpus']
	else:
		return 0.0


def job_type(row):
	jtype = row['JobName']
	if jtype.startswith('ood_'):
		jtype = f'interactive ({row["JobName"]})'
	elif jtype.startswith('sys/dashboard'):
		jtype = f'interactive (ood_{row["JobName"].split("/")[-1]})'
	elif 'interactive' in jtype:
		jtype = 'interactive (not OOD)'
	else:
		jtype = 'non-interactive slurm'
	jtype = jtype.replace('rstudio_server', 'rstudio')
	jtype = jtype.replace('jupyter_lab', 'jupyter')
	return jtype


def job_state(row):
	return row['state'].split(' ')[0]


def gpu_devices(row):
	pattern = r'gpu\:.*?\:(\d+)'
	matches = re.findall(pattern, row['GRES'])
	return sum(int(m) for m in matches)


def utilization(row, cap_dict):
	partition = row['partition']
	if 'gpu' in partition:
		util = row['Total GPU hours'] / (cap_dict[partition]['GPU hours'])
	else:
		util = row['Total CPU hours'] / (cap_dict[partition]['Core hours'])
	return util


def partition_type(row):
	if row['partition'] in ['instructional', 'eqa-cs5014-18sp']:
		return 'instructional'
	elif row['partition'] in ['standard', 'parallel', 'largemem', 'dev', 'gpu', 'knl']:
		return 'research'
	else:
		return 'condo'


def get_pi(row):
	members = row['Users']
	pi = members.split("^")[-1].split(",")[0]  
	return pi


def merge_data(labels, usage_file, account_file, org_file, capacity_file, hours, groups=['Allocation']):
	capacity_df = pd.read_csv(capacity_file, delimiter='|')
	capacity_df['GPU devices'] = capacity_df.apply(lambda row: gpu_devices(row), axis=1)  
	capacity_df = capacity_df.groupby(['PARTITION']).agg({"NODELIST": len, "CPUS": np.sum, "GPU devices": np.sum})
	capacity_df['Core hours'] = capacity_df['CPUS'] * hours
	capacity_df['GPU hours'] = capacity_df['GPU devices'] * hours
	cap_dict = capacity_df.to_dict('index')
	print(capacity_df)
	capacity_df.to_csv(f"{capacity_file[:-4]}-summary.csv")

	usage_df = pd.read_csv(usage_file, delimiter="|")  
	usage_df['Total CPU hours'] = usage_df['cputimeraw'] / 3600
	usage_df['GPU devices'] = usage_df['alloctres'].str.extract(r'gres/gpu=(\d+)').fillna(0).astype(
		int)  
	usage_df['Total GPU hours'] = usage_df.apply(lambda row: calc_gpu_hours(row), axis=1)
	usage_df['state'] = usage_df.apply(lambda row: job_state(row), axis=1)
	usage_df['JobType'] = usage_df.apply(lambda row: job_type(row), axis=1)
	usage_df['Utilization'] = usage_df.apply(lambda row: utilization(row, cap_dict), axis=1)
	usage_df['PartitionType'] = usage_df.apply(lambda row: partition_type(row), axis=1)

	usage_df = usage_df.drop(columns=["cputimeraw", "alloccpus", "GPU devices"])
	if "Utilization" in usage_df:
		usage_df = usage_df.drop(columns=["Utilization"])

	org_groups = [g for g in groups if g in usage_df.columns.values]
	usage_df = usage_df.groupby(org_groups).sum().reset_index()
	print(usage_df)

	org_df = pd.read_csv(org_file, delimiter=r"\s+", header=0, names=['Organization', 'School'])
	account_df = pd.read_csv(account_file, delimiter=r"\s+", header=0)
	cols = account_df.columns.values
	cols[0] = "Allocation"
	account_df.columns = cols
	account_df['PI'] = account_df.apply(lambda row: get_pi(row), axis=1)
	print(account_df)

	accts_and_orgs = pd.merge(account_df, org_df, on='Organization', how='outer', suffixes=('_left', '_right'))
	print(accts_and_orgs)
	combined = pd.merge(usage_df, accts_and_orgs, on='Allocation', how='left', suffixes=('_left', '_right'))
	print(combined)
	return combined


def save_df(df: pd.DataFrame, filepath=".", fname="rivanna-stats") -> None:
	path = os.path.join(filepath, fname)
	os.makedirs(filepath, exist_ok=True)
	df.to_csv(path, index=False)


def apply_filter(df: pd.DataFrame, filter_dict) -> pd.DataFrame:
	print (f"Applying filter {filter_dict} to columns={df.columns.values}")
	if "all" in filter_dict.keys():
		# nothing to do 
		return df
	# drop keys that don't exist in dataframe
	filter_dict = {k:v for k,v in filter_dict.items() if k in df.columns.values}

	if len(filter_dict) == 0:
		# filter column not present, nothing to do
		return pd.DataFrame(columns=df.columns.values)

	print (f"filter_dict={filter_dict}")
	if len(filter_dict) == 1:
		# filter by single column
		key_col = list(filter_dict.keys())[0]
		values = filter_dict[key_col]
		filtered_df = df[df[key_col].isin(values)] 
	else:
		# create multi-index from filter dict and dataframe -> keep overlap
		fvalue_list = [v for v in filter_dict.values()]
		filter_idx = pd.MultiIndex.from_product(fvalue_list, names=list(filter_dict)) 
		df_idx = pd.MultiIndex.from_frame(df[filter_dict.keys()])
		filtered_df = df.loc[df_idx.isin(filter_idx)]
	print (filtered_df.groupby(list(filter_dict)).sum(numeric_only=True))
	return filtered_df


def parse_filter(farg: str) -> list:
	"""Example:
	    in:
		"School:[DS,EN,MD];Description:[standard,purchase]|Status:[Staff,Faculty]"

		out: list of dict
		[
			{
				'School': ['DS', 'EN', 'MD'], 
				'Description': ['standard', 'purchase']
			}, 
			{
				'Status': ['Staff', 'Faculty']
			}
		]
	"""
	filters = farg.split("|")
	filter_list = []
	for f in filters:
		items = f.split(";")
		fd = {}
		for item in items:
			kv = item.split(":")
			if len(kv) > 1:
				fd[kv[0]] = kv[1].replace("[", "").replace("]", "").split(",")
			else:
				fd[kv[0]] = None
		filter_list.append(fd) 
	if not any("all" in d for d in filter_list):
		filter_list.append({"all":None})
	return filter_list    


if __name__ == '__main__':
	parser = init_parser()
	args = parser.parse_args()
	filters = parse_filter(args.filter)
	agroups = list(set(args.groups.replace('|', ',').split(',')))
	if 'Allocation' not in agroups:
		agroups.append('Allocation')
	analysis = args.groups.split('|')
	hours = float(args.days) * 24
	df = merge_data(args.labels, args.usage, args.allocations, args.organizations, args.capacity, hours, groups=agroups)
	filters = parse_filter(args.filter)

	for r in analysis:
		print(''.join(["#"] * 80))
		groups = r.split(',') if args.groups != '' else ['Allocation']
		print(f'Analyzing by {r}, {groups}')
		for filter in filters:
			print (f"Filtering by {filter}")
			sum_df = df.groupby(groups).sum().reset_index()  
			ftrunk, ext = os.path.splitext(args.output)
			# flatten filter values which is a list of lists
			if list(filter.values())[0] is not None:
				f_values = [v for values in filter.values() for v in values]
				filter_str = "-".join(f_values)
			else:
				filter_str = "-".join(filter.keys())
			print (f"filter_str={filter_str}")
			filepath = args.path.replace("{FILTER}", filter_str)
			fname = f"{ftrunk}-{''.join(groups)}-{filter_str}{ext}"
			print(f"filepath={filepath}, fname={fname}")
			filtered_df  = apply_filter(sum_df, filter)
			save_df(filtered_df, filepath=filepath, fname=fname)
			
			print(filtered_df)
			print("------------------------------------")
			print(f"Total CPU Hours: {filtered_df['Total CPU hours'].sum():,.2f}")
			print(f"Total GPU Device Hours: {filtered_df['Total GPU hours'].sum():,.2f}")
			
			groups = r.split(',') if args.groups != '' else ['User']
