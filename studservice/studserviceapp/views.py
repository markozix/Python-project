from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import F
from django import forms
from django.forms import formset_factory
from studserviceapp.send_gmails import create_and_send_message
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from studserviceapp.CSVkolok import import_week_from_csv, obradi
from studserviceapp.CSVparser import import_timetable_from_csv
from studserviceapp.models import Student, Grupa, Termin, Nastavnik, Predmet, Nalog, Semestar, IzborGrupe, IzbornaGrupa, \
    Obavestenje
import datetime
from studserviceapp.util import get_current_semester


# Create your views here.

def index(request):
    """
    Pocetna stranica
    """
    return HttpResponse("Dobrodosli na studentski servis")


def timetableforuser(request, username):
    """
    Prikazivanje rasporeda korisnika
    """
    response = HttpResponse()

    request.session['username'] = username

    timetable = []

    trenutnaGodina = datetime.datetime.now().year
    trenutniMesec = datetime.datetime.now().month
    if trenutniMesec <= 2 or trenutniMesec >= 10:
        trenutniSemestar = 'neparni'
    else:
        trenutniSemestar = 'parni'

    obavestenja = Obavestenje.objects.all().order_by('-id')[:5]
    # obavestenja_reversed = reversed(obavestenja)

    try:
        nalog = Nalog.objects.get(username=username)
    except Nalog.DoesNotExist:
        return HttpResponse("Zeljeni korisnik ne postoji!")
    except Nalog.MultipleObjectsReturned:
        return HttpResponse("Greska u bazi, molimo kontaktirajte studentsku sluzbu!")
    if nalog.uloga == 'nastavnik':

        try:
            nastavnik = Nastavnik.objects.get(nalog__username=username)
        except Nastavnik.DoesNotExist:
            return HttpResponse("Zeljeni korisnik ne postoji!")
        except Nastavnik.MultipleObjectsReturned:
            return HttpResponse("Greska u bazi, molimo kontaktirajte studentsku sluzbu!")
        else:
            # response.write(f'Raspored za nastavnika: {nastavnik.ime} {nastavnik.prezime}<br><br>')
            rasporedZaNastavnika = nastavnik.ime + " " + nastavnik.prezime;

            predmeti = nastavnik.predmet.all()
            if len(predmeti) < 1:
                return HttpResponse("Profesoru nije dodeljen nijedan predmet!")

            for predmet in predmeti:

                response.write(f'Raspored za predmet: {predmet.naziv}')
                response.write('<br>')

                termini = Termin.objects.filter(predmet_id=predmet.id, nastavnik=nastavnik).values()
                if len(termini) < 1:
                    # response.write("Profesor nema zakazanih termina za ovaj predmet!<br>")
                    # continue
                    return HttpResponse("Profesor nema zakazanih termina za ovaj predmet!")

                for terminQS in termini:
                    termin = Termin.objects.get(id=terminQS['id'])

                    # response.write(f'Predmet: {termin.predmet.naziv} ')

                    # response.write(f'Tip nastave: {termin.tip_nastave} ')

                    # response.write(f'Nastavnik: {termin.nastavnik.ime} {termin.nastavnik.prezime} ')

                    # response.write('Grupe: ')
                    brojGrupa = len(termin.grupe.all())
                    counter = 0

                    grupeNaPredmetu = ''
                    for grupa in termin.grupe.all():
                        if counter < brojGrupa - 1:
                            # response.write(f'{grupa.oznaka_grupe}, ')
                            grupeNaPredmetu += (grupa.oznaka_grupe + ', ')
                        else:
                            # response.write(f'{grupa.oznaka_grupe} ')
                            grupeNaPredmetu += (grupa.oznaka_grupe)
                        counter += 1

                    # response.write(f'Dan: {termin.dan} ')

                    # response.write(f'Pocetak: {termin.pocetak} ')
                    # response.write(f'Zavrsetak: {termin.zavrsetak} ')

                    # response.write(f'Oznaka ucionice: {termin.oznaka_ucionice} ')
                    # response.write('<br>')

                    predmetRed = (termin.predmet.naziv, termin.tip_nastave, rasporedZaNastavnika,
                                  grupeNaPredmetu, termin.dan, termin.pocetak, termin.zavrsetak, termin.oznaka_ucionice)
                    timetable.append(predmetRed)

                # response.write('<br>')

            context = {'redovi': timetable, 'rasporedZaNastavnika': rasporedZaNastavnika,
                       'username': request.session['username'], 'uloga': nalog.uloga, 'obavestenja': obavestenja}
            return render(request, 'studserviceapp/timetableForUserForm.html', context)

    elif nalog.uloga == 'student':
        try:
            student = Student.objects.get(nalog__username=username)
        except Student.DoesNotExist:
            return HttpResponse("Zeljeni korisnik ne postoji!")
        except Student.MultipleObjectsReturned:
            return HttpResponse("Greska u bazi, molimo kontaktirajte studentsku sluzbu!")
        else:
            try:
                if trenutniSemestar == 'neparni':
                    if trenutniMesec <= 2:
                        grupa = student.grupa.get(semestar__skolska_godina_pocetak=trenutnaGodina - 1,
                                                  semestar__vrsta='neparni')
                    else:
                        grupa = student.grupa.get(semestar__skolska_godina_pocetak=trenutnaGodina,
                                                  semestar__vrsta='neparni')
                else:
                    grupa = student.grupa.get(semestar__skolska_godina_kraj=trenutnaGodina, semestar__vrsta='parni')
            except Grupa.DoesNotExist:
                return HttpResponse("Student nije ni u jednoj vazecoj grupi!")
            except Grupa.MultipleObjectsReturned:
                return HttpResponse("Greska u bazi, molimo kontaktirajte studentsku sluzbu!")

            # response.write(f'Raspored za grupu: {grupa.oznaka_grupe}<br>')
            rasporedZaGrupu = grupa.oznaka_grupe

            termini = Termin.objects.filter(grupe__oznaka_grupe=grupa.oznaka_grupe).values()
            if len(termini) < 1:
                # response.write('Grupa studenta nema nijedno dodeljeno predavanje!')
                return HttpResponse('Grupa studenta nema nijedno dodeljeno predavanje!')
            for terminQS in termini:
                termin = Termin.objects.get(id=terminQS['id'])

                # response.write(f'Predmet: {termin.predmet.naziv} ')

                # response.write(f'Tip nastave: {termin.tip_nastave} ')

                # response.write(f'Nastavnik: {termin.nastavnik.ime} {termin.nastavnik.prezime} ')

                # response.write('Grupe: ')
                brojGrupa = len(termin.grupe.all())
                counter = 0

                grupeNaPredmetu = ''
                for grupa in termin.grupe.all():
                    if counter < brojGrupa - 1:
                        # response.write(f'{grupa.oznaka_grupe}, ')
                        grupeNaPredmetu += (grupa.oznaka_grupe + ', ')
                    else:
                        # response.write(f'{grupa.oznaka_grupe} ')
                        grupeNaPredmetu += (grupa.oznaka_grupe)
                    counter += 1

                # response.write(f'Dan: {termin.dan} ')

                # response.write(f'Pocetak: {termin.pocetak} ')
                # response.write(f'Zavrsetak: {termin.zavrsetak} ')

                # response.write(f'Oznaka ucionice: {termin.oznaka_ucionice} ')
                # response.write('<br>')
                ime_prezime_nastavnika = termin.nastavnik.ime + " " + termin.nastavnik.prezime
                predmetRed = (termin.predmet.naziv, termin.tip_nastave, ime_prezime_nastavnika,
                              grupeNaPredmetu, termin.dan, termin.pocetak, termin.zavrsetak, termin.oznaka_ucionice)
                timetable.append(predmetRed)

            context = {'redovi': timetable, 'rasporedZaGrupu': rasporedZaGrupu, 'username': request.session['username'],
                       'uloga': nalog.uloga, 'obavestenja': obavestenja}
            return render(request, 'studserviceapp/timetableForUserForm.html', context)
    else:
        termini = Termin.objects.all()
        if len(termini) < 1:
            # response.write('Grupa studenta nema nijedno dodeljeno predavanje!')
            return HttpResponse('Ne postoji raspored!')
        for terminQS in termini:
            termin = Termin.objects.get(id=terminQS.id)

            # response.write(f'Predmet: {termin.predmet.naziv} ')

            # response.write(f'Tip nastave: {termin.tip_nastave} ')

            # response.write(f'Nastavnik: {termin.nastavnik.ime} {termin.nastavnik.prezime} ')

            # response.write('Grupe: ')
            brojGrupa = len(termin.grupe.all())
            counter = 0

            grupeNaPredmetu = ''
            for grupa in termin.grupe.all():
                if counter < brojGrupa - 1:
                    # response.write(f'{grupa.oznaka_grupe}, ')
                    grupeNaPredmetu += (grupa.oznaka_grupe + ', ')
                else:
                    # response.write(f'{grupa.oznaka_grupe} ')
                    grupeNaPredmetu += (grupa.oznaka_grupe)
                counter += 1

            # response.write(f'Dan: {termin.dan} ')

            # response.write(f'Pocetak: {termin.pocetak} ')
            # response.write(f'Zavrsetak: {termin.zavrsetak} ')

            # response.write(f'Oznaka ucionice: {termin.oznaka_ucionice} ')
            # response.write('<br>')

            ime_prezime_nastavnika = termin.nastavnik.ime + " " + termin.nastavnik.prezime
            predmetRed = (termin.predmet.naziv, termin.tip_nastave, ime_prezime_nastavnika,
                          grupeNaPredmetu, termin.dan, termin.pocetak, termin.zavrsetak, termin.oznaka_ucionice)
            timetable.append(predmetRed)

        context = {'redovi': timetable, 'username': request.session['username'], 'uloga': nalog.uloga,
                   'obavestenja': obavestenja}
        return render(request, 'studserviceapp/timetableForUserForm.html', context)


