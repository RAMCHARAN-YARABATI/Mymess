
from django.db import models

class StudentUser(models.Model):
    '''
       In Python, inheritance means your class (child) gets all the properties and methods from another class (parent).
       Here: StudentUser → your class (child)
       models.Model → Django’s built-in class (parent)
    '''
    name        = models.CharField(max_length=100)
    rollnumber  = models.CharField(max_length=20)
    department  = models.CharField(max_length=50)
    gender      = models.CharField(max_length=10)
    email       = models.EmailField(unique=True)
    password    = models.CharField(max_length=200)

    # 💰 wallet – starts at ₹15 000
    refund_wallet = models.DecimalField(default=15000.00,
                                        max_digits=10, decimal_places=2)

    def __str__(self):
        return self.email
    

class MealSlot(models.Model):
    BREAKFAST = "Breakfast"
    LUNCH     = "Lunch"
    DINNER    = "Dinner"
    ''' ✅ These are constants used for meal types. Defining them helps avoid typing mistakes and keeps the code readable. '''
    MEALS = [(BREAKFAST, BREAKFAST), (LUNCH, LUNCH), (DINNER, DINNER)]

    name  = models.CharField(max_length=15, choices=MEALS, unique=True)
    price = models.PositiveIntegerField()   
    ''' problem '''               

    def __str__(self):
        return self.name



class BookingRecord(models.Model):
    '''This model represents one meal booking by one student for a particular date.'''
    user = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    '''on_delete=models.CASCADE = if a student is deleted, all their bookings will be deleted automatically.'''
    meal_type = models.ForeignKey(MealSlot, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, default="Booked")
    booked_at = models.DateTimeField(auto_now_add=True)
    qr_token = models.CharField(max_length=100, blank=True, null=True)

    # ✅ Add this line below:
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.name} - {self.meal_type.name} - {self.date}"