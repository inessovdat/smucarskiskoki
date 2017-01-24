import re
import orodja
import csv
import requests
import os
import sys

regex_tekme = re.compile(
    #r'div class=.bloc-tab.>'
    #r'.*?<h2 class=.bloc-title.><div class=.blue_bottom_left sprite_corner.></div>OFFICIAL RESULTS</h2>.*?'
    #r'.*?<div class=.padding-content.>.*?'
    #r'<h3>.*?'
    r'<a href=.http://data.fis-ski.com/global-links/statistics/overview-top-ranked-in-all-competitions.html?.*?sector=JP&place=.*?&gender=.*?>(?P<prizorisce>.*?)</a>.*?'
    r'\((?P<drzava_prizorisca>\D{3})\).*?<span class=.right.>(?P<datum>\d{2}\.\d{2}\.\d{4})</span>'
    #r'.*?</h3>.*?'
    #r'.*?<div class=.row.>.*?'
    #r'.*?<div class=.small-12 large-8 columns.>.*?'
    r'.*?<h4>.*?'
    r'\D*?HS(?P<velikost_skakalnice>\d\d\d?).*?</h4>'
    r'.*?</div>.*?'
    r'.*?<div class=.small-12 large-4 columns.>.*?'
    r'<div class=.right text-right.>Race codex : \d{4}'
    ,
    flags=re.DOTALL)


regex_rezultatov = re.compile(
     #r'<tr>.'
     r'<td class=.i\d. align=.right.>&nbsp;(?P<mesto>\d\d?)</td>.<td class=.i\d. align=.right.>&nbsp;\d\d?</td>.*?'
     #r'<td class=.i\d. align=.right.>&nbsp;\d\d</td>.'
     r'<td class=.i\d. align=.right.>&nbsp;(?P<id_tekmovalca>\d{4})</td>.*?'
     r'<td class=.i\d.><a href=.http://data.fis-ski.com/dynamic/athlete-biography.html?.*?competitorid=.*?&amp;type=result.>(?P<tekmovalec>.*?)</a>&nbsp;</td>.*?'
     r'<td class=.i\d. align=.center.>(?P<leto_rojstva>\d{4})&nbsp;</td>.'
     r'<td class=.i\d. align=.center.>(?P<drzava>\D{3})&nbsp;</td>.'
     r'.*?<td class=.i\d. align=.right.>&nbsp;\d{2}\d?.\d</td>.'
     r'<td class=.i\d. align=.right.>&nbsp;\d?\d?\d?.?\d?\d?</td>.'
     r'<.*?td class=.i\d. align=.right.>&nbsp;\d?\d?\d?.?\d?\d?</td>.'
     r'<td class=.i\d. align=.right.>&nbsp.*?;\d?\d?\d?.?\d?\d?</td>.'
     r'<.*?td class=.i\d. align=.right.>&nbsp;(?P<tocke>\d{2}\d?.\d)</td>'
     r'.*?</tr>',
    flags=re.DOTALL)


def pripravi_podatke_tekma(podatki):
    '''Uredi posamezne podatke v prejetem slovarju.'''
    podatki = podatki.groupdict()
    podatki['prizorisce'] = podatki['prizorisce'].strip()
    podatki['drzava_prizorisca'] = podatki['drzava_prizorisca'].strip()
    podatki['datum'] = podatki['datum'].strip()
    podatki['velikost_skakalnice'] = int(podatki['velikost_skakalnice'])
    return podatki


def pripravi_podatke_rezultati(podatki):
    '''Uredi posamezne podatke v prejetem slovarju.'''
    podatki = podatki.groupdict()
    podatki['mesto'] = int(podatki['mesto'])
    podatki['id_tekmovalca'] = int(podatki['id_tekmovalca'])
    podatki['tekmovalec'] = podatki['tekmovalec'].strip()
    podatki['leto_rojstva'] = int(podatki['leto_rojstva'])
    podatki['drzava'] = podatki['drzava'].strip()
    podatki['tocke'] = float(podatki['tocke'])
    return podatki


def izloci_podatke_tekma(imenik):
    '''Poišče ujemanja med regexom tekme in datotekami v imeniku in jih vrne v obliki seznama.'''
    ujemanja = []
    for datoteka in orodja.datoteke(imenik):
         print(datoteka)
         vsebina = orodja.vsebina_datoteke(datoteka)
         for podatki in re.finditer(regex_tekme, vsebina):
             ujemanja.append(pripravi_podatke_tekma(podatki))
             print(ujemanja)
    return ujemanja


def izloci_podatke_rezultati(imenik):
    '''Poišče ujemanja med regexom rezultatov in datotekami v imeniku in jih vrne v obliki seznama.'''
    ujemanja = []
    for datoteka in orodja.datoteke(imenik):
         print(datoteka)
         vsebina = orodja.vsebina_datoteke(datoteka)
         for podatki in re.finditer(regex_rezultatov, vsebina):
             ujemanja.append(pripravi_podatke_rezultati(podatki))
             print(ujemanja)
    return ujemanja


def izloci_tekmovalce(tekma):
    '''Prejete podatke o tekmi razdeli na podatke o tekmovalcu in podatke o uvrstitvi.'''
    podatki_tekmovalec = []
    podatki_uvrstitve = []
    tekmovalci_id = set()
    for tek in tekma:
        if tek['id_tekmovalca'] not in tekmovalci_id:
            tekmovalci_id.add(tek['id_tekmovalca'])
            podatki_tekmovalec.append({'id_tekmovalca':tek['id_tekmovalca'], 'tekmovalec':tek['tekmovalec'], 'leto_rojstva':tek['leto_rojstva'], 'drzava':tek['drzava']})
    for tek in tekma:
        podatki_uvrstitve.append({'mesto':tek['mesto'], 'id_tekmovalca':tek['id_tekmovalca'], 'tocke':tek['tocke']})

    return podatki_tekmovalec, podatki_uvrstitve


tekme = izloci_podatke_tekma('smucarskiskoki/tekme_id/')
rezultati = izloci_podatke_rezultati('smucarskiskoki/tekme_id/')
tekmovalci, uvrstitve = izloci_tekmovalce(rezultati)

orodja.zapisi_tabelo(tekme, ['prizorisce', 'drzava_prizorisca', 'datum', 'velikost_skakalnice'], 'smucarskiskoki/tekme.csv')
orodja.zapisi_tabelo(uvrstitve, ['mesto', 'id_tekmovalca', 'tocke'], 'smucarskiskoki/rezultati.csv')
orodja.zapisi_tabelo(tekmovalci, ['id_tekmovalca', 'tekmovalec', 'leto_rojstva', 'drzava'], 'smucarskiskoki/tekmovalci.csv')