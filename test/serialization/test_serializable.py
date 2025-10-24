from uuid import UUID

from <%my_service%>.domain.models.user_role import UserRole
from <%my_service%>.util import time


async def test_serializable_datetimes():
    user_role = _sample_user_role()
    record = user_role.to_dict()
    assert UserRole.from_dict(record) == user_role


async def test_serializable_datetimes_from_sql_record():
    user_role = _sample_user_role()
    record = user_role.to_native_dict()
    assert UserRole.from_native_dict(record) == user_role


def _sample_user_role():
    return UserRole(
        user_id=UUID('00000000000000000000000000000001', version=4),
        role_id=UUID('00000000000000000000000000000002', version=4),
        granted_on=time.current_datetime(),
        granted_by=UUID('00000000000000000000000000000003', version=4)
    )