def allsemesters(request):
    """
    Prikaz svih semestara
    :param request:
    :return:
    """
    if request.method == "POST":
        semestar = Semestar(vrsta=request.POST['vrsta_semestra'],
                            skolska_godina_pocetak=request.POST['skolska_godina_pocetak'],
                            skolska_godina_kraj=request.POST['skolska_godina_kraj'])
        semestar.save()

    qs = Semestar.objects.all()
    context = {'semestri': qs, 'username': request.session['username']}
    return render(request, 'studserviceapp/pregledsemestara.html', context)


def groupsforsemester(request, id):
    """
    Prikaz svih izbornih grupa u semestru, resava i dodavanje nove izborne grupe
    :param request:
    :param id:
    :return:
    """

    semestar = Semestar.objects.get(id=id)

    if request.method == 'POST':
        helpGrupa = request.POST.get('izborna_grupa_id', 0)
        if helpGrupa != 0 and IzbornaGrupa.objects.filter(id=request.POST['izborna_grupa_id']).count() > 0:
            grupa = IzbornaGrupa.objects.get(id=request.POST['izborna_grupa_id'])
            grupa.kapacitet = request.POST['kapacitet']
            if request.POST.get('aktivna') == 'on':
                grupa.aktivna = True
            else:
                grupa.aktivna = False

            grupa.save()

        else:
            grupa = IzbornaGrupa(oznaka_grupe=request.POST['oznaka_grupe'],
                                 oznaka_semestra=request.POST['oznaka_semestra'],
                                 kapacitet=request.POST['kapacitet'], smer=request.POST['smer'],
                                 aktivna=request.POST.get('aktivna', False), za_semestar=semestar, broj_studenata=0)
            grupa.save()
            for p in request.POST.getlist('predmeti'):
                grupa.predmeti.add(p)
            grupa.save()
            cnt = 2
            while (1):
                id = request.POST.get('oznaka' + str(cnt), 0)
                kap = request.POST.get('kapacitet' + str(cnt), 0)
                smer = request.POST.get('smer' + str(cnt), 0)
                if id != 0 and kap != 0 and smer != 0:
                    grupa2 = IzbornaGrupa(oznaka_grupe=id,
                                          oznaka_semestra=request.POST['oznaka_semestra'],
                                          kapacitet=kap, smer=smer,
                                          aktivna=request.POST.get('aktivna', False), za_semestar=semestar,
                                          broj_studenata=0)
                    grupa2.save()
                    for p2 in request.POST.getlist('predmeti'):
                        grupa2.predmeti.add(p2)
                    grupa2.save()
                else:
                    break
                cnt += 1

    qs = IzbornaGrupa.objects.filter(za_semestar=semestar)
    context = {'izbornegrupe': qs, 'semestar': semestar, 'username': request.session['username']}
    return render(request, 'studserviceapp/pregledizbornihgrupa.html', context)


