from app.finances.models import Expense
from app.finances.schemas import ResponseExpense, FilterExpense
from app.finances.dao import ExpenseDAO
from app.finances.caching import CacheClient
from sqlalchemy.ext.asyncio import AsyncSession


async def find_expenses_by_filter_with_cache(
        db_session: AsyncSession,
        filters: FilterExpense,
        cache: CacheClient
) -> list[ResponseExpense]:
    ids = await ExpenseDAO.find_id_by_filter(
        db_session=db_session, filters=filters)
    if not ids:
        return []

    cached_exp = await cache.get_many_exp(ids)
    cached_ids = {exp.id for exp in cached_exp}
    missing_ids = list(set(ids) - cached_ids)

    db_expenses = []
    if missing_ids:
        db_models = await ExpenseDAO.find_by_id(db_session,
                                                missing_ids)
        db_expenses = [ResponseExpense.model_validate(model)
                       for model in db_models]

        await cache.set_many(db_expenses)

    all_expenses = db_expenses + cached_exp
    ordered_exp = sorted(all_expenses,
                         key=lambda x: ids.index(x.id))
    return ordered_exp
