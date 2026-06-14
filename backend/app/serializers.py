from datetime import date, time
from decimal import Decimal

from app import models


def date_to_api(value: date) -> str:
    return value.isoformat()


def time_to_api(value: time) -> str:
    return value.strftime("%H:%M")


def money_to_api(value: Decimal) -> float:
    return float(value)


def user_to_api(user: models.User) -> dict:
    return {
        "id": user.id,
        "fullName": user.full_name,
        "phone": user.phone,
        "email": user.email,
        "role": user.role.value,
        "createdAt": user.created_at,
    }


def appointment_status_history_to_api(item: models.AppointmentStatusHistory) -> dict:
    return {
        "id": item.id,
        "adminId": item.admin_id,
        "adminName": item.admin.full_name if item.admin else None,
        "previousStatus": item.previous_status.value,
        "newStatus": item.new_status.value,
        "createdAt": item.created_at,
    }


def clinic_info_to_api(info: models.ClinicInfo) -> dict:
    return {
        "id": info.id,
        "name": info.name,
        "description": info.description,
        "address": info.address,
        "phone": info.phone,
        "whatsapp": info.whatsapp,
        "instagram": info.instagram,
        "workingHours": info.working_hours,
        "mapUrl": info.map_url,
    }


def service_category_to_api(category: models.ServiceCategory) -> dict:
    return {
        "id": category.id,
        "title": category.title,
        "slug": category.slug,
        "description": category.description,
        "imageUrl": category.image_url,
        "sortOrder": category.sort_order,
    }


def service_to_api(service: models.Service) -> dict:
    return {
        "id": service.id,
        "title": service.title,
        "slug": service.slug,
        "description": service.description,
        "price": money_to_api(service.price),
        "durationMinutes": service.duration_minutes,
        "category": service_category_to_api(service.category),
        "imageUrl": service.image_url,
        "contraindications": service.contraindications,
    }


def admin_service_to_api(service: models.Service) -> dict:
    data = service_to_api(service)
    data["isActive"] = service.is_active
    return data


def product_category_to_api(category: models.ProductCategory) -> dict:
    return {
        "id": category.id,
        "title": category.title,
        "slug": category.slug,
    }


def product_to_api(product: models.Product) -> dict:
    return {
        "id": product.id,
        "title": product.title,
        "slug": product.slug,
        "description": product.description,
        "price": money_to_api(product.price),
        "imageUrl": product.image_url,
        "stock": product.stock,
        "category": product_category_to_api(product.category),
    }


def admin_product_to_api(product: models.Product) -> dict:
    data = product_to_api(product)
    data["isActive"] = product.is_active
    data["createdAt"] = product.created_at
    return data


def specialist_to_api(specialist: models.Specialist) -> dict:
    return {
        "id": specialist.id,
        "fullName": specialist.full_name,
        "position": specialist.position,
        "specialization": specialist.specialization,
        "experienceYears": specialist.experience_years,
        "photoUrl": specialist.photo_url,
        "serviceIds": [service.id for service in specialist.services],
    }


def admin_specialist_to_api(specialist: models.Specialist) -> dict:
    data = specialist_to_api(specialist)
    data["userId"] = specialist.user_id
    data["isActive"] = specialist.is_active
    return data


def doctor_schedule_to_api(schedule_item: models.DoctorSchedule) -> dict:
    return {
        "id": schedule_item.id,
        "specialist": specialist_to_api(schedule_item.specialist),
        "date": date_to_api(schedule_item.schedule_date),
        "startTime": time_to_api(schedule_item.start_time),
        "endTime": time_to_api(schedule_item.end_time),
        "isAvailable": schedule_item.is_available,
        "createdAt": schedule_item.created_at,
        "updatedAt": schedule_item.updated_at,
    }


def doctor_schedule_item_to_api(schedule_item: models.DoctorSchedule) -> dict:
    return {
        "date": date_to_api(schedule_item.schedule_date),
        "startTime": time_to_api(schedule_item.start_time),
        "endTime": time_to_api(schedule_item.end_time),
        "isAvailable": schedule_item.is_available,
    }


