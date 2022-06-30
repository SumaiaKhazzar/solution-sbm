import logging
import datetime
from lime_application import LimeApplication
from lime_type import LimeObject
from lime_type.unit_of_work import UnitOfWork
from ..translations import get_translation
from limepkg_base_solution_helpers.limeobject_classes.general import (
    option_changed,
)
from limepkg_base_solution_helpers.common.common import (
    create_history
)
import limepkg_basic_deal.decorators as deal_decorators

logger = logging.getLogger(__name__)


@deal_decorators.deal()
class Deal(LimeObject):
    """Summarize the function of a Person object here"""

    def before_update(self, uow, **kwargs):
        """
        This is called on all new and updated objects. All changes
        made to the object here will be persisted.
        All other objects that are changed or created here must be
        added to the unit of work.
        """
        super().before_update(uow, **kwargs)

        if option_changed(self, "dealstatus", to_key=["agreement"]):
            self.properties.expecteddate.value = datetime.datetime.now()
        if option_changed(self, "dealstatus"):
            create_deal_history(self, uow)

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
    register_class("deal", Deal)


def create_deal_history(deal: LimeObject, uow: UnitOfWork):
    app: LimeApplication = deal.application
    coworker_name: str = ""
    coworker: LimeObject = app.coworker
    if coworker:
        coworker_name = coworker.properties.name.value
    note = get_translation(
        app,
        "dealstatus.autohistory.note",
        from_status=deal.properties.dealstatus.original_value.text,
        to_status=deal.properties.dealstatus.value.text,
        coworker_name=coworker_name,
    )
    history = create_history(deal, note=note, history_type="autolog")
    if coworker:
        history.properties.coworker.attach(coworker)
        uow.add(coworker)
    uow.add(history)
