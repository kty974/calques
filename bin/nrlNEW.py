############################################################
#
# scritp de recuperation des calques du nrl fichier image et txt
#  pour integration dans le catalogue synopsis
#  https://www.nrlmry.navy.mil/TC.html
#  https://www.nrlmry.navy.mil/archdat/test/kml/TC/
#  pour tous les syustemes actifs sur tousles bassins.
# les repertoires "tmp" de travail et "resultat" sont passes en argument
# Le script est lance par le cron et produit des calqes dans le repertoire resultat 
# qui seront integres au catalogue, pour moment sous le  process NRL
#
######################################################################################
#  le 20/01/2020  Catherine Bientz
#  Modification dans le recherche du bassin "Southern Hem. Season :": "SHEM", en "Southern Hem.": "SHEM"
######################################################################################


import os
import sys
import string
import urllib
import urllib2
import requests
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
from datetime import datetime, timedelta

# if len(sys.argv) < 2:
#     print "Usage: %s <repertoire tmp> <repertoire resultat> " % (sys.argv[0])
#     exit()

# const
#OUTPUT_DIR = "../resultat/"
OUTPUT_DIR = sys.argv[2]
#TMP_DIR = "../tmp/"
TMP_DIR = sys.argv[1]

DOWNLOAD_LINK = "https://www.nrlmry.navy.mil/TC.html"
DOWNLOAD_LINK_DATA = "https://www.nrlmry.navy.mil/archdat/test/kml/TC/"

"""
todo: documentation here
"""

class MyHTMLParser(HTMLParser):

	def __init__(self):
		HTMLParser.__init__(self)
		self.files = []
		self.list_date = []
#		for N in [0]:
		for N in [0, 1]:
#		for N in [0, 1, 2]:
			date_N_days_ago = datetime.now() - timedelta(days=N)
			self.list_date.append(date_N_days_ago.strftime('%Y%m%d'))
		print "date a traiter : %s" % self.list_date

	def handle_starttag(self, tag, attrs):
		if tag == 'a' and len(attrs) == 1 and attrs[0][1].endswith('png'):
			file = attrs[0][1]
			# EVOLUTION => change here to get all the files of the page
			for date_file in self.list_date:
				if file.startswith(date_file):
					self.files.append(file)

	def newFiles(self):
		self.files = []


def generate_tmp_path(filename=""):
	return TMP_DIR + filename

def generate_resultat_path(filename=""):
	return OUTPUT_DIR + filename


def switch_bassin(argument):
    switcher = {
        "Atlantic": "ATL",
        "Central Pacific": "CPAC",
        "East Pacific": "EPAC",
        "Indian Ocean": "IO",
        "Southern Hem.": "SHEM",
        "West Pacific": "WPAC",
    }
    return switcher.get(argument, "Invalid Bassin")



print "\n\n**** debut de traitement lancement nrl.py  : %s" %  datetime.now().strftime('%Y%m%d-%H-%M-%S')

## recuperation de la liste des images deja telechargees dans un set
set_Telecharge = set()
set_historic = set()
if os.path.exists("%s" % (generate_tmp_path("historique.txt"))):
	f = open(generate_tmp_path("historique.txt"), "r")
	tmp_lines = f.readlines()
	f.close()
	for line in tmp_lines:
		set_historic.add(line.strip())


## recuparation de la page html des systeme actifs
if __name__ == '__main__':
	file = "TC.html"
	print os.system("rm %s.old" % (generate_tmp_path(file)))
	
	os.system("mv %s %s.old" % (generate_tmp_path(file), generate_tmp_path(file)))

	request = urllib2.Request(DOWNLOAD_LINK)
	res_txt = urllib2.urlopen(request).read()
	with open(generate_tmp_path(file), 'w') as f: f.write(res_txt)


### recuperation de la liste des systemes actifs et de l'annee en cours
list_actif_storm = []
soup = BeautifulSoup(res_txt, "html.parser")
saison = soup.find('div', class_='allOrActives')
words = str(saison.find_previous('b').get_text()).split(" ")
print words
annee = words[0]
print "annee recuperee :  %s" % (annee)

