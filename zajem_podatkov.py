import orodja
import re
import csv
import requests
import os
import sys


def preveri_podatke(niz):
    '''Preveri, če je bila katera od tekem odpovedana, ekipna, kvalifikacije
    ali ženska in vrne False, drugače vrne True.'''
    if 'cancelled' in niz:
        print('Odpovedana tekma')
        return False
    if 'Team HS' in niz:
        print('Ekipna tekma')
        return False
    if '>QUA</a></td>' in niz:
        print('Kvalifikacije')
        return False
    if 'gender_l">L'in niz:
        print('Ženska tekma')
        return False
    else:
        return True


def id_tekme(niz):
    '''V danem nizu poišče id-je tekem, vrne seznam ujemanj.'''
    id = []
    for ujemanje in re.findall(r'raceid=\d{4}', niz):
            if ujemanje not in id:
                id.append(ujemanje)
    return id


def uredi_id(tekma_id):
    '''Iz prejetega niza izloči niz 'raceid=' in vrne samo id tekme'''
    tekma_id = tekma_id[7:]
    return tekma_id

def tekme_url(seznam):
    '''Iz prejetega seznama pridobi id-je tekem, vsebino strani na danih naslovih shrani v datoteke tekem.'''
    osnovni_url = 'http://data.fis-ski.com/dynamic/results.html'
    parametri = 'sector=JP'
    for stevilka in seznam:
        id = uredi_id(stevilka)
        koncni_url = '{}?{}&{}'.format(osnovni_url, parametri, stevilka)
        datoteka = 'smucarskiskoki/tekme_id/skoki{}.html'.format(id)
        orodja.shrani(koncni_url, datoteka)


def obdelava_skakalnic(datoteka_skakalnice):
    '''Iz prejete datoteke pridobi id-je tekem, jih preveri in vrne seznam id-jev, ki ustrezajo pogojem.'''
    regex_skakalnice = re.compile(
        r'<td height(?P<podatki>.*?)class=.sprite-tab view-fiche',
        flags=re.DOTALL)

    tekma_id = []
    for tekma in re.finditer(regex_skakalnice, orodja.vsebina_datoteke(datoteka_skakalnice)):
        nepreverjeni_podatki = tekma.group('podatki')
        if preveri_podatke(nepreverjeni_podatki) == True:
            preverjeni_podatki = nepreverjeni_podatki
            stevilo = id_tekme(preverjeni_podatki)
            tekma_id.append(stevilo)
    return(tekma_id)


def id_skakalnice(datoteka_sezone):
    '''V dani datoteki poišče in vrne seznam id-jev skakalnic.'''
    with open(datoteka_sezone) as f:
        vsebina = f.read()
        id = []
        for ujemanje in re.findall(r'event_id=\d{5}', vsebina):
            if ujemanje not in id:
                id.append(ujemanje)
        return id


def uredi(seznam):
    rezultat = []
    for element in seznam:
        element = element[9:]
        rezultat.append(element)
    return rezultat[::-1]


def skakalnice_url(seznam):
    '''Dobi sezam id-jev skakalnic in vrne seznam url-jev skakalnic'''
    seznam_skakalnic = []
    osnovni_url = 'http://data.fis-ski.com/dynamic/event-details.html'
    parametri = 'cal_suchsector=JP'
    for skakalnica in seznam:
        koncni_url = '{}?event_id={}&{}'.format(osnovni_url, skakalnica, parametri)
        datoteka = 'smucarskiskoki/skakalnice_id/skoki_{}.html'.format(skakalnica)
        orodja.shrani(koncni_url, datoteka)
        seznam_skakalnic.append(datoteka)
    return seznam_skakalnic


def sezone_url():
    '''Vsebino strani za vsako tekmo posebej shrani v svojo datoteko.'''
    for leto in range(2006, 2017):
        osnovni_url = 'http://data.fis-ski.com/global-links/all-fis-results.html'
        parametri = 'sector_search=JP&gender_search=m&category_search=WC&date_from=begin'
        koncni_url = '{}?seasoncode_search={}&{}'.format(osnovni_url, leto, parametri)
        datoteka_sezone = 'smucarskiskoki/{}.html'.format(leto)
        orodja.shrani(koncni_url, datoteka_sezone)

        '''Sestavimo seznam datotek skakalnic.'''
        skakalnice_seznam = skakalnice_url(uredi(id_skakalnice(datoteka_sezone)))

        for skakalnica in skakalnice_seznam:
            '''Sestavimo seznam id-jev tekem.'''
            seznam_id_tekem = obdelava_skakalnic(skakalnica)

            for tekma_id in seznam_id_tekem:
                tekme_url(tekma_id)

sezone_url()

