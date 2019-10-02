# Enterprise Django School Management System

An Enterprise Online High school management Portal.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all requirements.

> First thing first clone this repository

```bash
git clone https://github.com/Abdoulrasheed/django-enterprise-school.git
```

> Next, change directory to the root of the project
```bash
cd django-enterprise-school
```

> Install requirements

```bash
pip install -r requirements.txt
```

> Edit Host file and add some subdomains

```bash
sudo nano /etc/hosts
```

> Create a public tenant

```
from schools.models import Client, Domain

# create your public tenant
tenant = Client(schema_name='public',
				description='the public tenant',
                name='Schemas Inc.',
                active_until='2016-12-05',
                on_trial=False)
tenant.save()

domain = Domain()
domain.domain = 'my-domain.com' # root domain
domain.tenant = tenant
domain.is_primary = True
domain.save()
```

> Migrate Database

```
python manage.py migrate_schemas
```

> Create tenant su

```
python manage.py create_tenant_superuser
```

Choose public tenant and create the user

Now visit admin.<domain> (eg _admin.example.local_)

> Done


## TODO

> - [x] Add Sudmomains

> - [x] Add Saas Support

> - [x] Add Email Notification

> - [ ] Notification Module should be asynchronous

> - [ ] Add Library

> - [ ] Add Hostel

> - [ ] Add Student / Teacher ID Card Generation

> - [ ] Add Admission Letter with support of different templates

> - [ ] Add Markdown to allow customising admission template


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## Attribution
### Commercial usage is prohibited