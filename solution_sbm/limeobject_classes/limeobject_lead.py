import logging
from lime_application import LimeApplication
from lime_type import LimeObject
from lime_type.unit_of_work import UnitOfWork
from ..translations import get_translation
from limepkg_base_solution_helpers.common.common import (
    format_phone,
    create_history
)
from limepkg_base_solution_helpers.limeobject_classes.general import (
    option_changed,
    set_name_from_firstname_lastname,
)
import limepkg_basic_lead.decorators as lead_decorators

logger = logging.getLogger(__name__)


@lead_decorators.lead()
class Lead(LimeObject):
    """Summarize the function of a Person object here"""

    def before_update(self, uow, **kwargs):
        """
        This is called on all new and updated objects. All changes
        made to the object here will be persisted.
        All other objects that are changed or created here must be
        added to the unit of work.
        """
        super().before_update(uow, **kwargs)

        if self.properties.phone.is_dirty():
            self.properties.phone.value = format_phone(
                self.properties.phone.value)

        set_name_from_firstname_lastname(self)

        if option_changed(self, "leadstatus"):
            create_lead_history(self, uow)

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
    register_class("lead", Lead)


def create_lead_history(lead: LimeObject, uow: UnitOfWork):
    app: LimeApplication = lead.application
    coworker_name: str = ""
    coworker: LimeObject = app.coworker
    if coworker:
        coworker_name = coworker.properties.name.value
    note = get_translation(
        app,
        "leadstatus.autohistory.note",
        from_status=lead.properties.leadstatus.original_value.text,
        to_status=lead.properties.leadstatus.value.text,
        coworker_name=coworker_name,
    )
    history = create_history(lead, note=note, history_type="autolog")
    if coworker:
        history.properties.coworker.attach(coworker)
        uow.add(coworker)
    uow.add(history)
