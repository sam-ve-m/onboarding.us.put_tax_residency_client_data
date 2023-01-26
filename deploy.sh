fission spec init
fission env create --spec --name onb-us-tax-resd-env --image nexus.sigame.com.br/fission-onboarding-us-tax-residency:0.1.3-0 --poolsize 2 --graceperiod 3 --version 3 --imagepullsecret "nexus-v3" --spec
fission fn create --spec --name onb-us-tax-resd-fn --env onb-us-tax-resd-env --code fission.py --executortype poolmgr --requestsperpod 10000 --spec
fission route create --spec --name onb-us-tax-resd-rt --method PUT --url /onboarding/external_fiscal_tax_confirmation --function onb-us-tax-resd-fn