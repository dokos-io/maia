# coding=utf-8
from __future__ import unicode_literals, absolute_import
import click
from subprocess import Popen, check_output, PIPE, STDOUT
import os, shlex
import json
import frappe

@click.command('maia-new-site')
def _maia_new_site():
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


def create_new_site(first_name, last_name, email, siteprefix, max_users, customer, mariadb_root_user, mariadb_password, admin_password):
	site_name = siteprefix + '.maia-by-dokos.fr'
	db_name = 'dokos-' + siteprefix[:10]
	print(db_name)

	create_db_and_site(site_name, db_name, mariadb_root_user, mariadb_password, admin_password)
	print("==========> DB and Site Successfully Created")
	install_maia(site_name)
	print("==========> Maia Installed")
	setup_site(site_name)
	print("==========> Parameters for France Set")
	add_system_manager_and_limits(site_name, email, first_name, last_name, max_users)
	print("==========> System Manager and Limits Set")
	add_specific_config(site_name, customer)
	print("==========> Specific Config Added")
	add_to_lets_encrypt_file(site_name)
	print("==========> Let's Encrypt File Updated")

	setup_and_reload_nginx()
	print("==========> Installation Successful")


def create_db_and_site(site_name, db_name, mariadb_root_user, mariadb_password, admin_password):
	commands = []

	command = "bench new-site {site_name} --db-name {db_name} --mariadb-root-username {db_root_username} --mariadb-root-password {db_root_password} --admin-password {admin_password} --verbose".format(site_name=site_name, db_name=db_name, db_root_username=mariadb_root_user, db_root_password=mariadb_password, admin_password=admin_password)
	commands.append(command)

	run_commands(commands)

def install_maia(site_name):
	commands = []

	command = "bench --site {site_name} install-app maia".format(site_name=site_name)
	commands.append(command)

	run_commands(commands)

def setup_site(site_name):
	frappe.connect(site=site_name)
	try:
		frappe.db.set_value('System Settings', None, 'country', 'France')
		frappe.db.set_value('System Settings', None, 'language', 'fr')
		frappe.db.set_value('System Settings', None, 'time_zone', 'heure:France-Europe/Paris')
		frappe.get_doc(dict(doctype='Domain', domain='Sage-Femme')).insert(ignore_permissions=True)

		frappe.db.commit()
	except Exception as e:
		print(e)
	finally:
		frappe.destroy()

def add_system_manager_and_limits(site_name, email, first_name, last_name, max_users):
	commands = []

	command = "bench --site {site_name} set-limits --limit users {max_users} --limit space 5".format(site_name=site_name, max_users=max_users)
	commands.append(command)

	run_commands(commands)

	frappe.connect(site=site_name)
	try:
		add_system_manager(email=email, first_name=first_name, last_name=last_name, send_welcome_email=True)
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

def add_system_manager(email, first_name=None, last_name=None, send_welcome_email=False):
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

def run_commands(commands):
	bench_path = frappe.utils.get_bench_path()
	try:
		for command in commands:
			terminal_action = Popen(shlex.split(command.encode('utf8')), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=bench_path)
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

commands = [_maia_new_site]
