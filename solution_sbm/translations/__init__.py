import os.path
import lime_translation as translate
from lime_application import LimeApplication


def register_translations():
    """
    Returns the path to the directory containing po-files.
    """
    return os.path.abspath(os.path.dirname(__file__))


def get_translation(app: LimeApplication, key: str, **kwargs):
    return translate.get_text(
        app.language, f"solution_smh_package.{key}", **kwargs
    )
