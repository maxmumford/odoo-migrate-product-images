#! /usr/bin/python
import argparse
import openerplib
from copy import copy

description = """This script will connect to the source server and for each product will look for a 
corresponding product in the target server, download the image, and upload it to the target server."""

# define arguments
parser = argparse.ArgumentParser(description)

parser.add_argument('--source-database', type=str, help='[SOURCE] Name of database to connect to')
parser.add_argument('--source-hostname', type=str, help='[SOURCE] Hostname of the OpenERP server', default='localhost')
parser.add_argument('--source-port', type=int, help='[SOURCE] RPC port of the OpenERP server', default=0)
parser.add_argument('--source-protocol', type=str, help='[SOURCE] The protocol used by the RPC connection', default='xmlrpc')
parser.add_argument('--source-username', type=str, help='[SOURCE] Username to connect to the OpenERP server', default='admin')
parser.add_argument('--source-password', type=str, help='[SOURCE] Password to connect to the OpenERP server', default='admin')
parser.add_argument('--source-saas', type=bool, help="[SOURCE] If connecting to SaaS, automatically set appropriate port and protocol", default=False)
parser.add_argument('--source-product-model', type=str, help='[SOURCE] The product model - usually product.product or product.template', default="product.product")

parser.add_argument('--target-database', type=str, help='[TARGET Name of database to connect to')
parser.add_argument('--target-hostname', type=str, help='[TARGET] Hostname of the OpenERP server', default='localhost')
parser.add_argument('--target-port', type=int, help='[TARGET] RPC port of the OpenERP server', default=0)
parser.add_argument('--target-protocol', type=str, help='[TARGET] The protocol used by the RPC connection', default='xmlrpc')
parser.add_argument('--target-username', type=str, help='[TARGET] Username to connect to the OpenERP server', default='admin')
parser.add_argument('--target-password', type=str, help='[TARGET] Password to connect to the OpenERP server', default='admin')
parser.add_argument('--target-saas', type=bool, help="[TARGET] If connecting to SaaS, automatically set appropriate port and protocol", default=False)
parser.add_argument('--target-product-model', type=str, help='[TARGET] The product model - usually product.product or product.template', default="product.product")

# parse arguments
args = parser.parse_args()

# handle saas option
if args.source_saas:
        args.source_protocol = 'xmlrpcs'
        args.source_port = 443

if args.target_saas:
        args.target_protocol = 'xmlrpcs'
        args.target_port = 443

# open connections to each
source_conn = openerplib.get_connection(hostname=args.source_hostname, database=args.source_database, login=args.source_username, password=args.source_password, port=args.source_port or 'auto', protocol=args.source_protocol)
try:
	source_conn.check_login()
except Exception as e:
	print "Could not connect to source server"
	raise

target_conn = openerplib.get_connection(hostname=args.target_hostname, database=args.target_database, login=args.target_username, password=args.target_password, port=args.target_port or 'auto', protocol=args.target_protocol)
try:
	target_conn.check_login()
except Exception as e:
	print "Could not connect to target server"
	raise

# get products from source
source_product_obj = source_conn.get_model(args.source_product_model)
source_imd_obj = source_conn.get_model('ir.model.data')

source_product_ids = source_product_obj.search([])
source_product_imd_ids = source_imd_obj.search([('model', '=', args.source_product_model), ('res_id', 'in', source_product_ids)])
source_product_imds = source_imd_obj.read(source_product_imd_ids, ['name', 'module', 'res_id'])

# get products from target
target_product_obj = target_conn.get_model(args.target_product_model)
target_imd_obj = target_conn.get_model('ir.model.data')

target_product_ids = target_product_obj.search([])
target_product_imd_ids = target_imd_obj.search([('model', '=', args.target_product_model), ('res_id', 'in', target_product_ids)])
target_product_imds = target_imd_obj.read(target_product_imd_ids, ['name', 'module', 'res_id'])
target_product_imd_names = [imd['name'] for imd in target_product_imds]

# get products common to both instances
common_product_imds = []
for source_product_imd in copy(source_product_imds):
	for target_product_imd in target_product_imds:
		if source_product_imd['name'] == target_product_imd['name']:
			common_product_imds.append({'name': source_product_imd['name'], 'source': source_product_imd, 'target': target_product_imd})

# for each common product, download the image and upload it to the target
for common_product_imd in common_product_imds:
	image = source_product_obj.read(common_product_imd['source']['res_id'], ['image_medium'])['image_medium']
	target_product_obj.write(common_product_imd['target']['res_id'], {'image_medium': image})
	print 'Done product %d' % common_product_imd['target']['res_id']

print "Finished :)"