def addizbornagrupa(request):
    """
    Pozivanje stranice za unos izborne grupe
    :param request:
    :return:
    """
    predmeti = Predmet.objects.all()
    semestar = Semestar.objects.get(id=request.GET['semestar'])
    context = {'semestar': semestar, 'predmeti': predmeti, 'username': request.session['username']}
    return render(request, 'studserviceapp/unosizbornegrupe.html', context)


def chooseagroup(request, username):
    """
    Provjera da li je nalog od studenta

    :param request:
    :param username:
    :return:
    """

    trenutnaGodina = datetime.datetime.now().year
    slGodina = trenutnaGodina + 1

    studenti = Student.objects.all()
    predmeti = Predmet.objects.all()

    trenutniSemestar = get_current_semester()

    nalog = Nalog.objects.get(username=username)
    if (nalog.uloga == 'student'):

        student = Student.objects.get(nalog__username=username)
        grupe = IzbornaGrupa.objects.filter(smer=student.smer, aktivna=True, broj_studenata__lt=F('kapacitet'))
        grupee = []
        for g in grupe:
            grupa = IzbornaGrupa.objects.get(id=g.id)
            grupee.append(grupa)

        if (len(grupee) < 1):
            context = {'username': username}
            return render(request, 'studserviceapp/neuspehizborgrupe.html', context)

        if (trenutniSemestar == 'neparni'):
            sem = 1
        else:
            sem = 2

        if (sem == 1):
            r1 = 1
            r2 = 3
            r3 = 5
            r4 = 7
        else:
            r1 = 2
            r2 = 4
            r3 = 6
            r4 = 8

        context = {'username': username, 's': student, 'grupe': grupee, 'predmeti': predmeti, 'p': trenutnaGodina,
                   'k': slGodina, 'r1': r1, 'r2': r2, 'r3': r3, 'r4': r4}
        return render(request, 'studserviceapp/izborgrupe.html', context)


