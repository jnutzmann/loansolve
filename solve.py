import sys
import json
from datetime import datetime, timedelta

PAYMENT_START = datetime(2015, 8, 1)

# Assumptions that make paying the highest interest loan first correct
# 1) min payments on the other loans do not exist
# 2) compounding interest is tricky...


# when loan is paid off, no min payment exists (increases available funds)
# not paying full interest on loans increases their principal
# the longer you have the loans, the more capitalization matters


def print_loan(loan):
    print("\t[%s] Principal: %0.2f, Interest: %0.2f" % (loan["name"], loan["principal"], loan["interest"]))


def solve(loans, monthly_payment):

    day = datetime.now()

    loans.sort(key=lambda x: x["interest_rate"])

    total_paid = 0

    while True:
        monthly_budget = monthly_payment
        month = day.month

        complete_loans = []

        total = 0
        for l in loans:
            total += l["principal"] + l["interest"]

        print("\n== %i / %i == %i" % (day.month, day.year, total))

        while day.month == month:

            for l in range(len(loans)):

                loan = loans[l]

                # If the loan is paid off, do nothing
                if loan["principal"] <= 0 and loan["interest"] <= 0:
                    if l not in complete_loans:
                        complete_loans.append(l)
                    continue

                # If interest has started on loan, then calculate it.
                if day >= loan["interest_starts"]:
                    loan["interest"] += loan["principal"] * loan["interest_rate"] / 36500

                # Capitalize if necessary
                if loan["next_capitalization"] <= day:
                    loan["principal"] += loan["interest"]
                    loan["interest"] = 0
                    loan["next_capitalization"] += timedelta(days=loan["capitalization_frequency_days"])

                # Pay the minimum payment if necessary
                if day >= PAYMENT_START and day >= loan["min_payment_starts"] and day.day == loan["minimum_payment_dom"]:
                    monthly_budget += pay_loan(loan, loan["minimum_payment"])
                    print("\t[%s] %i MIN PAYMENT %0.2f" % (loan["name"], day.day, loan["minimum_payment"]))

            day += timedelta(days=1)

        complete_loans.sort(reverse=True)

        for l in complete_loans:
            complete = loans.pop(l)

            print("!! LOAN COMPLETED %s !!" % complete["name"])

        if day >= PAYMENT_START:

            index = 1

            while monthly_budget > 0 and index <= len(loans):
                payment_target = monthly_budget
                monthly_budget = pay_loan(loans[len(loans)-index], monthly_budget)
                index += 1
                print("\t[%s] %i ADDL PAYMENT %0.2f" % (loan["name"], day.day, payment_target-monthly_budget))

            total_paid += monthly_payment - monthly_budget

        if len(loans) == 0:

            print("==== TOTAL_PAID = %0.2f ====" % total_paid)
            break

        for l in loans:
            print_loan(l)


def pay_loan(loan, amount):
    if amount <= loan["interest"]:
        loan["interest"] -= amount
    else:
        amount -= loan["interest"]
        loan["interest"] = 0

        if amount <= loan["principal"]:
            loan["principal"] -= amount
        else:
            amount -= loan["principal"]
            loan["principal"] = 0
            return amount

    return 0


def main():

    with open(sys.argv[1]) as f:
        loans = json.load(f)

    date_fields = ["interest_starts", "min_payment_starts", "next_capitalization"]
    for loan in loans:
        for f in date_fields:
            loan[f] = datetime.strptime(loan[f], "%m/%d/%Y")
        loan["last_payment"] = 0

    solve(loans, int(sys.argv[2]))

if __name__ == "__main__":
    main()
