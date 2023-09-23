# Images Management API

This project encompasses an API developed using Django REST Framework (DRF), tailored to enable users to seamlessly upload and efficiently manage images in both PNG and JPG formats. The API is structured with distinct account tiers, each offering a spectrum of functionalities.


## Features

- **Image Upload**: Users can upload images in PNG or JPG format via HTTP requests.
- **Image Listing**: Users can list all the images they have uploaded.
- **Different Account Tiers**: The API supports different account tiers with various functionalities:
  - **Basic**
    - 200px height thumbnail link
  - **Premium**
    - 200px height thumbnail link
    - 400px height thumbnail link
    - Original image link
  - **Enterprise**
    - 200px and 400px height thumbnail links
    - Original image link
    - Ability to fetch expiring image links (valid between 300 and 30000 seconds)
- **Admin-defined Account Tiers**: Apart from the built-in tiers, admins can create custom tiers with configurable settings through the django-admin interface.
- **Browsable API**: The project utilizes DRF's browsable API, avoiding the need for a custom user UI.

### Using Docker
remember to create the file settings_local.py in the project folder and configure your database example you have in settings_local.example

1. Install [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/).
2. Run `docker-compose up --build` to start the services.
3. The API will be available at `http://localhost:8050`.

if you want to have css and static when you start docker you have to do
1. launch docker with the script above and in a new terminal type this command `docker container ls `
2. then I type a command like this `docker exec -it 'images-web-1' /bin/bash`
3. then add this command and exit the terminal  `python manage.py collectstatic --noinput`

### Manual Setup

1. Configure and activate the virtual environment I recommend using python at least 3.10 .
2. create a settings_local.py file in your project folder and configure your database the example you have in settings_local.example
3. Install the required packages using `pip install -r requirements_dev.txt`.
4. Run migrations using `python manage.py migrate`.
5. Start the Django development server using `python manage.py runserver`.
6. The API will be available at `http://127.0.0.1:8000`.

## Testing

To run the tests, execute the following command:

`python manage.py test`