def chooseagroupObrada(request):
    upisuje_semestar = 0
    prvi_put = False
    np = ""

    upisuje_semestar = request.POST['radioBtn']
    print(upisuje_semestar)

    if request.POST['pp'] == 'prviPut':
        prvi_put = True
    elif request.POST['pp'] == 'nijePrvi':
        prvi_put = False

    if request.POST['np'] == 'odjednom':
        np = 'odjednom'
    elif request.POST['np'] == 'narate':
        np = 'na rate'
    elif request.POST['np'] == 'stipendista':
        np = 'stipendista'

    if request.method == 'POST':
        izbGrupe = IzborGrupe(
            ostvarenoESPB=request.POST['brOpoena'],
            upisujeESPB=request.POST['brUpoena'],
            broj_polozenih_ispita=request.POST['brPispita'],
            upisuje_semestar=upisuje_semestar,
            prvi_put_upisuje_semestar=prvi_put,
            nacin_placanja=np,
            student=Student.objects.get(nalog__username=request.POST['username']),
            izabrana_grupa=IzbornaGrupa.objects.get(oznaka_grupe=request.POST['grupeX']),
            upisan=False)  # na pocetku staviti false

        student = Student.objects.get(nalog__username=request.POST['username'])

        trenutniSemestar = get_current_semester()
        try:
            if trenutniSemestar == 'neparni':
                if datetime.datetime.now().month <= 2:
                    grupa = student.grupa.get(semestar__skolska_godina_pocetak=datetime.datetime.now().year - 1,
                                              semestar__vrsta='neparni')
                else:
                    grupa = student.grupa.get(semestar__skolska_godina_pocetak=datetime.datetime.now().year,
                                              semestar__vrsta='neparni')
            else:
                grupa = student.grupa.get(semestar__skolska_godina_kraj=datetime.datetime.now().year,
                                          semestar__vrsta='parni')

            print(trenutniSemestar)
            context = {'username': request.session['username']}
            return render(request, 'studserviceapp/neuspjesnoDodatStudent.html', context)
        except Grupa.DoesNotExist:

            izbGrupe.save()

            for p23 in request.POST.getlist('predmeti'):
                izbGrupe.nepolozeni_predmeti.add(p23)
            izbGrupe.save()

            izborna_grupa = IzbornaGrupa.objects.get(oznaka_grupe=request.POST['grupe'])

            if trenutniSemestar == 'neparni':
                if datetime.datetime.now().month <= 2:
                    semestar = Semestar.objects.get(vrsta=trenutniSemestar,
                                                    skolska_godina_pocetak=datetime.datetime.now().year - 1)
                else:
                    semestar = Semestar.objects.get(vrsta=trenutniSemestar,
                                                    skolska_godina_pocetak=datetime.datetime.now().year)
            else:
                semestar = Semestar.objects.get(vrsta=trenutniSemestar,
                                                skolska_godina_pocetak=datetime.datetime.now().year)

            try:
                grupa_nova = Grupa.objects.get(oznaka_grupe=request.POST['grupe'], smer=student.smer, semestar=semestar)
            except Grupa.DoesNotExist:
                grupa_nova = Grupa(oznaka_grupe=request.POST['grupe'], smer=student.smer, semestar=semestar)
                grupa_nova.save()

            student.grupa.add(grupa_nova)
            student.save()

            broj_studenata = izborna_grupa.broj_studenata
            izborna_grupa.broj_studenata = broj_studenata + 1
            izborna_grupa.save()

            context = {'username': request.session['username']}
            return render(request, 'studserviceapp/uspjesnoDodatStudent.html', context)


def changeizbornagrupa(request, id, id2):
    """

    Pozivanje stranice za izmenu grupe
    :param request:
    :return:
    """
    predmeti = Predmet.objects.all();
    semestar = Semestar.objects.get(id=id)
    izborna_grupa = IzbornaGrupa.objects.get(id=id2)
    context = {'izborna_grupa': izborna_grupa, 'predmeti': predmeti, 'semestar': semestar,
               'username': request.session['username']}
    return render(request, 'studserviceapp/izmenaizbornegrupe.html', context)


def addsemester(request):
    context = {'username': request.session['username']}
    return render(request, 'studserviceapp/unossemestra.html', context)


def viewgroups(request):
    """

    Pregled grupa za semestar
    :param request:
    :return:
    """

    trenSeme = get_current_semester()
    mesec = datetime.datetime.now().month
    godina = datetime.datetime.now().year
    if trenSeme == 'parni':
        semestar = Semestar.objects.get(skolska_godina_kraj=godina, vrsta=trenSeme)
    else:
        if mesec <= 2:
            semestar = Semestar.objects.get(skolska_godina_pocetak=godina - 1, vrsta=trenSeme)
        else:
            semestar = Semestar.objects.get(skolska_godina_pocetak=godina, vrsta=trenSeme)
    qs = IzbornaGrupa.objects.filter(za_semestar=semestar)
    nalog = Nalog.objects.get(username=request.session['username'])
    context = {'izbornegrupe': qs, 'semestar': semestar, 'username': request.session['username'], 'uloga': nalog.uloga}
    return render(request, 'studserviceapp/prikazigrupe.html', context)


def viewstudents(request, id):
    """

    :param request:
    :param id:
    :return:
    """

    ig = IzbornaGrupa.objects.get(id=id)
    students = Student.objects.filter(grupa__oznaka_grupe=ig.oznaka_grupe)
    nalog = Nalog.objects.get(username=request.session['username'])
    context = {'izbornegrupe': ig, 'students': students, 'username': request.session['username'], 'uloga': nalog.uloga}
    return render(request, 'studserviceapp/prikazistudente.html', context)


