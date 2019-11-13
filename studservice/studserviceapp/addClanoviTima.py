"""
Skripta za dodavanje studenata koji su clanovi tima u bazu.
Student nece biti dodan ukoliko grupa u koju se dodaje ne postoji!
"""

import os, datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studservice.settings")
import django
django.setup()
from studserviceapp.models import Student, Nalog, Grupa

godina = datetime.datetime.now().year

matovicNalog = Nalog(username='mmatovic16', lozinka=None, uloga='student')
matovicNalog.save()
#try:
#    matovicGrupa = Grupa.objects.get(oznaka_grupe=301, semestar__skolska_godina_pocetak=godina, semestar__vrsta='neparni')
#except Grupa.DoesNotExist:
#    print("Grupa ne postoji, student ne moze biti dodan!")
#else:
matovicStudent = Student(ime='Marko', prezime='Matovic', broj_indeksa=8, godina_upisa=2016, smer='RN', nalog=matovicNalog)
matovicStudent.save()
#    matovicStudent.grupa.add(matovicGrupa)
#    matovicStudent.save()

vukicevicNalog = Nalog(username='mvukicevic16', lozinka=None, uloga='student')
vukicevicNalog.save()
#try:
#    vukicevicGrupa = Grupa.objects.get(oznaka_grupe=303, semestar__skolska_godina_pocetak=godina, semestar__vrsta='neparni')
#except Grupa.DoesNotExist:
#    print("Grupa ne postoji, student ne moze biti dodan!")
#else:
vukicevicStudent = Student(ime='Marko', prezime='Vukicevic', broj_indeksa=29, godina_upisa=2016, smer='RN', nalog=vukicevicNalog)
vukicevicStudent.save()
#    vukicevicStudent.grupa.add(vukicevicGrupa)
#    vukicevicStudent.save()

bakarecNalog = Nalog(username='bbakarec16', lozinka=None, uloga='student')
bakarecNalog.save()
#try:
#    bakarecGrupa = Grupa.objects.get(oznaka_grupe=301, semestar__skolska_godina_pocetak=godina, semestar__vrsta='neparni')
#except Grupa.DoesNotExist:
#    print("Grupa ne postoji, student ne moze biti dodan!")
#else:
bakarecStudent = Student(ime='Bogdan', prezime='Bakarec', broj_indeksa=20, godina_upisa=2016, smer='RN', nalog=bakarecNalog)
bakarecStudent.save()
#    bakarecStudent.grupa.add(bakarecGrupa)
#    bakarecStudent.save()