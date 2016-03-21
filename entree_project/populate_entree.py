# populates the entree database with an admin user and test user
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entree_project.settings')

import django
django.setup()

import argparse
from entree.models import UserProfile
from django.contrib.auth.models import User

SUPERUSER_PASSWORD = '6sEzVx4oeD7Xct6K7y0Q'
TEST_USER_PASSWORD = 'cs411entree'
DEFAULT_SEARCH_RADIUS = 10  # miles


def populate():

    # check if the database is already populated
    if len(UserProfile.objects.all()) > 0:
        print('The database is already populated. Please flush the database before repopulating\nusing:')
        print('python manage.py flush\n')
        return

    # create admin user (superuser)
    print('Creating superuser...')
    add_superuser(
        username="admin",
        first_name="Admin",
        last_name="User"
    )

    # create standard user
    print('Creating standard user...')
    add_user(
        username="testuser",
        first_name="Test",
        last_name="User"
    )


def summarize():
    pass


def add_superuser(username, first_name, last_name):
    password = SUPERUSER_PASSWORD
    email = generate_email(username)
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    profile = UserProfile(
        user=user,
        search_radius=DEFAULT_SEARCH_RADIUS
    )
    profile.save()


def add_user(username, first_name, last_name):
    password = TEST_USER_PASSWORD
    email = generate_email(username)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    profile = UserProfile(
        user=user,
        search_radius=DEFAULT_SEARCH_RADIUS
    )
    profile.save()


def generate_email(username):
    return username + "@entree.com"


# Execute population script
if __name__ == '__main__':

    # setup command line parser
    parser = argparse.ArgumentParser(description='Populates the Entree database with test data.')
    args = vars(parser.parse_args())

    print("=" * 80)
    print("STARTING ENTREE DATABASE POPULATION SCRIPT")
    print("=" * 80)

    populate()
    summarize()

    print("=" * 80)
    print("ENTREE DATABASE POPULATION COMPLETE")
    print("=" * 80)