def addkolok(request):
    if request.method == 'POST':
        form = UploadKlkRaspored(request.POST, request.FILES)
        if form.is_valid():
            raspored_file = request.FILES['nedelja']
            broj = form.cleaned_data['broj']
            losi, poruke = import_week_from_csv(raspored_file, broj)
            zipovano = zip(losi, poruke)
            if len(losi) == 0:
                return render(request, 'studserviceapp/klkuspeh.html', {'username': request.session['username']})
            else:
                context = {'zipovano': zipovano, 'broj': broj, 'username': request.session['username']}
                return render(request, 'studserviceapp/klkneuspeh.html', context)
    else:
        form = UploadKlkRaspored()
    return render(request, 'studserviceapp/dodajkolok.html', {'form': form, 'username': request.session['username']})


def addklksuccess(request):
    if request.method == 'POST':
        cnt = 1
        cnt2 = 0
        cnt3 = 1
        rec = {}
        for key in request.POST.keys():
            cnt3 += 1
            cnt2 += 1
            if cnt2 > 6:
                cnt2 = 1
                cnt += 1
                if cnt3 < len(request.POST.keys()):
                    rec['broj'] = request.POST['broj']
                    uspesnih = obradi(rec)
                    rec = {}
            s = str(cnt) + str(cnt2)
            key_rec = ''
            if cnt2 == 1:
                s2 = 'predmet'
                key_rec = s2
            elif cnt2 == 2:
                s2 = 'profesor'
                key_rec = s2
            elif cnt2 == 3:
                s2 = 'ucionica'
                key_rec = s2
            elif cnt2 == 4:
                s2 = 'vreme'
                key_rec = s2
            elif cnt2 == 5:
                s2 = 'dan'
                key_rec = s2
            elif cnt2 == 6:
                s2 = 'datum'
                key_rec = s2
            s = s + s2
            if cnt3 < len(request.POST.keys()):
                value = request.POST[s]
                rec[key_rec] = value

    if uspesnih == cnt - 1:
        return render(request, 'studserviceapp/klkuspeh.html', {'username': request.session['username']})
    else:
        form = UploadKlkRaspored()
        return render(request, 'studserviceapp/dodajkolok.html',
                      {'form': form, 'username': request.session['username']})


class UploadKlkRaspored(forms.Form):
    broj = forms.CharField(label='Broj nedelje:', max_length=100)
    nedelja = forms.FileField(label='Izaberite raspored:')


def prikazStudentaZaUploadSlike(request, username):
    nalog = Nalog.objects.get(username=username)

    if (nalog.uloga == 'student'):
        student = Student.objects.get(nalog__username=username)

        ime = student.ime
        prezime = student.prezime
        brindeksa = student.broj_indeksa
        godupisa = student.godina_upisa
        smjer = student.smer

        trenutniSemestar = get_current_semester()
        if trenutniSemestar == 'neparni':
            if datetime.datetime.now().month <= 2:
                grupa = student.grupa.get(semestar__skolska_godina_pocetak=datetime.datetime.now().year - 1,
                                          semestar__vrsta='neparni')
            else:
                grupa = student.grupa.get(semestar__skolska_godina_pocetak=datetime.datetime.now().year,
                                          semestar__vrsta='neparni')
        else:
            grupa = student.grupa.get(semestar__skolska_godina_kraj=datetime.datetime.now().year,
                                      semestar__vrsta='parni')

        context = {'ime': ime, 'prezime': prezime, 'brindeksa': brindeksa, 'godupisa': godupisa,
                   'smjer': smjer, 'grupa': grupa.oznaka_grupe, 'username': username}

        return render(request, 'studserviceapp/uploadSlike.html', context)


def obradaSlike(request):
    student = Student.objects.get(nalog__username=request.POST['username'])
    slika = request.FILES['slika']

    student.slika = slika
    student.save()

    context = {'username': request.POST['username']}
    return render(request, 'studserviceapp/slikaUspjesnoDodata.html', context)


def profesorPregled(request, username):
    trenutnaGodina = datetime.datetime.now().year
    trenutniMesec = datetime.datetime.now().month

    if trenutniMesec <= 2 or trenutniMesec >= 10:
        trenutniSemestar = 'neparni'
    else:
        trenutniSemestar = 'parni'

    nalog = Nalog.objects.get(username=username)

    if (nalog.uloga == 'nastavnik'):
        nastavnik = Nastavnik.objects.get(nalog__username=username)
        n: str = nastavnik.ime + " " + nastavnik.prezime
        predmeti = nastavnik.predmet.all()
        predmetiNiz = []

        lista = []

        for predmet in predmeti:
            ime = predmet.naziv
            listaGrupa = []
            grupeNiz: str = ""
            predmetiNiz.append(predmet.naziv)
            termini = Termin.objects.filter(predmet_id=predmet.id, nastavnik=nastavnik).values()

            for t in termini:

                termin = Termin.objects.get(id=t['id'])
                for grupa in termin.grupe.all():

                    if grupa.semestar.vrsta != trenutniSemestar:
                        continue
                    else:
                        listaGrupa.append(grupa.oznaka_grupe)

            lista.append(listaGrupa)

        context = {'predmetiNiz': predmetiNiz, 'lista': lista, 'nastavnik': n, 'username': username,
                   'uloga': nalog.uloga}

        return render(request, 'studserviceapp/profesorPregled.html', context)
    else:
        grupe = Grupa.objects.all()

        context = {'grupe': grupe, 'username': username, 'uloga': nalog.uloga}

        return render(request, 'studserviceapp/profesorPregled.html', context)


