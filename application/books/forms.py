#Sisältää kirjojen käsittelyyn tarvittavat lomakkeet

from flask_wtf import FlaskForm
from wtforms import StringField, validators

class BookForm(FlaskForm):
    author_firstname = StringField("Kirjailijan etunimi", [validators.Length(min=2)])
    author_lastname = StringField("Kirjailijan sukunimi", [validators.Length(min=2)])
    name = StringField("Kirjan nimi", [validators.Length(min=2)])

    class Meta:
        csrf = False
