# coding=utf-8
# Copyright (c) 2019, Dokos and Contributors
# See license.txt
from __future__ import unicode_literals, absolute_import
import click
from subprocess import Popen, check_output, PIPE, STDOUT
import os, shlex
import json
import frappe
from frappe.commands import pass_context, get_site

@click.command('maia-new-site')
def maia_new_site():
	first_name = click.prompt('First Name')
	last_name = click.prompt('Last Name')
	email = click.prompt('Email')
	siteprefix = click.prompt('Site Prefix')
	max_users = click.prompt('Number of Users')
	customer = click.prompt('SMS Customer')
	mariadb_root_user = click.prompt('Mariadb Root Username')
	mariadb_password = click.prompt('Mariadb Root Password')
	admin_password = click.prompt('Admin Password')

	if click.confirm('Register '+ first_name + ' ' + last_name + ' - ' + email + ' - ' + siteprefix + ' - '+ max_users + ' - ' + customer +' ?', abort=True):
		click.echo('New Site Creation Started')

		create_new_site(first_name, last_name, email, siteprefix, max_users, customer, mariadb_root_user, mariadb_password, admin_password)

@click.command('maia-reinstall-site')
@click.option('--site', help='site name')
@pass_context
def maia_reinstall_site(context, site):
	first_name = click.prompt('First Name')
	last_name = click.prompt('Last Name')
	email = click.prompt('Email')
	mariadb_root_user = click.prompt('Mariadb Root Username')
	mariadb_password = click.prompt('Mariadb Root Password')
	admin_password = click.prompt('Admin Password')

	if click.confirm('Reinstall and register '+ first_name + ' ' + last_name + ' - ' + email + ' ?', abort=True):
		click.echo('Site Reinstallation Started')

		site = get_site(context)

		reinstall_site(site, first_name, last_name, email, mariadb_root_user, mariadb_password, admin_password)

@click.command('make-maia-demo')
@click.option('--site', help='site name')
@click.option('--reinstall', default=False, is_flag=True, help='Reinstall site before demo')
@pass_context
def make_maia_demo(context, site, reinstall=False):
	"Reinstall site and setup demo"
	from frappe.commands.site import _reinstall
	from frappe.installer import install_app

	site = get_site(context)

	if reinstall:
		_reinstall(site, yes=True)
	with frappe.init_site(site=site):
		frappe.connect()
		if not 'maia' in frappe.get_installed_apps():
			install_app('maia')

		# import needs site
		from maia.demo import demo
		demo.make()


def create_new_site(first_name, last_name, email, siteprefix, max_users, customer, mariadb_root_user, mariadb_password, admin_password):
	site_name = siteprefix + '.maia-by-dokos.fr'
	db_name = 'dokos-' + siteprefix[-10:]
	print("==========> DB name: " + db_name)

	check_prerequisites()
	print("==========> Prerequisites checked")

	create_db_and_site(site_name, db_name, mariadb_root_user, mariadb_password, admin_password)
	print("==========> DB and Site Successfully Created")
	add_specific_config(site_name, customer)
	print("==========> Specific Config Added")
	add_limits(site_name, first_name, last_name, max_users)
	print("==========> Limits Set")

	install_maia(site_name)
	print("==========> Maia Installed")

	add_system_manager(site_name, email, first_name, last_name, True)
	print("==========> System Manager Added")

	add_professional_information_card(site_name, email, first_name, last_name)
	print("==========> Professional Information Card Added")

	add_to_lets_encrypt_file(site_name)
	print("==========> Let's Encrypt File Updated")

	setup_and_reload_nginx()
	print("==========> Installation Successful")

def reinstall_site(site_name, first_name, last_name, email, mariadb_root_user, mariadb_password, admin_password):
	force_reinstall_db(site_name, mariadb_root_user, mariadb_password, admin_password)
	print("==========> Site reinstalled")

	add_system_manager(site_name, email, first_name, last_name, False)
	print("==========> System Manager Added")

	add_professional_information_card(site_name, email, first_name, last_name)
	print("==========> Professional Information Card Added")

	setup_and_reload_nginx()
	print("==========> Installation Successful")

def check_prerequisites():
	bench_path = frappe.utils.get_bench_path()
	config_path = os.path.join(bench_path, 'sites', 'common_site_config.json')

	if not os.path.exists(config_path):
		config = {}
	with open(config_path, 'r') as f:
		config = json.load(f)

	if not config.get("sendinblue_key"):
		click.confirm('sendinblue_key key missing in common_site.json. Do you want to continue ?', abort = True)

