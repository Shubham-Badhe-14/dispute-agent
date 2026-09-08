# Chargeback Reason Codes

This document outlines the strict definitions and required evidence for Visa/Mastercard style chargeback reason codes.

## Reason Code 10.4: Fraud
**Definition**: Cardholder states they did not authorize or participate in the transaction. This is the most common reason code for stolen cards or compromised credentials.
**Risk Factors**: High-value transactions, international transactions where the merchant country does not match the cardholder's home country, and card-not-present (CNP) transactions.
**Required Analyst Action**: Check for IP/Geo mismatches, unusual velocity (multiple rapid transactions), and AVS (Address Verification System) failures. If the transaction matches the user's home country and the card was present, scrutinize heavily as it may be "friendly fraud."

## Reason Code 12.6: Duplicate Processing
**Definition**: The cardholder was charged more than once for the same transaction.
**Risk Factors**: Transactions occurring at the same merchant, for the exact same amount, within a very short time window (e.g., minutes apart).
**Required Analyst Action**: Verify if multiple identical charges exist on the account within a short timeframe. If so, rule in favor of the cardholder for the duplicate charge.

## Reason Code 13.1: Merchandise/Services Not Received
**Definition**: The cardholder authorized the transaction, but the merchant failed to provide the goods or services.
**Risk Factors**: High risk for digital goods (MCC 5815) where delivery is instantaneous but disputed, or retail goods (MCC 5310) shipped to an unverified address.
**Required Analyst Action**: Check shipping logs or digital download confirmations. If the merchant category is high-risk for delivery failures, weight the evidence accordingly.
