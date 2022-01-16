# Enable overlays for:
# - Headphones icon in statusbar by default
DEVICE_PACKAGE_OVERLAYS += \
	vendor/octo/overlays
# Load extendrom
$(call inherit-product-if-exists, vendor/extendrom/config/common.mk)
# Load prebuilts
ifdef OCTO_PACKAGES
PRODUCT_PACKAGES += $(OCTO_PACKAGES)
endif
