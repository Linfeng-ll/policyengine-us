from policyengine_us.model_api import *


class oh_unreimbursed_medical_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Unreimbursed Medical and Health Care Expense Deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",  # Line 36
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(10)
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        employer_premium_contribution = person(
            "employer_premium_contribution", period
        )
        status = employer_premium_contribution.possible_values
        premiums_expenses = add(
            tax_unit, period, ["health_insurance_premiums"]
        )
        hipaid = select(
            [
                employer_premium_contribution == status.NONE,
                employer_premium_contribution == status.SOME,
                employer_premium_contribution == status.ALL,
                employer_premium_contribution == status.NA,
            ],
            [0, 0, 0, premiums_expenses],
        )
        medical_expenses = add(
            tax_unit, period, ["medical_out_of_pocket_expenses"]
        )
        # moop
        federal_agi = tax_unit("adjusted_gross_income", period)

        rate = parameters(
            period
        ).gov.states.oh.tax.income.deductions.unreimbursed_medical_care_expenses.rate
        adjusted_moop = max_(0, medical_expenses - federal_agi * rate)

        return hipaid + adjusted_moop
