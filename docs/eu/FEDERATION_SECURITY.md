# Federatutako segurtasuna (2. fasea)

## Konfiantza eredua

- Nodoaren identitatea = domeinua + TLS ziurtagiria.
- mTLS bidezko elkarreko peering domeinu-ziurtagiriekin (CA publikoa/pribatua).
- TLS beharrezkoa nodoen artean; balioztapen zorrotza (self-signed ez prod-en).

## Biraketa eta indargabetzea

- Biraketa/indargabetzea ziurtagiri-berritzearen bidez kudeatzen da.
- Komprometitutako nodoa indargabetzen da bere ziurtagiria eta direktorio-sarrera baliogabetuz.

## Motibazioa

Nodoen ordezkapena saihestu eta federazioan egiaztatutako instantziak bakarrik parte har dezaten ziurtatu.

## Doikuntzak

- `allowlist`/`blocklist` nodoaren arabera (`node_policies`).
- Rate limiting eta anti-flood federazioaren ertzean.
- Moderazio-txostenen propagazioa nodoen artean.