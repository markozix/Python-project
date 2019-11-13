import csv
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studservice.settings")
import django

django.setup()

from studserviceapp.models import Student, Grupa, Nalog, Semestar, Predmet, Nastavnik, RasporedNastave, Termin


def import_timetable_from_csv(file_path):
    # popuni foreign keyeve koje ne citamo iz csv-a

    if (Semestar.objects.filter(skolska_godina_pocetak=2018).count() < 1):
        semestar1 = Semestar(vrsta='neparni', skolska_godina_pocetak=2018, skolska_godina_kraj=2019)
        semestar1.save()

    if (RasporedNastave.objects.filter(datum_unosa='2018-10-25').count() < 1):
        raspored = RasporedNastave(datum_unosa='2018-10-25')
        raspored.semestar = semestar1
        raspored.save()

    with open(file_path, encoding='utf-8') as csvfile:
        raspored_csv = csv.reader(csvfile, delimiter=';')
        cnt = 0
        check = -1
        check2 = 1
        predmet = ''
        termin = []
        keyss = []
        recnik = {}
        for red in raspored_csv:
            if (cnt == 2):  # specijalan slucaj za predmet
                predmet = red[0]

            if (cnt == 1):  # redosled tipova termina
                red = list(filter(None, red))
                termin = red

            elif (check == 1):  # izdvajamo trenutni predmet
                predmet = red[0]
                recnik = {}
                check *= -1
                check2 *= -1

            elif (len(
                    red) == 0):  # provera za naziv predmeta, posle praznog reda ide naziv predmeta pa podesimo check flag
                check = 1

            elif (check2 == 1 or cnt == 2):  # pravimo 'heder'
                check2 *= -1
                keyss2 = red
                keyss = keyss2[1:8]

            else:
                red.remove(red[0])
                cnt2 = 0
                for t in range(0, 3):
                    for r in keyss:
                        recnik[r] = red[cnt2]
                        cnt2 += 1
                    cnt2 += 1
                    if (
                            recnik[keyss[
                                0]]):  # ako nije prazan, u sledecem bloku imamo sve informacije za kreiranje modela
                        tmp = recnik['Nastavnik(ci)']
                        tmp2 = tmp.split(' ')
                        prezime_profesora = tmp2[0]
                        ime_profesora = tmp2[1]
                        user = ime_profesora.lower()
                        user = user[0:1]
                        user += prezime_profesora.lower()

                        if (Nalog.objects.filter(username=user).count() < 1):
                            nalogDB = Nalog(username=user, uloga='nastavnik')
                            nalogDB.save()

                        if (Predmet.objects.filter(naziv=predmet).count() < 1):
                            predmetDB = Predmet(naziv=predmet)
                            predmetDB.save()

                        tmp = recnik['Odeljenje']
                        grupe = tmp.split(', ')
                        for g in grupe:
                            if (Grupa.objects.filter(oznaka_grupe=g).count() < 1):
                                grupaDB = Grupa(oznaka_grupe=g, semestar=semestar1)
                                grupaDB.save()

                        if (Nastavnik.objects.filter(ime=ime_profesora, prezime=prezime_profesora).count() < 1):
                            nastavnikDB = Nastavnik(ime=ime_profesora, prezime=prezime_profesora)
                            nalog_tmp = Nalog.objects.get(username=user)
                            nastavnikDB.nalog = nalog_tmp
                            nastavnikDB.save()
                            predmet_tmp = Predmet.objects.get(naziv=predmet)
                            nastavnikDB.predmet.add(predmet_tmp)
                        else:
                            nastavnikDB = Nastavnik.objects.get(ime=ime_profesora, prezime=prezime_profesora)
                            predmet_tmp = Predmet.objects.get(naziv=predmet)
                            nastavnikDB.predmet.add(predmet_tmp)

                        tmp = recnik['Èas']
                        tmp2 = tmp.split('-')
                        poce = tmp2[0]
                        if (len(poce) < 4):
                            poce.append(':00')
                        kraj = tmp2[1]
                        if (len(kraj) < 4):
                            kraj += ':00'
                        if (Termin.objects.filter(oznaka_ucionice=recnik['Uèionica'], dan=recnik['Dan'],
                                                  pocetak=poce).count() < 1):
                            terminDB = Termin(oznaka_ucionice=recnik['Uèionica'], pocetak=poce, zavrsetak=kraj,
                                              dan=recnik['Dan'], tip_nastave=termin[t])
                            nastavnik_tmp = Nastavnik.objects.get(ime=ime_profesora, prezime=prezime_profesora)
                            terminDB.nastavnik = nastavnik_tmp
                            predmet_tmp = Predmet.objects.get(naziv=predmet)
                            terminDB.predmet = predmet_tmp
                            terminDB.raspored = raspored
                            terminDB.save()
                            for g in grupe:
                                terminDB.grupe.add(Grupa.objects.get(oznaka_grupe=g))

            cnt += 1

    print('Kraj')


# import_timetable_from_csv('rasporedCSV.csv')
