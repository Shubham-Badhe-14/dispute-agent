# Precedent Cases

Historical examples of tricky edge cases and how they should be resolved.

## Precedent Case 1: High-Value International Fraud
**Scenario**: User from MK disputes a $2500 transaction in US at MCC 4511 (Airlines) under Reason Code 10.4.
**Resolution**: Rule in favor of the cardholder (Approve Dispute). The geo-mismatch (MK vs US) combined with a high-value card-not-present transaction at a high-risk MCC is a textbook indicator of true fraud.

## Precedent Case 2: Digital Goods Friendly Fraud
**Scenario**: User from US disputes a $150 transaction at MCC 5815 (Digital Goods) under Reason Code 10.4. The transaction was made from an IP address matching their home city, and the user has an account age of > 1000 days.
**Resolution**: Reject the dispute. The IP match on a digital good, combined with a mature account, strongly suggests friendly fraud. The user likely made the purchase and regrets it, falsely claiming fraud.

## Precedent Case 3: Accidental Duplicate
**Scenario**: User disputes a $45.00 charge at MCC 5812 (Restaurants) under Reason Code 12.6. A nearly identical $45.00 charge exists 2 minutes prior.
**Resolution**: Rule in favor of the cardholder (Approve Dispute). Rapid consecutive charges for the exact same amount at a restaurant are almost always point-of-sale terminal errors.
