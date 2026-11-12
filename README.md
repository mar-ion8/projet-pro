# Fiche technique pour l'utilisation du processus de photogrammétrie
<img src="assets/img/logos.png" alt="logos"/>

## Table des matières

a la fin lol

## Introduction

### Contexte du besoin de l’entreprise : 

<p align="justify"> 
Modéliser le fonctionnement hydraulique d’un réseau d’assainissement. Pour cela, ouverture des regards, inspection des ouvrages et prise de cotation et vidéo de l’intérieur à l’aide d’une caméra 360° afin de reconstruire l’ouvrage en 3D et réaliser des produits dérivés.
</p>

### Objectifs : 

1. Produire un nuage de points 3D géoréférencé à partir des vidéos via un script python open source.
2. A partir du nuage de points réaliser des produits dérivés : orthophoto, pdf…


## Données d'entrée

Le modèle prend deux données en entrée :
- Vidéo Insta360 Dual FishEye, format .INSV (format brut à haute résolution) ; l'utilisateur doit s'assurer que la vidéo 
englobe bien le moment où la caméra descend dans le regard et permet la visualisation complète et claire du support de cible, et
le moment où la caméra s'arrête dans le fond du regard et permet d'identifier la longueur finale de la descente
- Coordonnées X, Y et Z du centre du regard, format .XLSX (ou .CSV) ; celles-ci seront reprojetées en WGS84 [EPSG:4326] dans
le processus

## Données de sortie

La donnée principale produite par le modèle est le nuage de points géoréférencé, format .LAZ.
L'utilisateur peut également choisir de générer un certain ensemble de données annexes, comme un fichier .PDF permettant
d'obtenir une vue 2D du regard modélisé.

## Méthodologie

### Démarche globale

insérer organigramme global 

### Variables utilisateurs

### Paramètres importants

### Fonctions principales

## Annexes

### Collaborateurs

<p><u>Auteurs :</u></p>

- Marion Bleuse (marion.bleuse8@gmail.com)
- Maxime Gineste (ginestemax@gmail.com)
- Ambrine Ortega (ambrineortega@gmail.com)

<p><u>Encadrants universitaires :</u></p>

- Théo Le Saint (theo.le-saint@univ-rennes2.fr) 
- Laurence Hubert-Moy (laurence.moy@univ-rennes2.fr) 

<p><u>Encadrant Hydracos :</u></p>

- Paul Vrchovsky (paul.vrchovsky@hydracos.fr)

### Sources



### IA

<p align="justify"> 
Pour gérer certaines portions de code, deux modèles d'IA ont principalement été utilisés. Claude (Sonnet 5.5)
en majorité, et Mistral IA. 
Estimer pourcentages de correction et génération
</p>