def ppStudenti(request, grupa):
    studenti = Student.objects.filter(grupa__oznaka_grupe=grupa)
    listaNaloga = []
    listaStudenata = []
    dict = {}
    for student in studenti:
        s = student.ime + " " + student.prezime
        listaStudenata.append(s)
        listaNaloga.append(student.nalog.username)
        dict[s] = student.nalog.username

    nalog = Nalog.objects.get(username=request.session['username'])
    context = {'studenti': listaStudenata, 'nalozi': listaNaloga, 'dict': dict, 'username': request.session['username'],
               'uloga': nalog.uloga}

    return render(request, 'studserviceapp/listaStudenataPoGrupama.html', context)


def prikazSlikeStudenta(request, username):
    student = Student.objects.get(nalog__username=username)
    img = student.slika.url

    nalog = Nalog.objects.get(username=request.session['username'])
    context = {'slika': img, 'username': request.session['username'], 'uloga': nalog.uloga}

    return render(request, 'studserviceapp/slikaStudenta.html', context)


def maillist(request, username):
    nalog = Nalog.objects.get(username=username)

    if nalog.uloga == 'sekretar' or nalog.uloga == 'administrator':
        admin = True

        predmeti = Predmet.objects.all()

        grupe = []
        trenutniSemestar = get_current_semester()

        if trenutniSemestar == 'neparni':
            if datetime.datetime.now().month <= 2:
                grupeSet = Grupa.objects.filter(semestar__vrsta=trenutniSemestar,
                                                semestar__skolska_godina_pocetak=datetime.datetime.now().year - 1).values()
            else:
                grupeSet = Grupa.objects.filter(semestar__vrsta=trenutniSemestar,
                                                semestar__skolska_godina_pocetak=datetime.datetime.now().year).values()
        else:
            grupeSet = Grupa.objects.filter(semestar__vrsta=trenutniSemestar,
                                            semestar__skolska_godina_pocetak=datetime.datetime.now().year).values()

        for grupaQS in grupeSet:
            grupa = Grupa.objects.get(id=grupaQS['id'])
            grupe.append(grupa)

        finalnalista = ['Svi', 'RN', 'RM', 'RD', 'IT']
        finalnalista.extend(predmeti)
        finalnalista.extend(grupe)

        context = {'admin': admin, 'mail': username + "@raf.rs",
                   'lista': finalnalista, 'username': username, 'uloga': nalog.uloga}

        return render(request, 'studserviceapp/slanjeMejla.html', context)

    else:
        admin = False

        nastavnik = Nastavnik.objects.get(nalog=nalog)
        predmeti = nastavnik.predmet.all()

        trenutniSemestar = get_current_semester()
        if trenutniSemestar == 'neparni':
            if datetime.datetime.now().month <= 2:
                termini = Termin.objects.filter(nastavnik=nastavnik, raspored__semestar__vrsta=trenutniSemestar,
                                                raspored__semestar__skolska_godina_pocetak=datetime.datetime.now().year - 1).values()
            else:
                termini = Termin.objects.filter(nastavnik=nastavnik, raspored__semestar__vrsta=trenutniSemestar,
                                                raspored__semestar__skolska_godina_pocetak=datetime.datetime.now().year).values()
        else:
            termini = Termin.objects.filter(nastavnik=nastavnik, raspored__semestar__vrsta=trenutniSemestar,
                                            raspored__semestar__skolska_godina_pocetak=datetime.datetime.now().year).values()

        listagrupa = []
        for terminQS in termini:
            termin = Termin.objects.get(id=terminQS['id'])
            listagrupa.extend(termin.grupe.all())

        finalnalista = []
        finalnalista.extend(predmeti)
        finalnalista.extend(listagrupa)

        context = {'admin': admin, 'imeprezime': nastavnik.ime + " " + nastavnik.prezime, 'mail': username + "@raf.rs",
                   'lista': finalnalista, 'username': username, 'uloga': nalog.uloga}

        return render(request, 'studserviceapp/slanjeMejla.html', context)

    return render(request)


