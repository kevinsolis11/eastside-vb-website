import sys
from django.contrib.auth import get_user_model

def ensure(username, password, email):
    User = get_user_model()
    try:
        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()
        print(f"UPDATED:{username}")
    except User.DoesNotExist:
        u = User.objects.create_superuser(username=username, email=email, password=password)
        print(f"CREATED:{username}")


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) % 3 != 0 or not args:
        print('Usage: rotate_pw.py username password email [username password email ...]')
        sys.exit(1)
    for i in range(0, len(args), 3):
        ensure(args[i], args[i+1], args[i+2])
