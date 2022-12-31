# Enable overlays
DEVICE_PACKAGE_OVERLAYS += \
	vendor/octo/overlays
# Load prebuilts
ifdef OCTO_PACKAGES
PRODUCT_PACKAGES += $(OCTO_PACKAGES)
endif
# Add F-DroidPrivilegedExtension
PRODUCT_PACKAGES += F-DroidPrivilegedExtension 
# Load TeamFiles PixelLauncherExtended 
$(call inherit-product, vendor/PixelLauncherExtended/PixelLauncher.mk)
ICONS_VARIANT := teamfilesicons
PIXEL_LAUNCHER_VARIANT := nomod
# Enable extendrom
$(call inherit-product-if-exists, vendor/extendrom/config/common.mk)