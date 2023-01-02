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
$(call inherit-product, packages/overlays/ThemeIcons/config.mk)