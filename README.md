# HAL.Science MCP Server  

Le serveur de HAL-MCP fournit un ensemble d’outils permettant d’interroger l’API de l’archive ouverte **[HAL](https://hal.science/)**.

Ces outils s’appuient sur les [différentes endpoints de l'API HAL](https://api.archives-ouvertes.fr/docs/ref) afin d’accéder aux métadonnées des dépôts disponibles dans HAL.

À travers l’API de recherche (`search`), le MCP permet d’interroger les informations bibliographiques des publications scientifiques, notamment : le titre ; le résumé ; les auteurs ; les dates de publication ; le type de document et les identifiants associés (DOI, URI, etc.).

Le serveur consulte également d'autres référentiels HAL :`author` : référentiel des auteurs ; `structure` : référentiel des structures de recherche et `anrproject` : référentiel des projets ANR. 

---
# Connecter votre agent au serveur HAL MCP

Le serveur **HAL MCP** est actuellement disponible sur l’environnement de préproduction pour la phase de test :

🔗 https://api-preprod.archives-ouvertes.fr/mcp

---
# Outils disponibles

Nous avons développé une première série de 7 outils permettant d’interroger les métadonnées HAL selon deux niveaux d’analyse :

## 1. Niveau auteur : recherche et analyse des profils scientifiques

Ces outils permettent d’explorer les informations relatives aux auteurs :

- `search_authors` : recherche d’auteurs dans HAL ;
- `search_author_publications` : consultation de leurs publications ;
- `get_author_affiliations` : identification de leurs affiliations. 

---

## 2. Niveau structure : analyse des activités de publication d'une struture

Ces outils permettent d’analyser les structures de recherche référencées dans HAL :

- `search_structures` : recherche des laboratoires, universités et institutions ;
- `get_publication_statistics_by_structure` : statistiques de production scientifique ;
- `count_anr_publications` : analyse des publications financées par l’ANR et mesure du niveau d’accès ouvert (*open access*) ;
- `search_lab_keyword_statistics` : identification des thématiques émergentes via les mots-clés des publications.

---
# Promptothèque

Pour obtenir des réponses fiables, il est recommandé de formuler les questions en lien avec les fonctionnalités couvertes par les outils disponibles. 
Vous trouverez ci-dessous une série d'exemples de requêtes pouvant être utilisées directement ou adaptées selon vos besoins.

## Recherche d'auteurs

- Recherche l'auteur **Yutong Fei** dans HAL.
- Donne-moi l'identifiant HAL de **Yutong Fei**.
- Quelles sont les publications récentes de **Yutong Fei** ?
- Donne les publications de **Yutong Fei** entre 2022 et 2024.
- À quel laboratoire est affilié **Yutong Fei** ?
- Dans quelles structures de recherche **Yutong Fei** a-t-il travaillé ?

## Recherche de structures

- Quel est l'identifiant HAL de **l'Université Claude Bernard Lyon 1** ?
- Recherche l'identifiant HAL de **CCSD**.
- Recherche la structure **CREATIS**.

## Statistiques de publications

- Donne les statistiques de publication (nombre de publications, répartition par type de document) de **l'Université Claude Bernard Lyon 1** entre 2018 et 2023.
- Combien de publications a produites **CREATIS** entre 2020 et 2024 ?
- Quelle est l'évolution du nombre de publications de **LIRIS** entre 2019 et 2024 ?

## Publications financées par l'ANR

- Combien de publications financées par des projets ANR en accès ouvert possède **l'Université Claude Bernard Lyon 1** en 2025 ?
- Combien de publications financées par l'ANR possède **CREATIS** entre 2020 et 2024 ?

## Analyse des thématiques de recherche

- Quels sont les principaux domaines de recherche de **l'Université Claude Bernard Lyon 1** en 2021 ?
- Quels sont les mots-clés les plus fréquents des publications de **CREATIS** en 2023 ?
- Quelles sont les thématiques émergentes de **LIRIS** en 2024 ?
---

# Description détaillée des outils

* `search_authors` : Recherche des auteurs dans le référentiel d’auteurs HAL à partir de leur prénom, nom ou d’une partie du nom.
Retourne les profils des auteurs correspondants avec leur identifiant HAL (`idHAL`) et les informations permettant d’accéder à leurs publications.

| Paramètre | Type | Description |
|---|---|---|
| `query` | obligatoire | Prénom, nom ou fragment du nom de l’auteur à rechercher |
| `rows` | optionnel (défaut : 10) | Nombre maximal d’auteurs retournés |

* `search_author_publications` : Recherche les publications d’un auteur dans HAL sur une période donnée.
Retourne les métadonnées des publications correspondantes : titre ; résumé ; date de publication ; type de document ; DOI lorsqu’il est disponible.

| Paramètre | Type | Description |
|---|---|---|
| `query` | obligatoire | Prénom et nom de l’auteur |
| `start_date` | optionnel | Date de début de la période |
| `end_date` | optionnel | Date de fin de la période |
| `rows` | optionnel (défaut : 50) | Nombre maximal de publications retournées |

* `get_author_affiliations` : Recherche les affiliations d’un auteur enregistré dans HAL en analysant les structures associées à ses publications.
Retourne les structures classées selon leur fréquence d’apparition dans les publications de l’auteur.

| Paramètre | Type | Description |
|---|---|---|
| `id_hal` | obligatoire | Identifiant HAL de l’auteur |

* `search_structures` : Recherche des structures de recherche référencées dans HAL (laboratoires, universités, institutions, etc.) à partir de leur nom ou de leur acronyme.
Retourne les structures correspondantes avec : leur identifiant HAL. 

| Paramètre | Type | Description                      |
|---|---|----------------------------------|
| `nom_structure` | obligatoire | Nom ou acronyme de la structure  |

* `get_publication_statistics_by_structure` : Recherche les publications d’une structure de recherche enregistrée dans HAL sur une période donnée.
Retourne des statistiques concernant : le nombre de publications ; leur type de document ;  leur année de production.

| Paramètre | Type | Description |
|---|---|---|
| `struct_id` | obligatoire | Identifiant HAL de la structure |
| `start_year` | obligatoire | Année de début |
| `end_year` | obligatoire | Année de fin |

* `count_anr_publications` : Recherche les publications financées par des projets ANR pour une structure de recherche sur une période donnée.
Permet également d’analyser leur niveau d’accès ouvert (*open access*).
Retourne : le nombre de publications financées par l’ANR ; les informations associées aux projets ANR ;
la part des publications disponibles en accès ouvert.

| Paramètre     | Type | Description                           |
|---------------|---|---------------------------------------|
| `struct_id`   | obligatoire | Identifiant HAL de la structure       |
| `start_date`  | optionnel | Date de début                         |
| `end_date`    | optionnel | Date de fin                           |
| `open_access` | optionnel | Filtre selon le statut d’accès ouvert |

* `search_lab_keyword_statistics` : Analyse les thématiques émergentes d’une structure de recherche enregistrée dans HAL à partir de la distribution des mots-clés associés aux publications.
Retourne : le nombre total de publications pour une année donnée ; une agrégation des mots-clés classés selon leur fréquence d’apparition.

| Paramètre | Type | Description |
|---|---|---|
| `structure_id` | obligatoire | Identifiant HAL de la structure |
| `year` | obligatoire | Année analysée |

