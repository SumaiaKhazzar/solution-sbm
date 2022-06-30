import logging
from ..translations import get_translation
from lime_application import LimeApplication
from lime_type import LimeObject
from lime_type.unit_of_work import UnitOfWork
from limepkg_base_solution_helpers.common.common import (
    create_history
)

from lime_file import File

logger = logging.getLogger(__name__)


class Document(LimeObject):
    """Summarize the function of a Person object here"""

    def before_update(self, uow, **kwargs):
        """
        This is called on all new and updated objects. All changes
        made to the object here will be persisted.
        All other objects that are changed or created here must be
        added to the unit of work.
        """
        super().before_update(uow, **kwargs)

        if self.is_new:
            create_document_history(self, uow)

    def before_delete(self, uow, **kwargs):
        """
        This is called on objects that are about to be deleted,
        before relations are detached. All changes made to
        the object here will be persisted.
        All other objects that are changed or created here must be
        added to the unit of work.

        """
        super().before_delete(uow, **kwargs)

    def after_update(self, unsaved_self, **kwargs):
        """
        This is called after the object has been saved, but before the
        transaction has been committed. IDs on new records will be set,
        and values that has changed are available on the unsaved_self
        object.
        Changes made to the object here will NOT be persisted.
        This is the place to publish custom events.
        """
        super().after_update(unsaved_self, **kwargs)


def register_limeobject_classes(register_class):
    register_class("document", Document)


def create_document_history(document: LimeObject, uow: UnitOfWork):
    app: LimeApplication = document.application
    document_name: str = ""
    coworker_name: str = ""
    document_file: File = document.properties.document.fetch()
    if document_file:
        document_name = document_file.filename
    coworker: LimeObject = app.coworker
    if coworker:
        coworker_name = coworker.properties.name.value
    note = get_translation(
        app,
        "document.autohistory.note",
        document_name=document_name,
        coworker_name=coworker_name,
    )
    history = create_history(document, uow, note=note, history_type="autolog")
    if coworker:
        history.properties.coworker.attach(coworker)
        uow.add(coworker)
    uow.add(history)