def appointment_to_api(appointment: models.Appointment) -> dict:
    return {
        "id": appointment.id,
        "appointmentNumber": appointment.appointment_number,
        "patientId": appointment.patient_id,
        "patientName": appointment.patient_name,
        "patientPhone": appointment.patient_phone,
        "service": service_to_api(appointment.service),
        "specialist": specialist_to_api(appointment.specialist),
        "date": date_to_api(appointment.appointment_date),
        "time": time_to_api(appointment.appointment_time),
        "requestedDate": date_to_api(appointment.requested_date) if appointment.requested_date else None,
        "requestedTime": time_to_api(appointment.requested_time) if appointment.requested_time else None,
        "status": appointment.status.value,
        "comment": appointment.comment,
        "patientContactStatus": appointment.patient_contact_status,
        "patientContactedAt": appointment.patient_contacted_at,
        "patientContactComment": appointment.patient_contact_comment,
        "statusHistory": [appointment_status_history_to_api(item) for item in appointment.status_history],
        "createdAt": appointment.created_at,
    }


def wishlist_item_to_api(item: models.WishlistItem) -> dict:
    return {
        "id": item.id,
        "product": product_to_api(item.product),
        "createdAt": item.created_at,
    }


def cart_item_to_api(item: models.CartItem) -> dict:
    return {
        "id": item.id,
        "product": product_to_api(item.product),
        "quantity": item.quantity,
        "price": money_to_api(item.price),
        "subtotal": money_to_api(item.subtotal),
    }


def cart_to_api(items: list[models.CartItem]) -> dict:
    return {
        "items": [cart_item_to_api(item) for item in items],
        "totalPrice": sum(money_to_api(item.subtotal) for item in items),
    }

def order_item_product_to_api(item: models.OrderItem) -> dict:
    if item.product is not None:
        return product_to_api(item.product)

    # Product was hard-deleted (order_items.product_id -> NULL via ON DELETE
    # SET NULL). Fall back to the title/slug/price snapshot stored on the order
    # item so historical orders still serialize instead of crashing.
    return {
        "id": item.product_id or "",
        "title": item.product_title,
        "slug": item.product_slug,
        "description": "",
        "price": money_to_api(item.price),
        "imageUrl": None,
        "stock": 0,
        "category": {"id": "", "title": "", "slug": ""},
    }

def order_item_to_api(item: models.OrderItem) -> dict:
    return {
        "product": order_item_product_to_api(item),
        "quantity": item.quantity,
        "price": money_to_api(item.price),
        "subtotal": money_to_api(item.subtotal),
    }


def payment_to_api(payment: models.Payment) -> dict:
    return {
        "id": payment.id,
        "paymentUrl": payment.payment_url,
        "providerPaymentId": payment.provider_payment_id,
        "status": payment.status.value,
        "expiresAt": payment.expires_at,
        "createdAt": payment.created_at,
    }


def order_to_api(order: models.Order) -> dict:
    return {
        "id": order.id,
        "orderNumber": order.order_number,
        "userId": order.user_id,
        "items": [order_item_to_api(item) for item in order.items],
        "totalPrice": money_to_api(order.total_price),
        "paymentStatus": order.payment_status.value,
        "orderStatus": order.order_status.value,
        "paymentMethod": order.payment_method.value,
        "deliveryMethod": order.delivery_method.value,
        "deliveryAddress": order.delivery_address,
        "recipientName": order.recipient_name,
        "recipientPhone": order.recipient_phone,
        "createdAt": order.created_at,
    }


def payment_create_to_api(payment: models.Payment) -> dict:
    return {
        "paymentId": payment.id,
        "paymentUrl": payment.payment_url,
        "expiresAt": payment.expires_at,
    }


def review_to_api(review: models.Review) -> dict:
    return {
        "id": review.id,
        "authorName": review.author_name,
        "rating": review.rating,
        "text": review.text,
        "source": review.source,
        "sourceUrl": review.source_url,
        "isPublished": review.is_published,
        "sortOrder": review.sort_order,
        "publishedAt": review.published_at,
        "createdAt": review.created_at,
        "updatedAt": review.updated_at,
    }


def recommendation_to_api(recommendation: models.Recommendation) -> dict:
    if recommendation.patient is not None:
        patient_name = recommendation.patient.full_name
        patient_phone = recommendation.patient.phone
    elif recommendation.appointment is not None:
        patient_name = recommendation.appointment.patient_name
        patient_phone = recommendation.appointment.patient_phone
    else:
        patient_name = None
        patient_phone = None

    return {
        "id": recommendation.id,
        "patientId": recommendation.patient_id,
        "patientName": patient_name,
        "patientPhone": patient_phone,
        "doctorId": recommendation.doctor_id,
        "appointmentId": recommendation.appointment_id,
        "text": recommendation.text,
        "productIds": [product.id for product in recommendation.products],
        "createdAt": recommendation.created_at,
    }
