import re
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

GMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'

class asha_worker(models.Model):
    LOGIN=models.ForeignKey(User, on_delete=models.CASCADE)
    Full_name=models.TextField()
    Age=models.IntegerField()
    dob=models.DateField(null=True, blank=True)
    Qualification=models.TextField()
    Email=models.TextField()
    Address = models.TextField()
    image = models.FileField()
    Area_assigned = models.TextField()
    Phone=models.BigIntegerField()
    Joining_date=models.DateField()
    Current_status = models.TextField(default='Active')

    def clean(self):
        super().clean()
        if self.Email and not re.match(GMAIL_REGEX, str(self.Email).strip(), re.IGNORECASE):
            raise ValidationError({'Email': 'Email must be in valid @gmail.com format (e.g., example@gmail.com).'})

class anganwadi_teacher(models.Model):
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    Name=models.TextField()
    Age=models.IntegerField()
    dob=models.DateField(null=True, blank=True)
    Gender=models.TextField()
    Phone=models.BigIntegerField()
    Email=models.TextField()
    Address=models.TextField()
    image = models.FileField(null=True, blank=True)
    Qualification=models.TextField()
    center_name = models.TextField()
    joining_date = models.DateField()
    Current_status = models.TextField(default='Active')

    def clean(self):
        super().clean()
        if self.Email and not re.match(GMAIL_REGEX, str(self.Email).strip(), re.IGNORECASE):
            raise ValidationError({'Email': 'Email must be in valid @gmail.com format (e.g., example@gmail.com).'})

