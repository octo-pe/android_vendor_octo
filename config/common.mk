# Enable overlays
DEVICE_PACKAGE_OVERLAYS += \
	vendor/octo/overlays
# Load prebuilts
ifdef OCTO_PACKAGES
PRODUCT_PACKAGES += $(OCTO_PACKAGES)
endif
# Add F-DroidPrivilegedExtension
PRODUCT_PACKAGES += F-DroidPrivilegedExtension 
# Enable extendrom
$(call inherit-product-if-exists, vendor/extendrom/config/common.mk)
# Enable PLE
PIXEL_LAUNCHER_VARIANT := nomod2
ICONS_VARIANT := teamfilesicons
$(call inherit-product, vendor/PixelLauncherExtended/PixelLauncher.mk)
ifneq ($(filter OCTO NIS,$(CUSTOM_BUILD_TYPE)),)
$(warning Enabling updater.)
# Include updater app
PRODUCT_PACKAGES += \
    S3Updater
# Include SELinux policies for updater
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += \
    vendor/octo/apps/S3Updater/sepolicy
# Versioning props
PRODUCT_SYSTEM_PROPERTIES  += \
    ro.s3updater.build.version=$(CUSTOM_PLATFORM_VERSION) \
    ro.s3updater.releasetype=$(CUSTOM_BUILD_TYPE) \
	ro.s3updater.updater.rom_name="PEPlus+NIS+Edition" \
    ro.s3updater.s3.endpoint="https://s3.octonezd.me" \
    ro.s3updater.s3.bucket="pe-nis"
endif