from __future__ import annotations

from app.repositories.base import pagination_meta, paginated
from app.repositories.users import (
    create_refresh_token,
    create_user,
    create_admin_user,
    delete_admin_user,
    get_active_refresh_token,
    get_user,
    get_user_by_email,
    get_user_by_phone,
    get_user_by_phone_or_email,
    list_admin_users,
    revoke_refresh_token,
    revoke_user_refresh_tokens,
    update_admin_user,
    update_user_profile,
)
from app.repositories.clinic import get_clinic_info, update_clinic_info
from app.repositories.services import (
    create_admin_service,
    create_service_category,
    delete_admin_service,
    delete_service_category,
    deactivate_admin_service,
    get_admin_service,
    get_service,
    get_service_by_slug,
    get_service_category,
    list_admin_services,
    list_service_categories,
    list_services,
    list_services_by_ids,
    update_admin_service,
    update_service_category,
)
from app.repositories.specialists import (
    create_admin_specialist,
    deactivate_admin_specialist,
    delete_admin_specialist,
    get_admin_specialist,
    get_specialist,
    get_specialist_by_user_id,
    list_admin_specialists,
    list_specialists,
    replace_specialist_services,
    update_admin_specialist,
)
from app.repositories.products import (
    create_admin_product,
    create_product_category,
    deactivate_admin_product,
    delete_admin_product,
    get_admin_product,
    get_product,
    get_product_by_slug,
    get_product_category,
    list_admin_products,
    list_admin_products_all,
    list_product_categories,
    list_products,
    list_products_by_ids,
    update_admin_product,
)
from app.repositories.orders import (
    create_admin_order,
    create_order_from_cart,
    create_order_payment,
    get_admin_order,
    get_user_order,
    list_admin_orders,
    list_admin_orders_all,
    list_user_orders,
    update_admin_order_status,
)
from app.repositories.appointments import (
    cancel_user_appointment,
    count_pending_appointments,
    create_appointment,
    get_appointment,
    is_appointment_slot_available,
    is_appointment_status_transition_allowed,
    list_admin_appointments,
    list_busy_appointments,
    reschedule_appointment,
    update_appointment_contact,
    update_appointment_status,
)
from app.repositories.schedule import (
    create_admin_doctor_schedule_item,
    deactivate_admin_doctor_schedule_item,
    delete_admin_doctor_schedule_item,
    get_admin_doctor_schedule_item,
    list_admin_doctor_schedule,
    list_doctor_schedule,
    list_schedule_items,
    update_admin_doctor_schedule_item,
)
from app.repositories.wishlist import (
    add_wishlist_item,
    delete_wishlist_item,
    list_wishlist_items,
)
from app.repositories.cart import (
    add_cart_item,
    delete_cart_item,
    list_cart_items,
    update_cart_item,
)
from app.repositories.reviews import (
    create_admin_review,
    delete_admin_review,
    get_admin_review,
    list_admin_reviews,
    list_reviews,
    update_admin_review,
)
from app.repositories.recommendations import (
    create_admin_recommendation,
    delete_admin_recommendation,
    get_admin_recommendation,
    list_admin_recommendations,
    list_patient_recommendations,
    replace_recommendation_products,
    update_admin_recommendation,
)
from app.repositories.analytics import (
    admin_analytics,
    get_sales_analytics,
    get_services_analytics,
)
from app.repositories.settings import (
    get_settings_map,
    replace_settings,
    upsert_setting,
)
