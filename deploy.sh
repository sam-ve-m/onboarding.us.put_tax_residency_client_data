#!/bin/bash

export FISSION_ENVIRONMENT_NAME="env-put-tax-residence"
export FISSION_FUNCTION_NAME="fn-put-tax-residence"
export FISSION_FUNCTION_ROUTE="onboarding/external_fiscal_tax_confirmation"
export FISSION_FUNCTION_ROUTE_NAME="route-put-tax-residence"

echo "- Starting spec..."; fission spec init || { echo "ERROR: Failed to init spec. Message: Make sure the script is run only once, or run the remove_fission.sh script. [FINISHING SCRIPT]"; exit; }
echo "- Creating environment: $FISSION_ENVIRONMENT_NAME..."; fission env create --spec --name $FISSION_ENVIRONMENT_NAME --image nexus.sigame.com.br/fission-env-cx-async:0.0.1 --builder nexus.sigame.com.br/fission-builder-3.8:0.0.1 || { echo "ERROR: Failed to create environment. Message: Make sure the script is run only once, or run the remove_fission.sh script. [FINISHING SCRIPT]"; exit; }
echo "- Creating function: $FISSION_FUNCTION_NAME..."; fission fn create --spec --name $FISSION_FUNCTION_NAME --env $FISSION_ENVIRONMENT_NAME --src "./func/*" --entrypoint main.update_external_fiscal_tax --executortype newdeploy --maxscale 1 || { echo "ERROR: Failed to create function. Message: Make sure the script is run only once, or run the remove_fission.sh script. [FINISHING SCRIPT]"; exit; }
echo "- Creating HTTP trigger: $FISSION_FUNCTION_ROUTE..."; fission route create --spec --name $FISSION_FUNCTION_ROUTE_NAME --method PUT --url $FISSION_FUNCTION_ROUTE --function $FISSION_FUNCTION_NAME || { echo "ERROR: Failed to create route. Message: Make sure the script is run only once, or run the remove_fission.sh script. [FINISHING SCRIPT]"; exit; }
echo "Fission successfully configured!"