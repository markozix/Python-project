from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('timetable/<str:username>', views.timetableforuser, name='timetableforuser'),
    path('allsemesters', views.allsemesters, name='allsemesters'),
    path('allsemesters/<int:id>', views.groupsforsemester, name='groupsforsemester'),
    path('addgroup', views.addizbornagrupa, name='addgroup'),
    path('changegroup/<int:id>/<int:id2>', views.changeizbornagrupa, name='changegroup'),
    path('chooseagroup/<str:username>', views.chooseagroup, name='chooseagroup'),
    path('chooseagroupObrada', views.chooseagroupObrada, name='chooseagroupObrada'),
    path('addsemester', views.addsemester, name='addsemester'),
    path('viewgroups', views.viewgroups, name='viewgroups'),
    path('viewgroups/<int:id>', views.viewstudents, name='viewstudents'),
    path('prikazStudentaZaUploadSlike/<str:username>', views.prikazStudentaZaUploadSlike, name='prikazStudentaZaUploadSlike'),
    path('obradaSlike', views.obradaSlike, name = 'obradaSlike'),
    path('profesorPregled/<str:username>', views.profesorPregled, name='profesorPregled'),
    path('profesorPregled/ppStudenti/<str:grupa>', views.ppStudenti, name='ppStudenti'),
    path('profesorPregled/ppStudenti/slika/<str:username>', views.prikazSlikeStudenta, name='prikazSlikeStudenta'),
    path('viewgroups/<int:id>', views.viewstudents, name='viewstudents'),
    path('addklk', views.addkolok, name='addkolok'),
    path('addklksuccess', views.addklksuccess, name='addklksuccess'),
    path('maillist/<str:username>', views.maillist, name='maillist'),
    path('maillistsuccess', views.sendmail, name='sendmail'),
    path('rafstudservice', views.rafstudservice, name='rafstudservice'),
    path('administrator/<str:username>', views.administratorShow, name='administratorShow'),
    path('administratorUpload/<str:username>', views.administratorUpload, name='administratorUpload'),
    path('sekretar/<str:username>', views.sekretarShow, name='sekretarShow'),
    path('nastavnik/<str:username>', views.nastavnikShow, name='nastavnikShow'),
    path('student/<str:username>', views.studentShow, name='studentShow'),
    path('studentDetalji', views.studentDetalji, name='studentDetalji'),
    path('studentDetaljiObrada', views.studentDetaljiObrada, name='studentDetaljiObrada'),
    path('prikazCelogRasporeda', views.prikazCelogRasporeda, name='prikazCelogRasporeda'),
    path('unosObavestenja', views.unosobavestenja, name='unosObavestenja'),
    path('addrRasporedPredavanja', views.addrasporedpredavanja, name='addRasporedPredavanja'),
    path('addRasporedObrada', views.addrasporedobrada, name='addRasporedObrada')
]
