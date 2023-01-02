set -eu
if [[ ! -f "vendor/octo/.venv/bin/python3" ]]
then
    echo "Creating venv..."
    python3 -m venv vendor/octo/.venv
fi
vendor/octo/.venv/bin/pip install asn1crypto
vendor/octo/.venv/bin/pip install -r $PWD/vendor/octo/requirements.txt
export PREBUILTS=$(vendor/octo/.venv/bin/python3 -m vendor.octo.tools.prebuilts $PWD/vendor/octo/Prebuilts.yml)
export OCTO_PACKAGES="$PREBUILTS"
echo "Prebuilt packages: $OCTO_PACKAGES"
set +eu
###########  extendrom section ##########
export ENABLE_EXTENDROM=true
export EXTENDROM_PREROOT_BOOT=true
export EXTENDROM_PACKAGES="Magisk | SignMagisk"
$PWD/vendor/extendrom/get_prebuilts.sh