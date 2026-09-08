# Merchant Category Rules

This document maps MCC (Merchant Category Code) codes to risk profiles and specific processing rules.

## MCC 5411: Grocery Stores, Supermarkets
**Risk Profile**: Low.
**Rules**: Disputes for fraud are generally rare unless the physical card was stolen. Card-present transactions at grocery stores should almost always be considered legitimate unless clear evidence of theft is presented.

## MCC 4511: Airlines, Air Carriers
**Risk Profile**: High.
**Rules**: Extremely high risk for organized fraud rings. Often involves high-value transactions and card-not-present booking. Any 10.4 (Fraud) claim should be heavily scrutinized for geo-mismatches and IP anomalies.

## MCC 5310: Discount Stores
**Risk Profile**: Medium.
**Rules**: Susceptible to 13.1 (Not Received) claims. Requires proof of physical delivery to the cardholder's verified billing address to refute a claim.

## MCC 5815: Digital Goods, Media, Books, Movies, Music
**Risk Profile**: High.
**Rules**: "Friendly fraud" is rampant here. Users often buy digital goods, consume them instantly, and file a 10.4 (Fraud) or 13.1 (Not Received) claim. Analysts must demand strict IP login matching from the merchant. If the IP matches the user's known location, reject the 10.4 claim.

## MCC 5812: Eating Places, Restaurants
**Risk Profile**: Low.
**Rules**: Primarily card-present transactions. Susceptible to 12.6 (Duplicate Processing) if a waiter accidentally swipes a card twice or a tip is entered incorrectly.
