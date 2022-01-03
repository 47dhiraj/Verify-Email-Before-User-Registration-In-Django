from django.contrib.auth.models import User
from accounts.models import Profile
from datetime import datetime


print('cron page running......')

def registration_expiry_check():
    today = datetime.today()
    profiles = Profile.objects.filter(signup_confirmation=False)
    for p in profiles:
        print(p)
        print(p.user)
        expdate = p.expiration_date
        if expdate < today:
            p.user.delete()

    