class user_table(models.Model):
    LOGIN=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ASHA=models.ForeignKey(asha_worker, on_delete=models.CASCADE, null=True, blank=True)
    name=models.TextField()
    husband_name=models.TextField()
    age=models.IntegerField()
    dob=models.DateField()
    blood_group=models.TextField()
    phone=models.BigIntegerField()
    Email = models.TextField()
    Address = models.TextField()
    panchayath = models.TextField()
    area = models.TextField(null=True, blank=True)
    district = models.TextField()
    state = models.TextField()
    pincode = models.TextField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True, null=True, blank=True)

    def clean(self):
        super().clean()
        if self.Email and not re.match(GMAIL_REGEX, str(self.Email).strip(), re.IGNORECASE):
            raise ValidationError({'Email': 'Email must be in valid @gmail.com format (e.g., example@gmail.com).'})

    @property
    def latest_child(self):
        if not self.pk:
            return None
        from myapp.models import child
        return child.objects.filter(USER=self).order_by('-date_of_birth', '-id').first()

    @property
    def delivered_children_count(self):
        if not self.pk:
            return 0
        from myapp.models import child
        return child.objects.filter(USER=self).count()

    @property
    def has_delivered_child(self):
        if not self.pk:
            return False
        from myapp.models import child
        return child.objects.filter(USER=self).exists()

    @property
    def current_pregnancy_number(self):
        return self.delivered_children_count + 1

    @property
    def is_currently_pregnant(self):
        from datetime import date, timedelta
        today = date.today()
        if not self.pk:
            return bool(self.expected_delivery_date and self.expected_delivery_date >= (today - timedelta(days=28)))
        from myapp.models import child, pregnancy_record
        latest_c = child.objects.filter(USER=self).order_by('-date_of_birth', '-id').first()
        latest_preg = pregnancy_record.objects.filter(USER=self).order_by('-checkup_date', '-id').first()

        # If mother has delivered a child in the past:
        if latest_c:
            # Check 1: If there is an antenatal checkup recorded AFTER the latest child's birth date:
            if latest_preg and latest_preg.checkup_date > latest_c.date_of_birth:
                rec_edd = latest_preg.expected_delivery_date or self.expected_delivery_date
                if rec_edd and rec_edd >= (today - timedelta(days=28)):
                    return True
                if (today - latest_preg.checkup_date).days <= 280:
                    return True

            # Check 2: If mother has a new expected delivery date set on profile that represents a subsequent pregnancy
            # (EDD must be at least ~150 days after previous child's DOB, and active/future)
            if self.expected_delivery_date:
                min_subsequent_edd = latest_c.date_of_birth + timedelta(days=150)
                if self.expected_delivery_date >= min_subsequent_edd:
                    if self.expected_delivery_date >= (today - timedelta(days=28)):
                        return True

            # Otherwise, the woman has delivered and is in the postpartum/delivered state
            return False

        # If mother has NOT delivered a child yet (first pregnancy):
        if self.expected_delivery_date:
            if self.expected_delivery_date >= (today - timedelta(days=28)):
                return True
            if latest_preg and (today - latest_preg.checkup_date).days <= 280:
                return True
            return True

        # Check latest pregnancy record if profile EDD is missing
        if latest_preg and latest_preg.expected_delivery_date:
            if latest_preg.expected_delivery_date >= (today - timedelta(days=28)):
                return True

        return False

    @property
    def has_delivered(self):
        if self.is_currently_pregnant:
            return False
        if not self.pk:
            return False
        from myapp.models import child
        return child.objects.filter(USER=self).exists()

    @property
    def maternal_status(self):
        if self.is_currently_pregnant:
            return "Pregnant"
        elif self.has_delivered:
            return "Delivered"
        return "Registered"

    @property
    def active_edd(self):
        if not self.is_currently_pregnant:
            return None
        from datetime import timedelta
        latest_c = self.latest_child
        edd = self.expected_delivery_date
        if latest_c and edd and edd < (latest_c.date_of_birth + timedelta(days=150)):
            edd = None
        if not edd:
            from myapp.models import pregnancy_record
            if latest_c:
                latest_p = pregnancy_record.objects.filter(USER=self, checkup_date__gt=latest_c.date_of_birth).order_by('-checkup_date', '-id').first()
            else:
                latest_p = pregnancy_record.objects.filter(USER=self).order_by('-checkup_date', '-id').first()
            if latest_p:
                edd = latest_p.expected_delivery_date
        return edd

    @property
    def gestation_weeks(self):
        if not self.is_currently_pregnant:
            return None
        edd = self.active_edd
        if not edd:
            return None
        from datetime import date
        today = date.today()
        days_left = (edd - today).days
        gest_days = 280 - days_left
        if gest_days < 0:
            return 0
        return gest_days // 7

    @property
    def gestation_month(self):
        if not self.is_currently_pregnant:
            return None
        edd = self.active_edd
        if not edd:
            return None
        from datetime import date
        today = date.today()
        days_left = (edd - today).days
        gest_days = 280 - days_left
        if gest_days <= 0:
            return 1
        month = (gest_days // 30) + 1
        if month > 9:
            return 9
        return month

    @property
    def gestation_week_display(self):
        if not self.is_currently_pregnant:
            if self.has_delivered:
                return "Delivered"
            return "N/A"
        w = self.gestation_weeks
        if w is None:
            return "N/A"
        if w > 40:
            return f"{w} Wks (Post-term)"
        return f"{w} Weeks"

    @property
    def pregnancy_status_display(self):
        if not self.is_currently_pregnant:
            if self.has_delivered:
                return "Delivered"
            return "Registered Mother"
        m = self.gestation_month
        w = self.gestation_weeks
        p_num = self.current_pregnancy_number
        prefix = f"Pregnancy #{p_num} • " if p_num > 1 else ""
        if w is not None and w > 40:
            return f"{prefix}Month 9 (Post-term, {w} Wks)"
        return f"{prefix}Month {m} ({w} Weeks)"


class pregnancy_record(models.Model):
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    ASHA=models.ForeignKey(asha_worker,on_delete=models.CASCADE)
    previous_pregnency_count=models.IntegerField()
    expected_delivery_date=models.DateField()
    checkup_date=models.DateField()
    weight=models.FloatField()
    height=models.FloatField()
    blood_pressure=models.TextField()
    hemoglobin=models.FloatField()
    health_status=models.TextField()
    additional_report=models.TextField()
    next_checkup_date=models.DateField()

    @property
    def gestation_weeks(self):
        edd = self.expected_delivery_date or (self.USER.expected_delivery_date if self.USER else None)
        if not edd or not self.checkup_date:
            return None
        days_left = (edd - self.checkup_date).days
        gest_days = 280 - days_left
        if gest_days < 0:
            return 0
        return gest_days // 7

    @property
    def gestation_month(self):
        w = self.gestation_weeks
        if w is None:
            return None
        m = (w // 4) + 1
        return min(m, 9)

    @property
    def gestation_week_display(self):
        w = self.gestation_weeks
        if w is None:
            return "N/A"
        if w > 40:
            return f"Week {w} (Post-term)"
        return f"Week {w}"

    @property
    def gestational_stage(self):
        w = self.gestation_weeks
        m = self.gestation_month
        if w is None:
            return "N/A"
        return f"Month {m} (Week {w})"


class child(models.Model):
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    ASHA=models.ForeignKey(asha_worker,on_delete=models.CASCADE)
    child_name=models.TextField()
    gender=models.TextField()
    date_of_birth=models.DateField()
    birth_weight=models.FloatField()
    birth_height=models.FloatField()
    blood_group=models.TextField()
    place_of_birth=models.TextField()
    delivery_type=models.TextField()
    hospital=models.TextField(blank=True, null=True)
    health_status=models.TextField()

class child_growth_record(models.Model):
    CHILD=models.ForeignKey(child,on_delete=models.CASCADE)
    height=models.FloatField()
    weight=models.FloatField()
    growth_date=models.DateField()
    health_condition=models.TextField()
    report_details=models.TextField()

class vaccination(models.Model):
    CHILD=models.ForeignKey(child,on_delete=models.CASCADE, null=True, blank=True)
    vaccine_code=models.TextField(null=True, blank=True)
    vaccine_name=models.TextField()
    vaccine_type=models.TextField()
    target_month=models.IntegerField(null=True, blank=True, default=0)
    description=models.TextField(null=True, blank=True)
    vaccination_date=models.DateField(null=True, blank=True)
    status=models.TextField(default='Scheduled')

    @property
    def target_month_display(self):
        if self.target_month is None:
            return "General"
        if self.target_month == 0:
            return "Month 0 (At Birth)"
        if self.target_month == 1:
            return "Month 1 (1st Month)"
        if self.target_month == 2:
            return "Month 2 (2nd Month)"
        if self.target_month == 3:
            return "Month 3 (3rd Month)"
        if self.target_month >= 12 and self.target_month % 12 == 0:
            yrs = self.target_month // 12
            return f"Month {self.target_month} ({yrs} Year{'s' if yrs > 1 else ''})"
        return f"Month {self.target_month}"


class notification(models.Model):
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    message=models.TextField()
    notification_date=models.DateField()

class vaccine_schedule(models.Model):
    VACCINATION=models.ForeignKey(vaccination,on_delete=models.CASCADE)
    schedule_date=models.DateField()
    time_from=models.TimeField()
    time_to=models.TimeField()

class nutrition_kit(models.Model):
    TEACHER=models.ForeignKey(anganwadi_teacher,on_delete=models.CASCADE)
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    kit_type=models.TextField()
    product_name=models.TextField()
    product_details=models.TextField()
    date=models.DateField()
    distribution_date=models.DateField()
    quantity=models.IntegerField()
    status=models.TextField(default='Pending')

class kit_stock(models.Model):
    TEACHER=models.ForeignKey(anganwadi_teacher, on_delete=models.CASCADE)
    kit_category=models.TextField(default='Pregnant Care Kit')
    product_name=models.TextField()
    product_details=models.TextField(blank=True, default='')
    stock_unit=models.TextField(default='Packs')
    quantity=models.IntegerField(default=0)
    date=models.DateField(auto_now_add=True)

    @property
    def kit_type(self):
        return self.kit_category

    def __str__(self):
        return f"{self.product_name} - {self.quantity} {self.stock_unit}"

class kit_notification(models.Model):
    NUTRITION=models.ForeignKey(nutrition_kit,on_delete=models.CASCADE)
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    notification_message=models.TextField()
    notification_date=models.DateField()

class report(models.Model):
    report_type=models.TextField()
    report_details=models.TextField()
    generated_date=models.DateField()


class notification_seen(models.Model):
    USER = models.ForeignKey(user_table, on_delete=models.CASCADE)
    notif_id = models.CharField(max_length=64)
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('USER', 'notif_id')