def create_db_and_site(site_name, db_name, mariadb_root_user, mariadb_password, admin_password):
	commands = []

	command = "bench new-site {site_name} --db-name {db_name} --mariadb-root-username {db_root_username} --mariadb-root-password {db_root_password} --admin-password {admin_password} --verbose".format(site_name=site_name, db_name=db_name, db_root_username=mariadb_root_user, db_root_password=mariadb_password, admin_password=admin_password)
	commands.append(command)

	run_commands(commands)

def force_reinstall_db(site, mariadb_root_user, mariadb_password, admin_password):
	commands = []

	command = "bench --site {site} --force reinstall --mariadb-root-username {db_root_username} --mariadb-root-password {db_root_password} --admin-password {admin_password} --yes".format(site=site, db_root_username=mariadb_root_user, db_root_password=mariadb_password, admin_password=admin_password)
	commands.append(command)

	run_commands(commands)

def install_maia(site_name):
	commands = []

	command = "bench --site {site_name} install-app maia".format(site_name=site_name)
	commands.append(command)

	run_commands(commands)

def add_limits(site_name, first_name, last_name, max_users):
	commands = []

	command = "bench --site {site_name} set-limits --limit users {max_users} --limit space 5".format(site_name=site_name, max_users=max_users)
	commands.append(command)

	run_commands(commands)

def add_system_manager(site_name, email, first_name, last_name, welcome_email=False):
	frappe.connect(site=site_name)
	try:
		create_system_manager(email=email, first_name=first_name, last_name=last_name, send_welcome_email=welcome_email)
		frappe.db.commit()
	except Exception as e:
		print(e)
	finally:
		frappe.destroy()

def add_professional_information_card(site_name, email, first_name, last_name):
	frappe.connect(site=site_name)
	try:
		create_professional_information_card(email=email, first_name=first_name, last_name=last_name)
		frappe.db.commit()
	except Exception as e:
		print(e)
	finally:
		frappe.destroy()

def add_specific_config(site_name, customer):
	bench_path = frappe.utils.get_bench_path()
	hostname = "https://{}".format(site_name)
	customer_config = {"customer": customer, "host_name": hostname}
	update_site_config(site_name, customer_config, bench_path)

def add_domain(site_name):
	commands = []

	command = "bench setup add-domain {domain} --site {site_name}".format(site_name=site_name, domain=site_name)
	commands.append(command)

	run_commands(commands)

def add_to_lets_encrypt_file(site_name):
	bench_path = frappe.utils.get_bench_path()
	f = open(os.path.join(bench_path, 'certificates.txt'), 'a+')
	f.write("{}\n".format(site_name))
	f.close()

def setup_and_reload_nginx():
	commands = []

	command = "bench setup nginx --yes"
	commands.append(command)

	command = "sudo service nginx reload"
	commands.append(command)

	run_commands(commands)

def create_system_manager(email, first_name=None, last_name=None, send_welcome_email=False):
	# add user
	language = frappe.get_single("System Settings").language
	frappe.local.lang = language

	user = frappe.get_doc({
		"doctype": "User",
		"name": email,
		"email": email,
		"language": "fr",
		"enabled": 1,
		"first_name": first_name or email,
		"last_name": last_name,
		"user_type": "System User",
		"send_welcome_email": 1 if send_welcome_email else 0
	})
	user.insert(ignore_permissions=True)

	# add roles
	roles = frappe.db.sql_list("""select name from `tabRole`
		where name not in ("Administrator", "Guest", "All")""")
	user.add_roles(*roles)

	#Add default forward email
	frappe.db.set_value("Contact Us Settings", None, "forward_to_email", user.name)

def create_professional_information_card(email, first_name=None, last_name=None):
	prof_card = frappe.get_doc({
		"doctype": "Professional Information Card",
		"user": email,
		"email": email,
		"first_name": first_name,
		"last_name": last_name
	})
	prof_card.insert(ignore_permissions=True, ignore_mandatory=True)

def run_commands(commands):
	bench_path = frappe.utils.get_bench_path()

	try:
		for command in commands:
			terminal_action = Popen(shlex.split(frappe.safe_decode(command)), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=frappe.safe_decode(bench_path))
			return_ = terminal_action.wait()

	except Exception as e:
		print(e)

def get_site_config(site, bench_path='.'):
	config_path = os.path.join(bench_path, 'sites', site, 'site_config.json')
	if not os.path.exists(config_path):
		return {}
	with open(config_path) as f:
		return json.load(f)

def put_site_config(site, config, bench_path='.'):
	config_path = os.path.join(bench_path, 'sites', site, 'site_config.json')
	with open(config_path, 'w') as f:
		return json.dump(config, f, indent=1)

def update_site_config(site, new_config, bench_path='.'):
	config = get_site_config(site, bench_path=bench_path)
	config.update(new_config)
	put_site_config(site, config, bench_path=bench_path)

commands = [maia_new_site, maia_reinstall_site, make_maia_demo]