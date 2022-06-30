import logging
from lime_application import LimeApplication
from lime_type import LimeObject
from lime_type.unit_of_work import UnitOfWork
from ..translations import get_translation
from limepkg_base_solution_helpers.limeobject_classes.general import (
    option_changed,
)
from limepkg_base_solution_helpers.limeobject_classes.company import (
    set_full_invoice_address,
    set_full_postal_address,
    set_full_visiting_address,
)
from limepkg_base_solution_helpers.common.common import (
    format_phone,
    create_history
)

logger = logging.getLogger(__name__)


class Company(LimeObject):
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

        if option_changed(self, "buyingstatus"):
            create_company_history(self, uow)
        set_full_visiting_address(self)
        set_full_invoice_address(self)
        set_full_postal_address(self)

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
    register_class("company", Company)


def create_company_history(company: LimeObject, uow: UnitOfWork):
    app: LimeApplication = company.application
    coworker_name: str = ""
    coworker: LimeObject = app.coworker
    if coworker:
        coworker_name = coworker.properties.name.value
    note = get_translation(
        app,
        "buyingstatus.autohistory.note",
        from_status=company.properties.buyingstatus.original_value.text,
        to_status=company.properties.buyingstatus.value.text,
        coworker_name=coworker_name,
    )
    history = create_history(company, note=note, history_type="autolog")
    if coworker:
        history.properties.coworker.attach(coworker)
        uow.add(coworker)
    uow.add(history)
