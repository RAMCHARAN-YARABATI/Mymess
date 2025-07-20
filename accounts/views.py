
import random,io, uuid, qrcode
from django.shortcuts import render, redirect,get_object_or_404
from .models import  StudentUser, BookingRecord, MealSlot
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import FileResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta, datetime
from django.views.decorators.http import require_POST
from .utils  import is_window_open, is_qr_visible_for_meal



def signup_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        rollnumber = request.POST['rollnumber']
        department = request.POST['department']
        gender = request.POST['gender']
        email = request.POST['email']
        password = request.POST['password']
        repeat_password = request.POST['repeat_password']

        '''

        if not email.endswith('@student.nitw.ac.in'):
            return render(request, 'accounts/signup.html', {'error_message': 'Only NITW student emails allowed.'})
        
        '''

        if password != repeat_password:
            return render(request, 'accounts/signup.html', {'error_message': 'Passwords do not match.'})

        if StudentUser.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {'error_message': 'Email already exists.'})

        # Save the user
        user = StudentUser(
            name=name,
            rollnumber=rollnumber,
            department=department,
            gender=gender,
            email=email,
            password=make_password(password)
        )                            
        user.save()

        return render(request, 'accounts/signup.html', {'success_message': 'Signup successful!'})

    return render(request, 'accounts/signup.html')



# Store OTPs temporarily
otp_storage = {}

