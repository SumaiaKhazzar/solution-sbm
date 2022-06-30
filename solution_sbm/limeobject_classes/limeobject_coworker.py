import logging
from lime_type import LimeObject
from limepkg_base_solution_helpers.common.common import format_phone
from limepkg_base_solution_helpers.limeobject_classes.general import (
    set_name_from_firstname_lastname
)

logger = logging.getLogger(__name__)


class Coworker(LimeObject):
    """Summarize the function of a Person object here"""

    def before_update(self, uow, **kwargs):
        """
        This is called on all new and updated objects. All changes
        made to the object here will be persisted.
        All other objects that are changed or created here must be
        added to the unit of work.
        """
        super().before_update(uow, **kwargs)

        set_name_from_firstname_lastname(self)

        if self.properties.phone.is_dirty():
            self.properties.phone.value = format_phone(
                self.properties.phone.value)
        if self.properties.mobilephone.is_dirty():
            self.properties.mobilephone.value = format_phone(
                self.properties.mobilephone.value)

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
    register_class("coworker", Coworker)
