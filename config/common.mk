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