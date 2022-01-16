########### extendrom section ###########
export ENABLE_EXTENDROM=true
# not yet :(
export EXTENDROM_PREROOT_BOOT=false
export EXTENDROM_PACKAGES="F-DroidPrivilegedExtension"
# $PWD/vendor/extendrom/get_prebuilts.sh
export OCTO_PACKAGES=$(python3 -m vendor.octo.tools.prebuilts $PWD/vendor/octo/Prebuilts.yml)