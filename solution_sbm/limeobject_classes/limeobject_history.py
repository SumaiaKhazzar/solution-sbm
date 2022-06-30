import logging
from lime_type.limeobjects import LimeObject
from limepkg_base_solution_helpers.limeobject_classes.general import (
    option_changed,
)

logger = logging.getLogger(__name__)


class History(LimeObject):
    """Summarize the function of a Person object here"""

    def before_update(self, uow, **kwargs):
        """
        This is called on all new and updated objects. All changes
        made to the object here will be persisted.
        All other objects that are changed or created here must be
        added to the unit of work.
        """
        super().before_update(uow, **kwargs)

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

        salescontact_types = ["salescall", "customervisit"]

        is_date_changed_on_salescontact = (
            unsaved_self.properties.date.is_dirty()
            and unsaved_self.properties.type.value.key in salescontact_types
        )

        if is_date_changed_on_salescontact or option_changed(
            unsaved_self, "type", to_key=salescontact_types
        ):
            set_latestsalescontact(self)


def register_limeobject_classes(register_class):
    register_class("history", History)


def set_latestsalescontact(history: LimeObject):
    uow = history.application.unit_of_work()
    history_date = history.properties.date.value
    if history.properties.deal.value:
        deal: LimeObject = history.properties.deal.fetch()
        deal.properties.latestsalescontact.value = history_date
        uow.add(deal)
    if history.properties.company.value:
        company: LimeObject = history.properties.company.fetch()
        company.properties.latestsalescontact.value = history_date
        uow.add(company)
    uow.commit()
