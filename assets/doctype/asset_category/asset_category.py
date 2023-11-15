# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, get_link_to_form


class AssetCategory(Document):
	def validate(self):
		self.validate_finance_books()
		self.validate_accounts_types()
		self.validate_accounts_currency()
		self.valide_cwip_accounts()

	def validate_finance_books(self):
		for d in self.finance_books:
			for field in ("Total Number of Depreciations", "Frequency of Depreciation"):
				if cint(d.get(frappe.scrub(field))) < 1:
					frappe.throw(
						_("Row {0}: {1} must be greater than 0").format(d.idx, field), frappe.MandatoryError
					)

	def validate_accounts_currency(self):
		accounts_types = [
			"fixed_asset_accounts",
			"accumulated_depreciation_accounts",
			"depreciation_expense_accounts",
			"capital_work_in_progress_accounts",
		]
		invalid_accountss = []
		for d in self.accountss:
			company_currency = frappe.get_value("Company", d.get("company_name"), "default_currency")
			for type_of_accounts in accounts_types:
				if d.get(type_of_accounts):
					accounts_currency = frappe.get_value("Accounts", d.get(type_of_accounts), "accounts_currency")
					if accounts_currency != company_currency:
						invalid_accountss.append(
							frappe._dict({"type": type_of_accounts, "idx": d.idx, "accounts": d.get(type_of_accounts)})
						)

		for d in invalid_accountss:
			frappe.throw(
				_("Row #{}: Currency of {} - {} doesn't matches company currency.").format(
					d.idx, frappe.bold(frappe.unscrub(d.type)), frappe.bold(d.accounts)
				),
				title=_("Invalid Accounts"),
			)

	def validate_accounts_types(self):
		accounts_type_map = {
			"fixed_asset_accounts": {"accounts_type": ["Fixed Asset"]},
			"accumulated_depreciation_accounts": {"accounts_type": ["Accumulated Depreciation"]},
			"depreciation_expense_accounts": {"accounts_type": ["Depreciation"]},
			"capital_work_in_progress_accounts": {"accounts_type": ["Capital Work in Progress"]},
		}
		for d in self.accountss:
			for fieldname in accounts_type_map.keys():
				if d.get(fieldname):
					selected_accounts = d.get(fieldname)
					key_to_match = next(iter(accounts_type_map.get(fieldname)))  # acounts_type or root_type
					selected_key_type = frappe.db.get_value("Accounts", selected_accounts, key_to_match)
					expected_key_types = accounts_type_map[fieldname][key_to_match]

					if selected_key_type not in expected_key_types:
						frappe.throw(
							_(
								"Row #{}: {} of {} should be {}. Please modify the accounts or select a different accounts."
							).format(
								d.idx,
								frappe.unscrub(key_to_match),
								frappe.bold(selected_accounts),
								frappe.bold(expected_key_types),
							),
							title=_("Invalid Accounts"),
						)

	def valide_cwip_accounts(self):
		if self.enable_cwip_accountsing:
			missing_cwip_accountss_for_company = []
			for d in self.accountss:
				if not d.capital_work_in_progress_accounts and not frappe.db.get_value(
					"Company", d.company_name, "capital_work_in_progress_accounts"
				):
					missing_cwip_accountss_for_company.append(get_link_to_form("Company", d.company_name))

			if missing_cwip_accountss_for_company:
				msg = _("""To enable Capital Work in Progress Accountsing,""") + " "
				msg += _("""you must select Capital Work in Progress Accounts in accountss table""")
				msg += "<br><br>"
				msg += _("You can also set default CWIP accounts in Company {}").format(
					", ".join(missing_cwip_accountss_for_company)
				)
				frappe.throw(msg, title=_("Missing Accounts"))


def get_asset_category_accounts(
	fieldname, item=None, asset=None, accounts=None, asset_category=None, company=None
):
	if item and frappe.db.get_value("Item", item, "is_fixed_asset"):
		asset_category = frappe.db.get_value("Item", item, ["asset_category"])

	elif not asset_category or not company:
		if accounts:
			if frappe.db.get_value("Accounts", accounts, "accounts_type") != "Fixed Asset":
				accounts = None

		if not accounts:
			asset_details = frappe.db.get_value("Asset", asset, ["asset_category", "company"])
			asset_category, company = asset_details or [None, None]

	accounts = frappe.db.get_value(
		"Asset Category Accounts",
		filters={"parent": asset_category, "company_name": company},
		fieldname=fieldname,
	)

	return accounts
