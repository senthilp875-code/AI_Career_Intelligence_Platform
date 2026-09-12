from .section_builder import build_resume_sections
from .themes import THEMES


def generate_resume_data(analysis, theme="modern_blue"):
    """
    Creates the complete resume data object.
    """

    resume = {

        "theme": THEMES.get(theme),

        "sections": build_resume_sections(analysis)

    }

    return resume