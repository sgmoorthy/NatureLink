from typing import Dict, Any

class BhuvanConfig:
    # Citation and attribution information
    CITATION_INFO = {
        "source": "National Remote Sensing Centre, ISRO, Government of India, Hyderabad, India",
        "copyright": "© NRSC, ISRO",
        "license_type": "Limited, non-exclusive, non-transferable"
    }

    # Data usage restrictions
    DATA_RESTRICTIONS = {
        "max_image_size": (1000, 1000),  # 1K x 1K size limit for visualization
        "download_allowed": False,  # No downloading of original product
        "internal_use_only": True  # For internal needs and applications
    }

    # Disclaimer text
    DISCLAIMER = (
        "Users are solely responsible for interpretations made from these products. "
        "NRSC/ISRO/DOS does not warrant results obtained by using this data. "
        "While sufficient care was taken to provide reliable information, "
        "NRSC/ISRO/DOS does not take responsibility for any errors."
    )

    @staticmethod
    def get_citation_header() -> Dict[str, str]:
        """Get HTTP headers for API requests with proper attribution."""
        return {
            "X-Data-Source": BhuvanConfig.CITATION_INFO["source"],
            "X-Copyright": BhuvanConfig.CITATION_INFO["copyright"],
            "X-License-Type": BhuvanConfig.CITATION_INFO["license_type"]
        }

    @staticmethod
    def validate_image_size(width: int, height: int) -> bool:
        """Validate if image dimensions comply with size restrictions."""
        max_width, max_height = BhuvanConfig.DATA_RESTRICTIONS["max_image_size"]
        return width <= max_width and height <= max_height

    @staticmethod
    def get_usage_terms() -> str:
        """Get formatted usage terms for display."""
        return (
            "This data is provided under a limited, non-exclusive, non-transferable license. "
            "Users may use the data for internal needs and create value-added products. "
            "Any visualization must be limited to 1K x 1K size and include appropriate attribution."
        )