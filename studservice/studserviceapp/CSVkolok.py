import codecs
import csv
import datetime
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studservice.settings")
import django

django.setup()

from studserviceapp.models import RasporedPolaganja, TerminPolaganja, Nastavnik, Predmet


def import_week_from_csv(file, broj):
    knedelja_csv = csv.reader(codecs.iterdecode(file, 'utf-8'), delimiter=',')
    cnt = 0
    if RasporedPolaganja.objects.filter(kolokvijumska_nedelja=broj).count() < 1:
        rasp = RasporedPolaganja(kolokvijumska_nedelja=broj)
        rasp.save()

    losi = []
    poruke = []
    for red in knedelja_csv:
        cnt2 = 0
        rec = {}
        for kolona in red:
            if cnt > 0:
                # Predmet,,,Profesor,UÄionice,Vreme,Dan,Datum
                if cnt2 == 0:
                    rec['predmet'] = kolona
                if cnt2 == 3:
                    rec['profesor'] = kolona
                if cnt2 == 4:
                    rec['ucionica'] = kolona
                if cnt2 == 5:
                    rec['vreme'] = kolona
                if cnt2 == 6:
                    rec['dan'] = kolona
                if cnt2 == 7:
                    rec['datum'] = kolona
                cnt2 += 1
        cnt += 1
        if rec:
            pocetak = rec['vreme'].split('-')[0] + ':00'
            kraj = rec['vreme'].split('-')[1] + ':00'
            datum = str(datetime.datetime.now().year) + '-' + rec['datum'][3] + rec['datum'][4] + '-' + rec['datum'][
                0] + rec['datum'][1]
            if 0 < int(rec['datum'].split('.')[0]) < 32 and 0 < int(rec['datum'].split('.')[1]) < 13:
                if TerminPolaganja.objects.filter(ucionice=rec['ucionica'], pocetak=pocetak, zavrsetak=kraj,
                                                  datum=datum).count() < 1:
                    nastavnik = rec['profesor']
                    tmp2 = nastavnik.split(' ')
                    prezime_profesora = tmp2[1]
                    ime_profesora = tmp2[0]

                    if Nastavnik.objects.filter(ime=ime_profesora, prezime=prezime_profesora).count() > 0:
                        if Predmet.objects.filter(naziv=rec['predmet']).count() > 0:
                            terminPolaganjaDB = TerminPolaganja(ucionice=rec['ucionica'], pocetak=pocetak, zavrsetak=kraj,
                                                                datum=datum)
                            nastavnik_tmp = Nastavnik.objects.get(ime=ime_profesora, prezime=prezime_profesora)
                            predmet_tmp = Predmet.objects.get(naziv=rec['predmet'])
                            raspored_tmp = RasporedPolaganja.objects.get(kolokvijumska_nedelja=broj)
                            terminPolaganjaDB.nastavnik = nastavnik_tmp
                            terminPolaganjaDB.predmet = predmet_tmp
                            terminPolaganjaDB.raspored_polaganja = raspored_tmp
                            terminPolaganjaDB.save()
                        else:
                            losi.append(rec)
                            poruke.append('nema predmeta!!!!!!!!!')

                    else:
                        losi.append(rec)
                        if Predmet.objects.filter(naziv=rec['predmet']).count() > 0:
                            poruke.append('nema nastavnika!!!!!!!!!')
                        else:
                            poruke.append('nema nastavnika i predmeta!!!!!!!!!')
            else:
                losi.append(rec)
                if Predmet.objects.filter(naziv=rec['predmet']).count() > 0:
                    if Nastavnik.objects.filter(ime=ime_profesora, prezime=prezime_profesora).count() > 0:
                        poruke.append('ne valja datum!!!!!!!!!')
                    else:
                        poruke.append('ne valja datum, nema nastavnika!!!!!!!!!')
                else:
                    if Nastavnik.objects.filter(ime=ime_profesora, prezime=prezime_profesora).count() > 0:
                        poruke.append('ne valja datum, nema predmeta!!!!!!!!!')
                    else:
                        poruke.append('ne valja datum, nema nastavnika i predmeta!!!!!!!!!')


    return losi, poruke


def obradi(rec):
    cnt = 0
    pocetak = rec['vreme'].split('-')[0] + ':00'
    kraj = rec['vreme'].split('-')[1] + ':00'
    datum = str(datetime.datetime.now().year) + '-' + rec['datum'][3] + rec['datum'][4] + '-' + \
            rec['datum'][
                0] + rec['datum'][1]
    if TerminPolaganja.objects.filter(ucionice=rec['ucionica'], pocetak=pocetak, zavrsetak=kraj,
                                      datum=datum).count() < 1:
        nastavnik = rec['profesor']
        tmp2 = nastavnik.split(' ')
        prezime_profesora = tmp2[1]
        ime_profesora = tmp2[0]

        if Nastavnik.objects.filter(ime=ime_profesora, prezime=prezime_profesora).count() > 0:
            if Predmet.objects.filter(naziv=rec['predmet']).count() > 0:
                terminPolaganjaDB = TerminPolaganja(ucionice=rec['ucionica'], pocetak=pocetak,
                                                    zavrsetak=kraj,
                                                    datum=datum)
                nastavnik_tmp = Nastavnik.objects.get(ime=ime_profesora, prezime=prezime_profesora)
                predmet_tmp = Predmet.objects.get(naziv=rec['predmet'])
                raspored_tmp = RasporedPolaganja.objects.get(kolokvijumska_nedelja=rec['broj'])
                terminPolaganjaDB.nastavnik = nastavnik_tmp
                terminPolaganjaDB.predmet = predmet_tmp
                terminPolaganjaDB.raspored_polaganja = raspored_tmp
                terminPolaganjaDB.save()
                cnt += 1

    return cnt