def sendmail(request):
    sender = request.POST['mejl']
    subject = request.POST['subject']
    msgPlain = request.POST['tekst']
    attachment = request.FILES.get('attachment', False)
    cilj = request.POST['cilj']
    if len(cilj) == 2:
        studenti = []
        studentiSet = Student.objects.filter(smer=cilj).values()

        for studentQS in studentiSet:
            studenti.append(Student.objects.get(id=studentQS['id']))

        for student in studenti:
            if attachment is False:
                create_and_send_message(sender, student.nalog.username + "@raf.rs", subject, msgPlain)
            else:
                create_and_send_message(sender, student.nalog.username + "@raf.rs", subject, msgPlain, attachment)

        return HttpResponse("Mail uspesno poslat!")
    if cilj == 'Svi':
        studenti = Student.objects.all()
        for student in studenti:
            if attachment is False:
                create_and_send_message(sender, student.nalog.username + "@raf.rs", subject, msgPlain)
            else:
                create_and_send_message(sender, student.nalog.username + "@raf.rs", subject, msgPlain, attachment)

        return HttpResponse("Mail uspesno poslat!")
    if cilj[0] in '0123456789':
        trenutniSemestar = get_current_semester()

        if trenutniSemestar == 'neparni':
            if datetime.datetime.now().month <= 2:
                studentiSet = Student.objects.filter(grupa__oznaka_grupe=cilj, grupa__semestar__vrsta=trenutniSemestar,
                                                     grupa__semestar__skolska_godina_pocetak=datetime.datetime.now().year - 1).values()
            else:
                studentiSet = Student.objects.filter(grupa__oznaka_grupe=cilj, grupa__semestar__vrsta=trenutniSemestar,
                                                     grupa__semestar__skolska_godina_pocetak=datetime.datetime.now().year).values()
        else:
            studentiSet = Student.objects.filter(grupa__oznaka_grupe=cilj, grupa__semestar__vrsta=trenutniSemestar,
                                                 grupa__semestar__skolska_godina_pocetak=datetime.datetime.now().year).values()

        studenti = []
        for studentQS in studentiSet:
            student = Student.objects.get(id=studentQS['id'])
            studenti.append(student)
    else:
        nastavnikString = request.POST['ime_prezime'].split(' ')
        nastavnik = Nastavnik.objects.get(ime=nastavnikString[0], prezime=nastavnikString[1])

        predmet = Predmet.objects.get(naziv=request.POST['cilj'])

        trenutniSemestar = get_current_semester()

        if trenutniSemestar == 'neparni':
            if datetime.datetime.now().month <= 2:
                termini = Termin.objects.filter(nastavnik=nastavnik, raspored__semestar__vrsta=trenutniSemestar,
                                                raspored__semestar__skolska_godina_pocetak=datetime.datetime.now().year - 1,
                                                predmet=predmet).values()
            else:
                termini = Termin.objects.filter(nastavnik=nastavnik, raspored__semestar__vrsta=trenutniSemestar,
                                                raspored__semestar__skolska_godina_pocetak=datetime.datetime.now().year,
                                                predmet=predmet).values()
        else:
            termini = Termin.objects.filter(nastavnik=nastavnik, raspored__semestar__vrsta=trenutniSemestar,
                                            raspored__semestar__skolska_godina_pocetak=datetime.datetime.now().year,
                                            predmet=predmet).values()

        studenti = []
        for terminQS in termini:
            termin = Termin.objects.get(id=terminQS['id'])
            grupeTermina = termin.grupe.all()
            for grupa in grupeTermina:
                studentiSet = Student.objects.filter(grupa=grupa).values()
                for studentQS in studentiSet:
                    student = Student.objects.get(id=studentQS['id'])
                    studenti.append(student)
    for student in studenti:
        if attachment is False:
            create_and_send_message(sender, student.nalog.username + "@raf.rs", subject, msgPlain)
        else:
            create_and_send_message(sender, student.nalog.username + "@raf.rs", subject, msgPlain, attachment)

    return HttpResponse("Mail uspesno poslat!")


def rafstudservice(request):
    return render(request, 'studserviceapp/RafStudService.html')


def administratorShow(request, username):
    nalog = Nalog.objects.get(username=username)

    if (nalog.uloga == 'nastavnik' or nalog.uloga == 'sekretar' or nalog.uloga == 'administrator'):
        context = {'username': username}
        return render(request, 'studserviceapp/Administrator.html', context)


def administratorUpload(request, username):
    nalog = Nalog.objects.get(username=username)

    if (nalog.uloga == 'nastavnik' or nalog.uloga == 'sekretar' or nalog.uloga == 'administrator'):
        context = {'username': username}
        return render(request, 'studserviceapp/AdministratorUpload.html', context)


def sekretarShow(request, username):
    nalog = Nalog.objects.get(username=username)

    if (nalog.uloga == 'nastavnik' or nalog.uloga == 'sekretar' or nalog.uloga == 'administrator'):
        context = {'username': username}
        return render(request, 'studserviceapp/Sekretar.html', context)


def nastavnikShow(request, username):
    nalog = Nalog.objects.get(username=username)

    if (nalog.uloga == 'nastavnik'):
        context = {'username': username}
        return render(request, 'studserviceapp/Nastavnik.html', context)


def studentShow(request, username):
    nalog = Nalog.objects.get(username=username)

    if (nalog.uloga == 'student'):
        context = {'username': username}
        return render(request, 'studserviceapp/Student.html', context)


def studentDetalji(request):
    nalog = Nalog.objects.get(username=request.session['username'])
    context = {'username': request.session['username'], 'uloga': nalog.uloga}
    return render(request, 'studserviceapp/FilterStudenta.html', context)


