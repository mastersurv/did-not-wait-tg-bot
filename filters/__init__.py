from loader import dp
from .user_status import AdminFilter


if __name__ == "filters":
    dp.filters_factory.bind(AdminFilter)
