from .flask_wtf import FlaskForm
from .wtforms import StringField
from .wtforms.fields.html5 import URLField


class SearchForm(FlaskForm):
    search = StringField('enter movie name')


class DetailsForm(FlaskForm):
    image_url = URLField('Image URL')
    cast_list = StringField('custom cast list')
