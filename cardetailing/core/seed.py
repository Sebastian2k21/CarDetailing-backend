from datetime import datetime, timedelta
from bson import ObjectId
from .models import CarService, CarServiceSchedule, CarServiceScheduleSubmit, Car, SubmitStatus


def create_test_data(detailer_id, user_ids):
    service = CarService.objects.create(
        _id=ObjectId(),
        name="Testowy Serwis Mycia",
        price=199.99,
        description="Profesjonalne mycie samochodu",
        image=None,
        detailer_id=detailer_id,
        duration=60,
        label_color="#ff5722"
    )
    print(f"Utworzono CarService: {service}")

    schedule_days = [0, 2, 4]
    schedules = []
    for day in schedule_days:
        schedule = CarServiceSchedule.objects.create(
            _id=ObjectId(),
            service_id=str(service._id),
            day_of_week=day,
            time=datetime.now().time()
        )
        schedules.append(schedule)
        print(f"Utworzono CarServiceSchedule: {schedule}")

    # 3. Pobieranie lub tworzenie statusu
    status, created = SubmitStatus.objects.get_or_create(
        name="pending",
        defaults={"_id": ObjectId()}
    )
    if created:
        print(f"Utworzono nowy status: {status}")
    else:
        print(f"Używany istniejący status: {status}")

    submits = []
    for user_id in user_ids:
        car = Car.objects.filter(user_id=user_id, is_removed=0).first()
        if not car:
            print(f"Użytkownik {user_id} nie ma przypisanego samochodu. Pomijam.")
            continue

        for schedule in schedules:
            submit = CarServiceScheduleSubmit.objects.create(
                _id=ObjectId(),
                date=datetime.now() + timedelta(days=schedule.day_of_week),
                schedule_id=str(schedule._id),
                user_id=user_id,
                service_id=str(service._id),
                car_id=str(car._id),
                status_id=str(status._id),
                employee_id=None
            )
            submits.append(submit)
            print(f"Utworzono CarServiceScheduleSubmit: {submit}")

    print("Testowe dane zostały pomyślnie utworzone.")
    return {
        "service": service,
        "schedules": schedules,
        "submits": submits
    }