for maList in soup.find_all('div', class_='listStorms'):
	monB = maList.find_previous('b')
	print monB.get_text()

	maTable = monB.find_next_siblings('table')
	if maTable is not None and len(maTable) > 0:
		for t in maTable[0].find_all('font'):
			print t.get_text()
			print "monB.get_text() :-%s- :-%s- \n" % (monB.get_text(), switch_bassin(monB.get_text()))
			list_actif_storm.append(str(switch_bassin(monB.get_text()) + "." + t.get_text()))
print "systeme actif :   \n  %s" % list_actif_storm
list_actif_storm.sort()
print "systeme actif trie  :   \n  %s" % list_actif_storm

# for b in soup.find_all('b'):
# 	print b.prettify()

###  pour chaque systeme et pour chaque type de produit,
###  recuperation de la liste des images disponibles dans parser.files
#list_type = [ "85rgb.html", "37rgb.html", "85h.html", "37h.html", "85pct.html"]
list_type = [ "85rgb.html"]
print "liste des canaux traites : " % list_type
parser = MyHTMLParser()

for storm in list_actif_storm:
	print "systeme traite :  \n   %s" % storm
	stormBassinName = storm.split(".")[0] + '/' + storm.split(".")[1]
	
	if __name__ == '__main__':

		
		for typeName in list_type:
			parser.newFiles()
			set_files = set()
			set_Atraiter = set()
			DOWNLOAD_LINK_STORM_TYPE = DOWNLOAD_LINK_DATA + annee + '/' + stormBassinName+ '/' + typeName.split(".")[0]
			print " url de telechargement  : %s" % DOWNLOAD_LINK_STORM_TYPE
			print "rm %s.old" % (generate_tmp_path(typeName))
			print os.system("rm %s.old" % (generate_tmp_path(typeName)))
			print "mv %s %s.old" % (generate_tmp_path(typeName), generate_tmp_path(typeName))
			print os.system("mv %s %s.old" % (generate_tmp_path(typeName), generate_tmp_path(typeName)))
			request = urllib2.Request(DOWNLOAD_LINK_STORM_TYPE)
			res_txt = urllib2.urlopen(request).read()
			with open(generate_tmp_path(typeName), 'w') as f: f.write(res_txt)
			parser.feed(res_txt)
		

			set_files = set(parser.files)
			print set_files
			set_Atraiter = set_files - (set_files & set_historic)
			set_Telecharge.update(set_files & set_historic)
			print "images a telecharger  :  %s " % set_Atraiter

			for file in list(set_Atraiter):
				#print "telechargement du fichier : %s" % file
				DOWNLOAD_LINK_STORM_TYPE_DATA = DOWNLOAD_LINK_STORM_TYPE + '/' + file
				file_png = file
				file_txt = file + '.' + "txt"
				### LANCEMENT telechargement proprement dit
				print "telechargement du url : %s" % DOWNLOAD_LINK_STORM_TYPE_DATA
				request = urllib2.Request(DOWNLOAD_LINK_STORM_TYPE_DATA)
				res_txt = urllib2.urlopen(request).read()
				with open(generate_resultat_path(file_png), 'w') as f: f.write(res_txt)
				request = urllib2.Request(DOWNLOAD_LINK_STORM_TYPE_DATA + ".txt")
				res_txt = urllib2.urlopen(request).read()
				with open(generate_resultat_path(file_txt), 'w') as f: f.write(res_txt)
#				print "rename du fichier : %s" % generate_resultat_path(file_txt)
#				os.rename('%s.t' % generate_resultat_path(file_txt), '%s' % generate_resultat_path(file_txt))
#				os.rename('%s.t' % generate_resultat_path(file), '%s' % generate_resultat_path(file))
				set_Telecharge.add(file)
				print "telechargement du url termine : %s" % DOWNLOAD_LINK_STORM_TYPE_DATA


print os.system("rm %s" % (generate_tmp_path("historique.txt")))

f = open(generate_tmp_path("historique.txt"), 'w')

for line in sorted(list(set_Telecharge)):
	f.write("%s\n" % line)
f.close()
print os.system("chmod -R 777 %s" % TMP_DIR)
print os.system("chmod -R 777 %s" % OUTPUT_DIR)