def studentDetaljiObrada(request):
    if request.method == 'POST':
        ime = request.POST['ime']
        prezime = request.POST['prezime']
        smjer = request.POST['smjer']
        godUpisa = request.POST['godUpisa']
        brIndeksa = request.POST['brIndeksa']

        nalog = Nalog.objects.get(username=request.session['username'])

        if ime == "" or prezime == "" or smjer == "" or godUpisa == "" or brIndeksa == "" :
            return HttpResponse("Niste popunili sva polja, vratite se i popunite!")
        else:
            trenutniSemestar = get_current_semester()
            username = ime[0] + prezime + godUpisa[2:4]
            student = Student.objects.get(nalog__username=username)

            # provjera semestra nije neophodna iz dole navedenog razloga ali je tu da bi se
            # u da tom trenutku ispisala jedna izborna grupa zavisno od semstra u kojem se nalazimo
            if trenutniSemestar == 'neparni':
                if datetime.datetime.now().month <= 2:
                    grupa = student.grupa.get(semestar__skolska_godina_pocetak=datetime.datetime.now().year - 1,
                                              semestar__vrsta='neparni')
                else:
                    grupa = student.grupa.get(semestar__skolska_godina_pocetak=datetime.datetime.now().year,
                                              semestar__vrsta='neparni')
            else:
                grupa = student.grupa.get(semestar__skolska_godina_kraj=datetime.datetime.now().year,
                                          semestar__vrsta='parni')

            # staviti get ako ima samo jedan unos, za tu realizaciju bi trebalo da se pamti dodatno u modelu godina
            # kada je izvrsen izbor grupe kako bi svaki put taj izbor bio unikatan
            ige = IzborGrupe.objects.filter(student__nalog__username = username).order_by('-id').values()[:1]
            #ige = reversed(ige1)
            print("Evo me " + str(ige))

            izborGrupe = IzborGrupe.objects.get(id=ige[0]['id'])


            ostvarenoESPB = izborGrupe.ostvarenoESPB
            upisujeESPB = izborGrupe.upisujeESPB
            upisuje_semestar = izborGrupe.upisuje_semestar
            nacin_placanja = izborGrupe.nacin_placanja
            nepolozeni_predmeti = list(izborGrupe.nepolozeni_predmeti.all().values())

            if len(nepolozeni_predmeti) <= 0:
                nepolozeni_predmeti = False
            izabrana_grupa = grupa.oznaka_grupe


            context = {'username': request.session['username'],'uloga': nalog.uloga, 'ost' :  ostvarenoESPB, 'upisuje' : upisujeESPB, 'us' : upisuje_semestar, 'np' : nacin_placanja,
                       'nepolozeni' : nepolozeni_predmeti, 'izg' : izabrana_grupa }


            return render(request, 'studserviceapp/DetaljiStudenta.html', context)


def prikazCelogRasporeda(request):
    timetable = []
    termini = Termin.objects.all()
    if len(termini) < 1:
        # response.write('Grupa studenta nema nijedno dodeljeno predavanje!')
        return HttpResponse('Ne postoji raspored!')
    for terminQS in termini:
        termin = Termin.objects.get(id=terminQS.id)

        # response.write(f'Predmet: {termin.predmet.naziv} ')

        # response.write(f'Tip nastave: {termin.tip_nastave} ')

        # response.write(f'Nastavnik: {termin.nastavnik.ime} {termin.nastavnik.prezime} ')

        # response.write('Grupe: ')
        brojGrupa = len(termin.grupe.all())
        counter = 0

        grupeNaPredmetu = ''
        for grupa in termin.grupe.all():
            if counter < brojGrupa - 1:
                # response.write(f'{grupa.oznaka_grupe}, ')
                grupeNaPredmetu += (grupa.oznaka_grupe + ', ')
            else:
                # response.write(f'{grupa.oznaka_grupe} ')
                grupeNaPredmetu += (grupa.oznaka_grupe)
            counter += 1

        # response.write(f'Dan: {termin.dan} ')

        # response.write(f'Pocetak: {termin.pocetak} ')
        # response.write(f'Zavrsetak: {termin.zavrsetak} ')

        # response.write(f'Oznaka ucionice: {termin.oznaka_ucionice} ')
        # response.write('<br>')

        ime_prezime_nastavnika = termin.nastavnik.ime + " " + termin.nastavnik.prezime
        predmetRed = (termin.predmet.naziv, termin.tip_nastave, ime_prezime_nastavnika,
                      grupeNaPredmetu, termin.dan, termin.pocetak, termin.zavrsetak, termin.oznaka_ucionice)
        timetable.append(predmetRed)

    nalog = Nalog.objects.get(username=request.session['username'])
    context = {'redovi': timetable, 'username': request.session['username'], 'uloga': nalog.uloga}
    return render(request, 'studserviceapp/timetable.html', context)


def unosobavestenja(request):
    nalog = Nalog.objects.get(username=request.session['username'])
    context = {'username': request.session['username'], 'uloga': nalog.uloga}
    return render(request, 'studserviceapp/unosobavestenja.html', context)


def addrasporedpredavanja(request):
    return render(request, 'studserviceapp/dodajraspored.html', {'username': request.session['username']})


def addrasporedobrada(request):
    fajl = request.FILES['raspored']
    import_timetable_from_csv(fajl)
    return render(request, 'studserviceapp/rasporeddodat.html', {'username': request.session['username']})