def send_otp_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not StudentUser.objects.filter(email=email).exists():
            return render(request, 'accounts/login.html', {
                'error': ' This email is not registered. Please sign up first.',
                'email': email
            })
        ''' Also passes the email back so the user doesn't need to re-enter it.'''

        if 'otp1' in request.POST:
            otp_entered = ''.join([
                request.POST.get('otp1', ''),
                request.POST.get('otp2', ''),
                request.POST.get('otp3', ''),
                request.POST.get('otp4', ''),
            ])

            if otp_storage.get(email) == otp_entered:
                request.session['user_email'] = email
                return redirect('home')
            else:
                return render(request, 'accounts/login.html', {
                    'email': email,
                    'otp_sent': True,
                    'error': " Invalid OTP. Try again.",
                })

        # Generate and send OTP
        otp = str(random.randint(1000, 9999))
        otp_storage[email] = otp

        send_mail(
            subject = 'Your One-Time Password (OTP) for MyMess',
            message = f"""
Hello,
Your One-Time Password (OTP) to log in to your MyMess account is:OTP: {otp}
Please enter this code within 5 minutes to complete your login.
If you did not request this OTP, please ignore this message.
Regards,  
MyMess Team  
                    """,
            from_email='noreplymymessbooking@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )


        return render(request, 'accounts/login.html', {
            'email': email,
            'otp_sent': True,
            'message': 'OTP sent to your email!',
        })

    return render(request, 'accounts/login.html')


#  Session-based “login required” decorator
def session_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'user_email' not in request.session:
            return redirect('send_otp')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@session_login_required
def home_view(request):
    email = request.session.get('user_email')

    if not email:
        return redirect('send_otp')  # Not logged in

    try:
        user = StudentUser.objects.get(email=email)
    except StudentUser.DoesNotExist:
        return redirect('send_otp')

    return render(request, 'accounts/home.html', {
        'firstname': user.name,
        'email': user.email,
        'rollnumber': user.rollnumber,
        'department': user.department,
        'gender': user.gender,
    })


def logout_view(request):
    request.session.flush() # This clears all session data
    return redirect('send_otp')


def orders_view(request):
    user      = StudentUser.objects.get(email=request.session["user_email"])
    now = datetime.now()
    today     = now.date()
    tomorrow  = today + timedelta(days=1)

    slots = MealSlot.objects.all().order_by("id")

    today_orders    = {b.meal_type_id: b for b in BookingRecord.objects.filter(user=user, date=today)}
    tomorrow_orders = {b.meal_type_id: b for b in BookingRecord.objects.filter(user=user, date=tomorrow)}

    today_flags    = {s.id: is_window_open(s.name, "today")    for s in slots}  #True or False 
    tomorrow_flags = {s.id: is_window_open(s.name, "tomorrow") for s in slots} #True or False

    cut_off = {s.id:is_qr_visible_for_meal(s.name) for s in slots }

    combined_orders = ( BookingRecord.objects.filter(user=user, date__in=[today, tomorrow]).order_by("-date") )
    transactions = BookingRecord.objects.filter(user=user).order_by("-booked_at") 

    return render(
        request,
        "accounts/orders.html",
        {
            "wallet":            user.refund_wallet,
            "today":             today,
            "tomorrow":          tomorrow,
            "slots":             slots,
            "today_orders":      today_orders,
            "tomorrow_orders":   tomorrow_orders,
            "today_flags":       today_flags,
            "tomorrow_flags":    tomorrow_flags,
            "combined_orders":   combined_orders,
            "transactions":      transactions,
            "cut_off":           cut_off,
            "window_text": {
                "Breakfast": "2 p.m. – midnight",
                "Lunch":     "today 5 p.m. to tomorrow 9 a.m.",
                "Dinner":    "today 10 p.m. to tomorrow 4 p.m.",
            },
        },
    )



# Apply confirmation (GET)
def apply_confirm(request, slot_id, day):
    user        = StudentUser.objects.get(email=request.session["user_email"])
    slot        = get_object_or_404(MealSlot, id=slot_id)
    date_target = timezone.localdate() if day == "today" else timezone.localdate() + timedelta(days=1)

    already     = BookingRecord.objects.filter(user=user, meal_type=slot, date=date_target).exists()
    is_open     = is_window_open(slot.name, day)

    return render(
        request,
        "accounts/apply_confirm.html",
        {
            "slot": slot,
            "day": day,
            "date": date_target,
            "already_booked": already,
            "is_open": is_open,
        },
    )


# Apply meal (POST)
#@require_POST: Ensures this view only accepts POST requests (not GET). So, the user must have clicked a form “Apply” button.
@require_POST 
def apply_meal(request, slot_id, day):
    user        = StudentUser.objects.get(email=request.session["user_email"])
    slot        = get_object_or_404(MealSlot, id=slot_id)
    date_target = timezone.localdate() if day == "today" else timezone.localdate() + timedelta(days=1)

    if not is_window_open(slot.name, day):
        messages.error(request, "Booking window closed.")
        return redirect("orders")

    if BookingRecord.objects.filter(user=user, meal_type=slot, date=date_target).exists():
        messages.warning(request, "Already booked.")
        return redirect("orders")

    if user.refund_wallet < slot.price:
        messages.error(request, "Insufficient balance.")
        return redirect("orders")

    BookingRecord.objects.create(user=user, meal_type=slot, date=date_target)
    user.refund_wallet -= slot.price
    user.save(update_fields=["refund_wallet"])

    messages.success(request, f"{slot.name} booked for {date_target}.")
    return redirect("orders")


# Cancel booking (POST)
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        BookingRecord, id=booking_id, user__email=request.session["user_email"]
    )
  
    day_flag = "today" if booking.date == timezone.localdate() else "tomorrow"
    '''
    if not is_window_open(booking.meal_type.name, day_flag):
        messages.error(request, "Cut‑off passed – cannot cancel.")
        return redirect("orders") '''

    booking.status   = "Canceled"
    booking.qr_token = None
    if booking.qr_image:
        booking.qr_image.delete(save=False)
    booking.qr_image = None
    booking.save(update_fields=["status", "qr_token", "qr_image"])
    booking.user.refund_wallet += booking.meal_type.price
    booking.user.save(update_fields=["refund_wallet"])

    messages.success(request, f"Canceled and refunded ₹{booking.meal_type.price}.")
    return redirect("orders")



def get_qr(request, booking_id):
    booking = get_object_or_404(
        BookingRecord, id=booking_id, user__email=request.session["user_email"]
    )

    # ✅ Generate QR only once
    if not booking.qr_token or not booking.qr_image:
        qr_text = (
            f"Meal:{booking.meal_type.name}|"
            f"Name:{booking.user.name}|"
            f"Roll:{booking.user.rollnumber}|"
            f"Date:{booking.date}|"
            f"Status:{booking.status}"
        )
        img = qrcode.make(qr_text)

        # Save QR image to memory buffer
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        # Save it to qr_codes/ inside media folder
        booking.qr_token = str(uuid.uuid4())
        booking.qr_image.save(
            f"qr_codes/qr_{booking.qr_token}.png",
            ContentFile(buf.getvalue()),
            save=True
        )

    return FileResponse(booking.qr_image.open("rb"), content_type="image/png")
