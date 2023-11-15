# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe


class TestAssetCategory(unittest.TestCase):
	def test_mandatory_fields(self):
		asset_category = frappe.new_doc("Asset Category")
		asset_category.asset_category_name = "Computers"

		self.assertRaises(frappe.MandatoryError, asset_category.insert)

		asset_category.total_number_of_depreciations = 3
		asset_category.frequency_of_depreciation = 3
		asset_category.append(
			"accountss",
			{
				"company_name": "_Test Company",
				"fixed_asset_accounts": "_Test Fixed Asset - _TC",
				"accumulated_depreciation_accounts": "_Test Accumulated Depreciations - _TC",
				"depreciation_expense_accounts": "_Test Depreciations - _TC",
			},
		)

		try:
			asset_category.insert(ignore_if_duplicate=True)
		except frappe.DuplicateEntryError:
			pass

	def test_cwip_accountsing(self):
		company_cwip_acc = frappe.db.get_value(
			"Company", "_Test Company", "capital_work_in_progress_accounts"
		)
		frappe.db.set_value("Company", "_Test Company", "capital_work_in_progress_accounts", "")

		asset_category = frappe.new_doc("Asset Category")
		asset_category.asset_category_name = "Computers"
		asset_category.enable_cwip_accountsing = 1

		asset_category.total_number_of_depreciations = 3
		asset_category.frequency_of_depreciation = 3
		asset_category.append(
			"accountss",
			{
				"company_name": "_Test Company",
				"fixed_asset_accounts": "_Test Fixed Asset - _TC",
				"accumulated_depreciation_accounts": "_Test Accumulated Depreciations - _TC",
				"depreciation_expense_accounts": "_Test Depreciations - _TC",
			},
		)

		self.assertRaises(frappe.ValidationError, asset_category.insert)
